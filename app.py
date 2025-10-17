from flask import Flask
from flask_cors import CORS
from config import Config
from routes.chat import chat_bp
from routes.trips import trips_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 配置 CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": Config.CORS_ORIGINS,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 注册蓝图
    app.register_blueprint(chat_bp)
    app.register_blueprint(trips_bp)
    
    # 健康检查端点
    @app.route('/health')
    def health():
        return {"status": "healthy", "service": "travel-planner-api"}
    
    # 根路由
    @app.route('/')
    def index():
        return {
            "service": "Travel Planner API",
            "version": "1.0.0",
            "endpoints": {
                "chat": "/api/chat/send",
                "chat_stream": "/api/chat/stream",
                "trips": "/api/trips/<user_id>",
                "trip_detail": "/api/trips/<user_id>/<conversation_id>",
                "search": "/api/trips/<user_id>/search"
            }
        }
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host='0.0.0.0',
        port=Config.FLASK_PORT,
        debug=Config.DEBUG
    )