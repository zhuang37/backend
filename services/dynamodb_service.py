import boto3
from boto3.dynamodb.conditions import Key, Attr
from typing import List, Dict, Optional
from config import Config
import json

class DynamoDBService:
    def __init__(self):
        # 智能选择凭证来源
        if Config.AWS_ACCESS_KEY_ID and Config.AWS_SECRET_ACCESS_KEY:
            print("使用环境变量中的 AWS 凭证")
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=Config.AWS_REGION,
                aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY
            )
        else:
            print("使用 AWS CLI 默认配置")
            self.dynamodb = boto3.resource(
                'dynamodb',
                region_name=Config.AWS_REGION
            )
        
        self.table = self.dynamodb.Table(Config.DYNAMODB_TABLE_NAME)
        print(f"DynamoDB Table: {Config.DYNAMODB_TABLE_NAME}")
    
    def get_user_trips(self, user_id: str, limit: int = 20) -> List[Dict]:
        """
        获取用户的所有行程
        
        Args:
            user_id: 用户ID（session_id）
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 行程列表
        """
        try:
            # 修复：使用 FilterExpression 替代 ScanIndexFilter
            response = self.table.query(
                KeyConditionExpression=Key('userId').eq(user_id),
                FilterExpression=Attr('dataType').eq('itinerary'),  # 修复这里
                Limit=limit,
                ScanIndexForward=False  # 按时间倒序
            )
            
            items = response.get('Items', [])
            
            # 解析 JSON 字符串
            for item in items:
                if 'fullItinerary' in item:
                    item['itinerary'] = json.loads(item['fullItinerary'])
                    del item['fullItinerary']
                if 'tripJson' in item:
                    item['tripData'] = json.loads(item['tripJson'])
                    del item['tripJson']
            
            return items
            
        except Exception as e:
            print(f"Error querying trips: {str(e)}")
            raise
    
    def get_trip_by_id(self, user_id: str, conversation_id: str) -> Optional[Dict]:
        """
        获取特定行程详情
        
        Args:
            user_id: 用户ID
            conversation_id: 对话ID
        
        Returns:
            Dict: 行程详情
        """
        try:
            response = self.table.get_item(
                Key={
                    'userId': user_id,
                    'conversationId': conversation_id
                }
            )
            
            item = response.get('Item')
            
            if item:
                # 解析 JSON
                if 'fullItinerary' in item:
                    item['itinerary'] = json.loads(item['fullItinerary'])
                    del item['fullItinerary']
                if 'tripJson' in item:
                    item['tripData'] = json.loads(item['tripJson'])
                    del item['tripJson']
            
            return item
            
        except Exception as e:
            print(f"Error getting trip: {str(e)}")
            raise
    
    def get_user_parameters(self, user_id: str, limit: int = 10) -> List[Dict]:
        """
        获取用户的初始旅行参数记录
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 参数列表
        """
        try:
            # 修复：使用 FilterExpression
            response = self.table.query(
                KeyConditionExpression=Key('userId').eq(user_id),
                FilterExpression=Attr('dataType').eq('parameters'),  # 修复这里
                Limit=limit,
                ScanIndexForward=False
            )
            
            items = response.get('Items', [])
            
            for item in items:
                if 'tripJson' in item:
                    item['tripData'] = json.loads(item['tripJson'])
                    del item['tripJson']
            
            return items
            
        except Exception as e:
            print(f"Error querying parameters: {str(e)}")
            raise
    
    def search_trips(self, user_id: str, destination: Optional[str] = None, 
                     budget_tier: Optional[str] = None) -> List[Dict]:
        """
        搜索行程
        
        Args:
            user_id: 用户ID
            destination: 目的地（可选）
            budget_tier: 预算等级（可选）
        
        Returns:
            List[Dict]: 匹配的行程列表
        """
        try:
            # 构建过滤表达式
            filter_expression = Attr('dataType').eq('itinerary')
            
            if destination:
                filter_expression = filter_expression & Attr('destination').contains(destination)
            
            if budget_tier:
                filter_expression = filter_expression & Attr('budget_tier').eq(budget_tier)
            
            # 使用 FilterExpression
            response = self.table.query(
                KeyConditionExpression=Key('userId').eq(user_id),
                FilterExpression=filter_expression,  # 这里是对的
                ScanIndexForward=False
            )
            
            items = response.get('Items', [])
            
            for item in items:
                if 'fullItinerary' in item:
                    item['itinerary'] = json.loads(item['fullItinerary'])
                    del item['fullItinerary']
            
            return items
            
        except Exception as e:
            print(f"Error searching trips: {str(e)}")
            raise
    
    def delete_trip(self, user_id: str, conversation_id: str) -> bool:
        """
        删除行程
        
        Args:
            user_id: 用户ID
            conversation_id: 对话ID
        
        Returns:
            bool: 是否删除成功
        """
        try:
            self.table.delete_item(
                Key={
                    'userId': user_id,
                    'conversationId': conversation_id
                }
            )
            return True
            
        except Exception as e:
            print(f"Error deleting trip: {str(e)}")
            raise
    
    def get_all_user_data(self, user_id: str, limit: int = 50) -> List[Dict]:
        """
        获取用户的所有数据（包括参数和行程）
        
        Args:
            user_id: 用户ID
            limit: 返回数量限制
        
        Returns:
            List[Dict]: 所有数据列表
        """
        try:
            # 不使用 FilterExpression，获取所有数据
            response = self.table.query(
                KeyConditionExpression=Key('userId').eq(user_id),
                Limit=limit,
                ScanIndexForward=False
            )
            
            items = response.get('Items', [])
            
            # 解析 JSON
            for item in items:
                if 'fullItinerary' in item:
                    item['itinerary'] = json.loads(item['fullItinerary'])
                    del item['fullItinerary']
                if 'tripJson' in item:
                    item['tripData'] = json.loads(item['tripJson'])
                    del item['tripJson']
            
            return items
            
        except Exception as e:
            print(f"Error getting all user data: {str(e)}")
            raise