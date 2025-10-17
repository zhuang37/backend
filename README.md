# Travel Planner Backend API

一个基于 AWS Bedrock Agent 和 DynamoDB 的 AI 旅行规划助手后端服务。

## 🌟 功能特性

- 🤖 集成 AWS Bedrock Agent 进行智能对话
- 💾 使用 DynamoDB 存储旅行计划和用户数据
- 🔄 支持流式和普通两种对话模式
- 🔍 支持搜索和过滤历史行程
- 🌐 完整的 RESTful API

## 🛠 技术栈

- **Backend**: Flask + Python 3.11
- **AI**: AWS Bedrock Agent
- **Database**: AWS DynamoDB
- **Cloud**: AWS Lambda (可选部署)

## 🚀 快速开始

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

### 4. 运行服务
```bash
python app.py
```

服务将运行在 `http://localhost:5000`

---

## 📚 API 接口文档

### 1. 聊天相关接口

#### 1.1 发送消息（普通模式）

**接口**
```http
POST /api/chat/send
```

**请求体**
```json
{
  "message": "Plan a 3-day trip to Tokyo with my friend, mid budget, love food and culture",
  "sessionId": "optional-session-id"
}
```

**响应示例**
```json
{
  "success": true,
  "message": "Message sent successfully",
  "data": {
    "response": "Here's a detailed 3-day Tokyo itinerary...",
    "sessionId": "349334502243902"
  }
}
```

---

#### 1.2 发送消息（流式模式）

**接口**
```http
POST /api/chat/stream
```

**请求体**
```json
{
  "message": "Plan a 5-day detailed trip to Paris",
  "sessionId": "optional-session-id"
}
```

**响应格式** - Server-Sent Events (SSE) 流
```
data: {"type": "session", "sessionId": "abc-123"}
data: {"type": "content", "text": "Here's"}
data: {"type": "content", "text": " a detailed"}
data: {"type": "done"}
```

---

#### 1.3 清除会话

**接口**
```http
DELETE /api/chat/session/{sessionId}
```

**响应**
```json
{
  "success": true,
  "message": "Session cleared"
}
```

---

### 2. 行程管理接口

#### 2.1 获取用户所有行程

**接口**
```http
GET /api/trips/{userId}?limit=20
```

**参数**
- `userId`: 用户ID（通常就是 sessionId）
- `limit`: 可选，返回数量，默认 20

**响应示例**
```json
{
  "success": true,
  "message": "Found 3 trips",
  "data": [
    {
      "userId": "349334502243902",
      "conversationId": "conv-1760724049104",
      "destination": "Tokyo",
      "start_date": "2024-06-15",
      "days": 3,
      "travelers": 2,
      "budget_tier": "mid",
      "totalCost": 2400,
      "itinerary": {
        "destination": "Tokyo",
        "days": 3,
        "itinerary": [
          {
            "day": 1,
            "activities": [...]
          }
        ]
      }
    }
  ]
}
```

---

#### 2.2 获取特定行程详情

**接口**
```http
GET /api/trips/{userId}/{conversationId}
```

---

#### 2.3 搜索行程

**接口**
```http
GET /api/trips/{userId}/search?destination=Tokyo&budget_tier=mid
```

**Query 参数**
- `destination`: 目的地（可选）
- `budget_tier`: 预算等级 - `low`, `mid`, `high`（可选）

---

#### 2.4 删除行程

**接口**
```http
DELETE /api/trips/{userId}/{conversationId}
```

---

#### 2.5 获取旅行参数记录

**接口**
```http
GET /api/trips/{userId}/parameters?limit=10
```

---

### 3. 其他接口

#### 3.1 健康检查
```http
GET /health
```

#### 3.2 API 信息
```http
GET /
```

---

## ⚠️ 错误响应格式

所有接口的错误响应统一格式：
```json
{
  "success": false,
  "message": "Error description",
  "error": {}
}
```

**HTTP 状态码**
- `200` - 成功
- `400` - 请求参数错误
- `404` - 资源不存在
- `500` - 服务器错误

---

## 📝 许可证

MIT License

## 👤 作者

- GitHub: [@your-username](https://github.com/your-username)