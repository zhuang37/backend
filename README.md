# Travel Planner Backend API

一个基于 AWS Bedrock Agent 和 DynamoDB 的 AI 旅行规划助手后端服务。

## 🌟 功能特性

- 🤖 集成 AWS Bedrock Agent 进行智能对话
- 💾 使用 DynamoDB 存储旅行计划和用户数据
- 🔄 支持流式和普通两种对话模式
- 🔍 支持搜索和过滤历史行程
- 🗺️ 集成 Google Maps API 获取精确地理坐标
- 🌐 完整的 RESTful API

## 🛠 技术栈

- **Backend**: Flask + Python 3.11
- **AI**: AWS Bedrock Agent
- **Database**: AWS DynamoDB
- **Maps**: Google Maps Geocoding API
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

编辑 `.env` 文件，填入你的 AWS 凭证和 Google Maps API Key：
```env
# AWS 配置
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
BEDROCK_AGENT_ID=your-agent-id
BEDROCK_AGENT_ALIAS_ID=your-alias-id
DYNAMODB_TABLE_NAME=TravelPlannerConversations

# Google Maps 配置
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Flask 配置
FLASK_ENV=development
FLASK_PORT=5000
CORS_ORIGINS=http://localhost:3000
```

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

### 3. 地点增强接口 🗺️

这些接口用于获取地点的精确地理坐标，方便前端在地图上标注。

#### 3.1 增强地点列表

**接口**
```http
POST /api/locations/enrich
```

**请求体**
```json
{
  "locations": ["Tokyo Tower", "Senso-ji Temple", "Shibuya Crossing"]
}
```

**响应示例**
```json
{
  "success": true,
  "message": "Processed 3 locations, 0 failed",
  "data": {
    "locations": {
      "Tokyo Tower": {
        "lat": 35.6586,
        "lng": 139.7454,
        "formatted_address": "4 Chome-2-8 Shibakoen, Minato City, Tokyo 105-0011, Japan",
        "place_id": "ChIJCewJkL2LGGAR3Qmk0vCTGkg"
      },
      "Senso-ji Temple": {
        "lat": 35.7147651,
        "lng": 139.7966553,
        "formatted_address": "2 Chome-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan",
        "place_id": "ChIJ8T1GpMGOGGARDYGSgpooDWw"
      },
      "Shibuya Crossing": {
        "lat": 35.6595,
        "lng": 139.7004,
        "formatted_address": "Shibuya City, Tokyo 150-0002, Japan",
        "place_id": "ChIJXSModoL1GGARYGSgpooDWxI"
      }
    },
    "failed_count": 0
  }
}
```

---

#### 3.2 批量增强地点（带上下文）

**接口**
```http
POST /api/locations/enrich-batch
```

**请求体**
```json
{
  "locations": [
    {
      "name": "Tokyo Tower",
      "context": "Tokyo, Japan"
    },
    {
      "name": "Eiffel Tower",
      "context": "Paris, France"
    }
  ]
}
```

**说明**: 通过添加 `context` 字段（城市、国家等），可以提高地点识别的准确性。

**响应格式**: 同 3.1

---

#### 3.3 增强完整行程坐标 ⭐

**接口**
```http
POST /api/locations/enrich-itinerary
```

**使用场景**: 从数据库读取完整行程，自动为所有地点添加精确坐标，方便前端地图展示。

**请求体（方式1 - 传 conversationId）**
```json
{
  "userId": "test-session-321",
  "conversationId": "conv-1760840130674"
}
```

**请求体（方式2 - 直接传 itinerary）**
```json
{
  "itinerary": [
    {
      "day": 1,
      "date": "2024-05-01",
      "theme": "Tokyo Highlights",
      "activities": [
        {
          "time": "09:00",
          "type": "attraction",
          "name": "Senso-ji Temple",
          "address": "2 Chome-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan",
          "duration_minutes": 120,
          "cost_estimate_usd": 0
        }
      ]
    }
  ]
}
```

**响应示例**
```json
{
  "success": true,
  "message": "Enriched 9/9 locations",
  "data": {
    "itinerary_with_coords": [
      {
        "day": 1,
        "date": "2024-05-01",
        "theme": "Tokyo Highlights",
        "activities": [
          {
            "time": "09:00",
            "type": "attraction",
            "name": "Senso-ji Temple",
            "address": "2 Chome-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan",
            "duration_minutes": 120,
            "cost_estimate_usd": 0,
            "coordinates": {
              "lat": 35.7147651,
              "lng": 139.7966553,
              "formatted_address": "2 Chome-3-1 Asakusa, Taito City, Tokyo 111-0032, Japan",
              "place_id": "ChIJ8T1GpMGOGGARDYGSgpooDWw"
            }
          },
          {
            "time": "12:00",
            "type": "restaurant",
            "name": "Sometaro",
            "address": "2 Chome-2-2 Nishi-Asakusa, Taito City, Tokyo 111-0035, Japan",
            "duration_minutes": 90,
            "cost_estimate_usd": 40,
            "coordinates": {
              "lat": 35.7214891,
              "lng": 139.7883256,
              "formatted_address": "2 Chome-2-2 Nishi-Asakusa, Taito City, Tokyo 111-0035, Japan",
              "place_id": "ChIJX8T1GpMOGGARpooDWwDYGSg"
            }
          }
        ]
      }
    ],
    "summary": {
      "total_locations": 9,
      "enriched": 9,
      "failed": 0
    },
    "failed_locations": []
  }
}
```

**特性**:
- ✅ 保留原始 activity 的所有字段
- ✅ 为每个 activity 添加 `coordinates` 字段
- ✅ 自动处理失败的地点（coordinates 为 null）
- ✅ 返回处理统计信息（成功/失败数量）
- ✅ 支持从 DynamoDB 自动读取或直接传入数据

---

### 4. 其他接口

#### 4.1 健康检查
```http
GET /health
```

#### 4.2 API 信息
```http
GET /
```

---

## 🌍 Google Maps API 配置

### 获取 API Key

1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建或选择项目
3. 启用 **Geocoding API**
4. 创建 API 密钥
5. 添加到 `.env` 文件：`GOOGLE_MAPS_API_KEY=your-key`

### 免费额度

- 每月 **$200** 免费额度
- Geocoding API: **$5/1000 次请求**
- 相当于每月免费 **40,000 次请求**

### 成本优化建议

- 使用缓存减少重复查询
- 将常用地点坐标存储到数据库
- 监控 API 使用量

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
