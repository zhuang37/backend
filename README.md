# Travel Planner Backend API

一个基于 AWS Bedrock Agent 和 DynamoDB 的 AI 旅行规划助手后端服务。

## 功能特性

- 🤖 集成 AWS Bedrock Agent 进行智能对话
- 💾 使用 DynamoDB 存储旅行计划和用户数据
- 🔄 支持流式和普通两种对话模式
- 🔍 支持搜索和过滤历史行程
- 🌐 完整的 RESTful API

## 技术栈

- **Backend**: Flask + Python 3.11
- **AI**: AWS Bedrock Agent
- **Database**: AWS DynamoDB
- **Cloud**: AWS Lambda (可选部署)

## 快速开始

### 1. 克隆项目
```bash
git clone https://github.com/your-username/travel-planner-backend.git
cd travel-planner-backend
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填入你的配置：
```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 AWS 凭证和配置。

### 4. 配置 AWS 凭证


1. 聊天相关接口
1.1 发送消息（普通模式）
最常用的接口 - 用户发送旅行需求，Agent 返回完整的回复。
httpPOST /api/chat/send
请求体：
json{
  "message": "Plan a 3-day trip to Tokyo with my friend, mid budget, love food and culture",
  "sessionId": "optional-session-id"  // 可选，不传则自动生成
}
响应示例：
json{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "response": "Here's a detailed 3-day Tokyo itinerary...",
    "sessionId": "349334502243902"
  }
}
前端使用场景：

聊天对话框发送消息
等待完整回复后一次性显示


1.2 发送消息（流式模式）
适合长回复 - Agent 的回复会逐字逐句返回，用户体验更好。
httpPOST /api/chat/stream
请求体：
json{
  "message": "Plan a 5-day detailed trip to Paris",
  "sessionId": "optional-session-id"
}
```

**响应格式：** Server-Sent Events (SSE) 流
```
data: {"type": "session", "sessionId": "abc-123"}

data: {"type": "content", "text": "Here's"}

data: {"type": "content", "text": " a detailed"}

data: {"type": "content", "text": " itinerary..."}

data: {"type": "done"}
前端使用场景：

打字机效果的聊天
长文本回复时实时显示


1.3 清除会话（可选）
httpDELETE /api/chat/session/{sessionId}
响应：
json{
  "success": true,
  "message": "Session cleared"
}
前端使用场景：

用户点击"新建对话"
清理本地缓存


2. 行程管理接口
2.1 获取用户所有行程
最常用的查询接口 - 获取用户历史保存的所有旅行计划。
httpGET /api/trips/{userId}?limit=20
参数：

userId: 用户ID（通常就是 sessionId）
limit: 可选，返回数量，默认 20

响应示例：
json{
  "success": true,
  "message": "Found 3 trips",
  "data": [
    {
      "userId": "349334502243902",
      "conversationId": "conv-1760724049104",
      "timestamp": 1760724049104,
      "dataType": "itinerary",
      "destination": "Tokyo",
      "start_date": "2024-06-15",
      "days": 3,
      "travelers": 2,
      "budget_tier": "mid",
      "totalCost": 2400,
      "itinerary": {
        "destination": "Tokyo",
        "start_date": "2024-06-15",
        "days": 3,
        "total_estimated_cost": 2400,
        "itinerary": [
          {
            "day": 1,
            "date": "2024-06-15",
            "theme": "Traditional Tokyo & Culinary Introduction",
            "activities": [
              {
                "time": "09:00",
                "type": "attraction",
                "name": "Senso-ji Temple",
                "description": "Historic Buddhist temple...",
                "address": "2 Chome-3-1 Asakusa, Taito City...",
                "duration_minutes": 120,
                "cost_estimate_usd": 0
              }
              // ... more activities
            ]
          },
          {
            "day": 2,
            // ...
          },
          {
            "day": 3,
            // ...
          }
        ]
      }
    }
    // ... more trips
  ]
}
前端使用场景：

"我的行程"列表页
显示所有历史旅行计划
按时间倒序排列


2.2 获取特定行程详情
httpGET /api/trips/{userId}/{conversationId}
响应示例：
json{
  "success": true,
  "message": "Trip found",
  "data": {
    "conversationId": "conv-1760724049104",
    "destination": "Tokyo",
    "start_date": "2024-06-15",
    "days": 3,
    "travelers": 2,
    "budget_tier": "mid",
    "totalCost": 2400,
    "itinerary": {
      // 完整的行程 JSON
    }
  }
}
前端使用场景：

点击列表中某个行程查看详情
显示完整的日程安排


2.3 搜索行程
httpGET /api/trips/{userId}/search?destination=Tokyo&budget_tier=mid
Query 参数：

destination: 目的地（可选）
budget_tier: 预算等级 - low, mid, high（可选）

响应示例：
json{
  "success": true,
  "message": "Found 2 matching trips",
  "data": [
    // 匹配的行程列表
  ]
}
前端使用场景：

搜索框：输入目的地搜索
筛选器：按预算筛选


2.4 删除行程
httpDELETE /api/trips/{userId}/{conversationId}
响应：
json{
  "success": true,
  "message": "Trip deleted successfully"
}
前端使用场景：

行程卡片的删除按钮
确认删除对话框


2.5 获取旅行参数记录
查看用户的原始需求 - 在调用 planner agent 之前保存的初始参数。
httpGET /api/trips/{userId}/parameters?limit=10
响应示例：
json{
  "success": true,
  "message": "Found 5 parameter records",
  "data": [
    {
      "conversationId": "conv-1760724049000",
      "timestamp": 1760724049000,
      "dataType": "parameters",
      "tripData": {
        "destination": "Tokyo",
        "start_date": "2024-06-15",
        "days": 3,
        "travelers": 2,
        "budget_tier": "mid",
        "preferences": ["food", "culture"]
      }
    }
  ]
}
前端使用场景：

调试/分析用
查看用户最初输入的需求


3. 其他接口
3.1 健康检查
httpGET /health
响应：
json{
  "status": "healthy",
  "service": "travel-planner-api"
}
3.2 API 信息
httpGET /
响应：
json{
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

错误响应格式
所有接口的错误响应统一格式：
json{
  "success": false,
  "message": "Error description",
  "error": {
    // 可选的详细错误信息
  }
}
常见 HTTP 状态码：

200 - 成功
400 - 请求参数错误
404 - 资源不存在
500 - 服务器错误

