# services/google_maps_service.py
import googlemaps
from typing import Optional, Dict
from config import Config

class GoogleMapsService:
    def __init__(self):
        """初始化 Google Maps 客户端"""
        self.client = googlemaps.Client(key=Config.GOOGLE_MAPS_API_KEY)
    
    def geocode_location(self, location_name: str) -> Optional[Dict]:
        """
        将地点名称转换为精确的地理信息
        
        Args:
            location_name: 地点名称（如 "东京塔"）
        
        Returns:
            {
                "lat": 35.6586,
                "lng": 139.7454,
                "formatted_address": "完整地址",
                "place_id": "Google Place ID"  // 可选
            }
            如果找不到则返回 None
        """
        try:
            # 调用 Geocoding API
            results = self.client.geocode(location_name)
            
            if not results:
                print(f"No results found for: {location_name}")
                return None
            
            # 取第一个结果（通常是最匹配的）
            first_result = results[0]
            geometry = first_result['geometry']['location']
            
            return {
                "lat": geometry['lat'],
                "lng": geometry['lng'],
                "formatted_address": first_result.get('formatted_address', ''),
                "place_id": first_result.get('place_id', '')
            }
            
        except Exception as e:
            print(f"Error geocoding '{location_name}': {str(e)}")
            return None
    
    def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        获取地点的详细信息（可选功能，如果需要更多信息）
        
        Args:
            place_id: Google Place ID
        
        Returns:
            详细信息字典
        """
        try:
            result = self.client.place(place_id)
            
            if result['status'] == 'OK':
                place = result['result']
                
                return {
                    "name": place.get('name', ''),
                    "rating": place.get('rating'),
                    "types": place.get('types', []),
                    "photos": place.get('photos', []),
                    "opening_hours": place.get('opening_hours', {})
                }
            
            return None
            
        except Exception as e:
            print(f"Error getting place details: {str(e)}")
            return None
    
    def batch_geocode(self, locations: list) -> Dict[str, Optional[Dict]]:
        """
        批量处理多个地点
        
        Args:
            locations: 地点名称列表
        
        Returns:
            {地点名: 地理信息} 的字典
        """
        results = {}
        
        for location in locations:
            results[location] = self.geocode_location(location)
        
        return results