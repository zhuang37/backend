from flask import Blueprint, request, Response, stream_with_context
from services.bedrock_service import BedrockService
from utils.response import success_response, error_response
import uuid
import json

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
bedrock_service = BedrockService()

@chat_bp.route('/send', methods=['POST'])
def send_message():
    """
    发送消息给 Agent
    
    请求体:
    {
        "message": "Plan a 3-day trip to Tokyo",
        "sessionId": "optional-session-id"  # 可选，不传则自动生成
    }
    
    响应:
    {
        "success": true,
        "message": "Success",
        "data": {
            "response": "Agent的回复内容",
            "sessionId": "session-uuid"
        }
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return error_response("Missing 'message' in request body", 400)
        
        user_message = data['message']
        session_id = data.get('sessionId') or str(uuid.uuid4())
        
        # 调用 Bedrock Agent
        result = bedrock_service.invoke_agent(user_message, session_id)
        
        return success_response(result, "Message sent successfully")
        
    except Exception as e:
        return error_response(f"Error processing message: {str(e)}", 500)


@chat_bp.route('/stream', methods=['POST'])
def stream_message():
    """
    流式发送消息（适合长响应）
    
    请求体:
    {
        "message": "Plan a 3-day trip to Tokyo",
        "sessionId": "optional-session-id"
    }
    
    响应: Server-Sent Events (SSE) 流
    """
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return error_response("Missing 'message' in request body", 400)
        
        user_message = data['message']
        session_id = data.get('sessionId') or str(uuid.uuid4())
        
        def generate():
            try:
                # 先发送 session_id
                yield f"data: {json.dumps({'type': 'session', 'sessionId': session_id})}\n\n"
                
                # 流式返回内容
                for chunk in bedrock_service.invoke_agent_stream(user_message, session_id):
                    yield f"data: {json.dumps({'type': 'content', 'text': chunk})}\n\n"
                
                # 发送完成信号
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
                
            except Exception as e:
                yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
        
        return Response(
            stream_with_context(generate()),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no'
            }
        )
        
    except Exception as e:
        return error_response(f"Error in streaming: {str(e)}", 500)


@chat_bp.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    """
    清除会话（可选功能，如果需要的话）
    
    响应:
    {
        "success": true,
        "message": "Session cleared"
    }
    """
    # 注意：Bedrock Agent 会自动管理会话，通常不需要手动清除
    # 这个端点主要是为了前端清理本地状态
    return success_response(None, "Session cleared")