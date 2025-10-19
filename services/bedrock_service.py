import boto3
import json
from config import Config
from botocore.config import Config as BotoConfig 

#  这段代码定义了一个叫 BedrockService 的类，用来初始化 AWS 客户端，以便后续向 Bedrock 发送请求。
class BedrockService:
    def __init__(self):
        boto_config = BotoConfig(
        read_timeout=300,  
        connect_timeout=60
        )
        self.client = boto3.client(
            'bedrock-agent-runtime',
            region_name=Config.AWS_REGION,
            aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
            config=boto_config
        )
        self.agent_id = Config.BEDROCK_AGENT_ID
        self.agent_alias_id = Config.BEDROCK_AGENT_ALIAS_ID
    
    def invoke_agent(self, user_message: str, session_id: str, enable_trace: bool = False):
        """
        调用 Bedrock Agent
        
        Args:
            user_message: 用户消息
            session_id: 会话 ID
            enable_trace: 是否启用追踪（调试用）
        
        Returns:
            dict: {
                "response": str,  # Agent 的回复
                "session_id": str,
                "trace": list  # 如果 enable_trace=True
            }
        """
        try:
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,
                inputText=user_message,
                enableTrace=enable_trace
            )
            
            # 解析流式响应
            event_stream = response['completion']
            agent_response = ""
            trace_data = []
            
            for event in event_stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        agent_response += chunk['bytes'].decode('utf-8')
                
                if enable_trace and 'trace' in event:
                    trace_data.append(event['trace'])
            
            result = {
                "response": agent_response,
                "session_id": session_id
            }
            
            if enable_trace:
                result["trace"] = trace_data
            
            return result
            
        except Exception as e:
            print(f"Error invoking Bedrock Agent: {str(e)}")
            raise
    
    def invoke_agent_stream(self, user_message: str, session_id: str):
        """
        流式调用 Bedrock Agent（用于实时响应）
        
        Yields:
            str: 逐步返回的文本片段
        """
        try:
            response = self.client.invoke_agent(
                agentId=self.agent_id,
                agentAliasId=self.agent_alias_id,
                sessionId=session_id,
                inputText=user_message,
                enableTrace=False
            )
            
            event_stream = response['completion']
            
            for event in event_stream:
                if 'chunk' in event:
                    chunk = event['chunk']
                    if 'bytes' in chunk:
                        yield chunk['bytes'].decode('utf-8')
                        
        except Exception as e:
            print(f"Error in streaming: {str(e)}")
            raise