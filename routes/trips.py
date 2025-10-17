from flask import Blueprint, request
from services.dynamodb_service import DynamoDBService
from utils.response import success_response, error_response

trips_bp = Blueprint('trips', __name__, url_prefix='/api/trips')
dynamodb_service = DynamoDBService()

@trips_bp.route('/<user_id>', methods=['GET'])
def get_trips(user_id):
    """
    获取用户的所有行程
    
    Query 参数:
    - limit: 返回数量，默认 20
    
    响应:
    {
        "success": true,
        "data": [
            {
                "conversationId": "conv-xxx",
                "destination": "Tokyo",
                "start_date": "2024-06-15",
                "days": 3,
                "itinerary": {...}
            }
        ]
    }
    """
    try:
        limit = request.args.get('limit', 20, type=int)
        trips = dynamodb_service.get_user_trips(user_id, limit)
        return success_response(trips, f"Found {len(trips)} trips")
        
    except Exception as e:
        return error_response(f"Error fetching trips: {str(e)}", 500)


@trips_bp.route('/<user_id>/<conversation_id>', methods=['GET'])
def get_trip(user_id, conversation_id):
    """
    获取特定行程详情
    
    响应:
    {
        "success": true,
        "data": {
            "conversationId": "conv-xxx",
            "destination": "Tokyo",
            "itinerary": {...}
        }
    }
    """
    try:
        trip = dynamodb_service.get_trip_by_id(user_id, conversation_id)
        
        if not trip:
            return error_response("Trip not found", 404)
        
        return success_response(trip, "Trip found")
        
    except Exception as e:
        return error_response(f"Error fetching trip: {str(e)}", 500)


@trips_bp.route('/<user_id>/search', methods=['GET'])
def search_trips(user_id):
    """
    搜索行程
    
    Query 参数:
    - destination: 目的地（可选）
    - budget_tier: 预算等级（可选）
    
    响应:
    {
        "success": true,
        "data": [...]
    }
    """
    try:
        destination = request.args.get('destination')
        budget_tier = request.args.get('budget_tier')
        
        trips = dynamodb_service.search_trips(user_id, destination, budget_tier)
        return success_response(trips, f"Found {len(trips)} matching trips")
        
    except Exception as e:
        return error_response(f"Error searching trips: {str(e)}", 500)


@trips_bp.route('/<user_id>/<conversation_id>', methods=['DELETE'])
def delete_trip(user_id, conversation_id):
    """
    删除行程
    
    响应:
    {
        "success": true,
        "message": "Trip deleted"
    }
    """
    try:
        success = dynamodb_service.delete_trip(user_id, conversation_id)
        
        if success:
            return success_response(None, "Trip deleted successfully")
        else:
            return error_response("Failed to delete trip", 500)
        
    except Exception as e:
        return error_response(f"Error deleting trip: {str(e)}", 500)


@trips_bp.route('/<user_id>/parameters', methods=['GET'])
def get_parameters(user_id):
    """
    获取用户的旅行参数记录
    
    响应:
    {
        "success": true,
        "data": [
            {
                "conversationId": "conv-xxx",
                "tripData": {
                    "destination": "Tokyo",
                    "days": 3,
                    ...
                }
            }
        ]
    }
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        parameters = dynamodb_service.get_user_parameters(user_id, limit)
        return success_response(parameters, f"Found {len(parameters)} parameter records")
        
    except Exception as e:
        return error_response(f"Error fetching parameters: {str(e)}", 500)

@trips_bp.route('/<user_id>/all', methods=['GET'])
def get_all_data(user_id):
    """
    获取用户的所有数据（调试用）
    
    响应:
    {
        "success": true,
        "data": [
            // 所有记录，包括 parameters 和 itinerary
        ]
    }
    """
    try:
        limit = request.args.get('limit', 50, type=int)
        all_data = dynamodb_service.get_all_user_data(user_id, limit)
        return success_response(all_data, f"Found {len(all_data)} records")
        
    except Exception as e:
        return error_response(f"Error fetching data: {str(e)}", 500)