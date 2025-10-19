# routes/locations.py
from flask import Blueprint, request
from services.google_maps_service import GoogleMapsService
from utils.response import success_response, error_response

locations_bp = Blueprint('locations', __name__, url_prefix='/api/locations')
maps_service = GoogleMapsService()

@locations_bp.route('/enrich', methods=['POST'])
def enrich_locations():
    """
    增强地点信息 - 获取精确的经纬度
    
    请求体:
    {
        "locations": ["东京塔", "浅草寺", "秋叶原"]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return error_response("Missing 'locations' in request body", 400)
        
        locations = data['locations']
        
        if not isinstance(locations, list) or len(locations) == 0:
            return error_response("'locations' must be a non-empty array", 400)
        
        enriched_data = {}
        failed_locations = []
        
        for location_name in locations:
            try:
                result = maps_service.geocode_location(location_name)
                
                if result:
                    enriched_data[location_name] = result
                else:
                    failed_locations.append(location_name)
                    enriched_data[location_name] = None
                    
            except Exception as e:
                print(f"Error processing location '{location_name}': {str(e)}")
                failed_locations.append(location_name)
                enriched_data[location_name] = None
        
        response_data = {
            "locations": enriched_data,
            "failed_count": len(failed_locations)
        }
        
        if failed_locations:
            response_data["failed_locations"] = failed_locations
        
        return success_response(
            response_data, 
            f"Processed {len(locations)} locations, {len(failed_locations)} failed"
        )
        
    except Exception as e:
        return error_response(f"Error enriching locations: {str(e)}", 500)


@locations_bp.route('/enrich-batch', methods=['POST'])
def enrich_locations_batch():
    """
    批量增强地点信息（带上下文，提高准确性）
    
    请求体:
    {
        "locations": [
            {
                "name": "东京塔",
                "context": "Tokyo, Japan"
            }
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'locations' not in data:
            return error_response("Missing 'locations' in request body", 400)
        
        locations = data['locations']
        enriched_data = {}
        failed_locations = []
        
        for location in locations:
            location_name = location.get('name') if isinstance(location, dict) else location
            context = location.get('context', '') if isinstance(location, dict) else ''
            
            query = f"{location_name}, {context}" if context else location_name
            
            try:
                result = maps_service.geocode_location(query)
                
                if result:
                    enriched_data[location_name] = result
                else:
                    failed_locations.append(location_name)
                    enriched_data[location_name] = None
                    
            except Exception as e:
                print(f"Error processing location '{location_name}': {str(e)}")
                failed_locations.append(location_name)
                enriched_data[location_name] = None
        
        response_data = {
            "locations": enriched_data,
            "failed_count": len(failed_locations)
        }
        
        if failed_locations:
            response_data["failed_locations"] = failed_locations
        
        return success_response(response_data, "Batch enrichment completed")
        
    except Exception as e:
        return error_response(f"Error in batch enrichment: {str(e)}", 500)


@locations_bp.route('/enrich-itinerary', methods=['POST'])
def enrich_itinerary():
    """
    从完整行程中提取并增强所有地点信息
    
    请求体:
    {
        "conversationId": "conv-xxx",
        "userId": "user-xxx",
        "itinerary": {...}  // 可选
    }
    """
    try:
        from services.dynamodb_service import DynamoDBService
        import json
        
        data = request.get_json()
        itinerary = data.get('itinerary')
        
        # 如果没有传 itinerary，从 DynamoDB 读取
        if not itinerary:
            user_id = data.get('userId')
            conversation_id = data.get('conversationId')
            
            if not user_id or not conversation_id:
                return error_response(
                    "Missing 'itinerary' or ('userId' and 'conversationId')", 
                    400
                )
            
            dynamodb_service = DynamoDBService()
            trip = dynamodb_service.get_trip_by_id(user_id, conversation_id)
            
            if not trip:
                return error_response("Trip not found", 404)
            
            # 如果是 parameters 类型，尝试找对应的 itinerary
            if trip.get('dataType') == 'parameters':
                all_trips = dynamodb_service.get_user_trips(user_id, limit=50)
                itinerary_trip = None
                
                for t in all_trips:
                    if t.get('dataType') == 'itinerary':
                        itinerary_trip = t
                        break
                
                if itinerary_trip:
                    trip = itinerary_trip
                else:
                    return error_response("No complete itinerary found for this user", 404)
            
            # 尝试从不同位置获取 itinerary（必须是数组格式）
            itinerary = trip.get('itinerary')
            
            # 如果在外层有 itinerary，检查是否是嵌套的
            if itinerary and isinstance(itinerary, dict) and 'itinerary' in itinerary:
                itinerary = itinerary['itinerary']
            
            # 验证 itinerary 是数组格式
            if not itinerary or not isinstance(itinerary, list):
                return error_response("No valid itinerary array found in trip data", 404)
        
        # 提取并增强所有地点
        enriched_itinerary = []
        total_locations = 0
        enriched_count = 0
        failed_locations = []
        
        for day_plan in itinerary:
            day_data = {
                "day": day_plan.get('day'),
                "date": day_plan.get('date'),
                "theme": day_plan.get('theme'),
                "activities": []
            }
            
            for activity in day_plan.get('activities', []):
                total_locations += 1
                
                name = activity.get('name', '')
                address = activity.get('address', '')
                query = f"{name}, {address}" if address else name
                
                try:
                    coords = maps_service.geocode_location(query)
                    
                    if coords:
                        enriched_count += 1
                    else:
                        failed_locations.append(name)
                    
                    activity_with_coords = activity.copy()
                    activity_with_coords['coordinates'] = coords
                    
                    day_data['activities'].append(activity_with_coords)
                    
                except Exception as e:
                    print(f"Error processing '{name}': {str(e)}")
                    failed_locations.append(name)
                    activity_with_coords = activity.copy()
                    activity_with_coords['coordinates'] = None
                    day_data['activities'].append(activity_with_coords)
            
            enriched_itinerary.append(day_data)
        
        response_data = {
            "itinerary_with_coords": enriched_itinerary,
            "summary": {
                "total_locations": total_locations,
                "enriched": enriched_count,
                "failed": len(failed_locations)
            }
        }
        
        if failed_locations:
            response_data["failed_locations"] = failed_locations
        
        return success_response(
            response_data,
            f"Enriched {enriched_count}/{total_locations} locations"
        )
        
    except Exception as e:
        return error_response(f"Error enriching itinerary: {str(e)}", 500)