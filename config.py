import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # AWS 配置
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    
    # Bedrock Agent 配置
    BEDROCK_AGENT_ID = os.getenv('BEDROCK_AGENT_ID')
    BEDROCK_AGENT_ALIAS_ID = os.getenv('BEDROCK_AGENT_ALIAS_ID')
    
    # DynamoDB 配置
    DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'TravelPlannerConversations')
    
    # Flask 配置
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    DEBUG = FLASK_ENV == 'development'
    
    # CORS 配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')