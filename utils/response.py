from flask import jsonify
from typing import Any, Optional

def success_response(data: Any = None, message: str = "Success", code: int = 200):
    """统一成功响应格式"""
    response = {
        "success": True,
        "message": message,
        "data": data
    }
    return jsonify(response), code

def error_response(message: str, code: int = 400, error_details: Optional[dict] = None):
    """统一错误响应格式"""
    response = {
        "success": False,
        "message": message,
        "error": error_details
    }
    return jsonify(response), code