# Project: CARGO - API 密钥管理文档

## 概述

本文档定义了 Project: CARGO 游戏中所有外部 API 的密钥管理规范。出于安全考虑，所有 API 密钥应通过环境变量或专用密钥管理服务注入，**严禁硬编码**在源码中。

---

## 环境变量配置

### 1. 大语言模型 API

#### OpenAI API
```bash
# 必需
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选 - 自定义 Base URL（用于代理或第三方兼容服务）
OPENAI_BASE_URL=https://api.openai.com/v1

# 可选 - 组织 ID
OPENAI_ORG_ID=org-xxxxxxxx
```

#### DeepSeek API（推荐备选）
```bash
# 必需
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# 可选 - 自定义 Base URL
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
```

#### Anthropic Claude API（可选）
```bash
# 可选
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. 向量数据库（RAG 检索）

#### Pinecone
```bash
PINECONE_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=cargo-technical-manual
```

#### Qdrant（开源备选）
```bash
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=optional-api-key
```

### 3. 监控与日志

#### LangSmith（LLM 调用追踪）
```bash
LANGCHAIN_API_KEY=ls-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
LANGCHAIN_PROJECT=cargo-production
LANGCHAIN_TRACING_V2=true
```

### 4. 云服务（可选）

#### AWS（如使用 AWS 托管）
```bash
AWS_ACCESS_KEY_ID=AKIAxxxxxxxxxxxxxxxx
AWS_SECRET_ACCESS_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AWS_REGION=us-east-1
```

---

## 配置文件模板

### `.env.example`（提交到版本控制）

```bash
# ============================================
# Project: CARGO - API Keys Configuration
# ============================================
# 复制此文件为 .env 并填入实际密钥值
# .env 文件应添加到 .gitignore，切勿提交！
# ============================================

# ------------------
# LLM Providers (至少配置一个)
# ------------------
OPENAI_API_KEY=
# OPENAI_BASE_URL=https://api.openai.com/v1

DEEPSEEK_API_KEY=
# DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# ANTHROPIC_API_KEY=

# ------------------
# Vector Database (RAG)
# ------------------
# Pinecone
PINECONE_API_KEY=
PINECONE_ENVIRONMENT=us-east-1
PINECONE_INDEX_NAME=cargo-technical-manual

# Qdrant (如果使用本地部署)
# QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=

# ------------------
# Monitoring & Tracing
# ------------------
# LANGCHAIN_API_KEY=
# LANGCHAIN_PROJECT=cargo-development
# LANGCHAIN_TRACING_V2=false

# ------------------
# Application Settings
# ------------------
# 游戏会话密钥（用于JWT签名）
CARGO_SESSION_SECRET=change-this-to-a-random-string-min-32-chars

# 开发模式开关
CARGO_DEBUG=false

# 日志级别
CARGO_LOG_LEVEL=INFO
```

### `.env`（本地开发，不提交到版本控制）

```bash
# 从 .env.example 复制并填入实际值
OPENAI_API_KEY=sk-your-actual-key-here
DEEPSEEK_API_KEY=sk-your-actual-key-here
PINECONE_API_KEY=your-pinecone-key-here
CARGO_SESSION_SECRET=your-random-secret-key-here
```

---

## 代码中的密钥使用方式

### Python (FastAPI/Flask)

```python
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# LLM API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# 优先使用 DeepSeek，回退到 OpenAI
LLM_API_KEY = DEEPSEEK_API_KEY or OPENAI_API_KEY
LLM_BASE_URL = os.getenv("DEEPSEEK_BASE_URL") if DEEPSEEK_API_KEY else os.getenv("OPENAI_BASE_URL")

# 向量数据库
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "cargo-technical-manual")

# 应用密钥
SESSION_SECRET = os.getenv("CARGO_SESSION_SECRET")
DEBUG = os.getenv("CARGO_DEBUG", "false").lower() == "true"

# 密钥验证
def validate_api_keys():
    """验证必需的 API 密钥是否已配置"""
    if not LLM_API_KEY:
        raise ValueError("至少需要配置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY")
    if not PINECONE_API_KEY:
        raise ValueError("PINECONE_API_KEY 未配置")
    if not SESSION_SECRET:
        raise ValueError("CARGO_SESSION_SECRET 未配置")
```

### TypeScript/React (前端)

```typescript
// 前端只应使用公开可暴露的密钥
// 敏感的 API 密钥应通过后端代理

const API_CONFIG = {
  // 后端 API 地址（不直接暴露 LLM API Key）
  BACKEND_URL: process.env.REACT_APP_BACKEND_URL || 'http://localhost:8000',
  
  // WebSocket 地址
  WS_URL: process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws',
};
```

---

## 密钥轮换策略

### 1. 定期轮换
- **LLM API Keys**: 每 90 天轮换一次
- **数据库密钥**: 每 180 天轮换一次
- **会话密钥**: 每次部署时更新

### 2. 紧急轮换
以下情况立即轮换所有密钥：
- 密钥疑似泄露
- 团队成员离职
- 安全审计要求

### 3. 轮换流程
```bash
# 1. 在服务商控制台生成新密钥
# 2. 更新 .env 文件
# 3. 重新部署应用
# 4. 验证新密钥工作正常
# 5. 在服务商控制台吊销旧密钥
```

---

## 安全最佳实践

### ❌ 禁止事项
1. **不要将密钥硬编码在源码中**
   ```python
   # 错误！
   API_KEY = "sk-xxxxxxxxxxxxxxxx"
   ```

2. **不要将 .env 文件提交到版本控制**
   ```bash
   # 确保 .gitignore 包含：
   .env
   *.pem
   *.key
   secrets/
   ```

3. **不要在日志中打印密钥**
   ```python
   # 错误！
   logger.info(f"Using API key: {API_KEY}")
   
   # 正确
   logger.info("API key configured: %s", "***" if API_KEY else "NOT SET")
   ```

4. **不要通过 URL 参数传递密钥**
   ```
   # 错误！
   https://api.example.com?api_key=sk-xxx
   ```

### ✅ 推荐做法
1. **使用环境变量**
2. **使用密钥管理服务**（如 AWS Secrets Manager、HashiCorp Vault）
3. **启用 API 密钥访问日志**
4. **设置 API 调用配额和告警**

---

## 生产环境密钥管理

### Docker 部署
```yaml
# docker-compose.yml
version: '3.8'
services:
  cargo-backend:
    image: cargo:latest
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
      - PINECONE_API_KEY=${PINECONE_API_KEY}
      - CARGO_SESSION_SECRET=${CARGO_SESSION_SECRET}
    env_file:
      - .env
```

### Kubernetes 部署
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cargo-api-keys
type: Opaque
stringData:
  OPENAI_API_KEY: "sk-xxxxxxxx"
  DEEPSEEK_API_KEY: "sk-xxxxxxxx"
  PINECONE_API_KEY: "xxxxxxxx"
  CARGO_SESSION_SECRET: "xxxxxxxx"
---
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cargo-backend
spec:
  template:
    spec:
      containers:
      - name: cargo
        image: cargo:latest
        envFrom:
        - secretRef:
            name: cargo-api-keys
```

---

## 密钥使用监控

### 监控指标
- API 调用次数
- 错误率（401/403 可能表示密钥问题）
- 响应时间
- 成本消耗

### 告警规则
```yaml
alerts:
  - name: api_key_expiring
    condition: key_age > 75 days
    severity: warning
    
  - name: api_key_invalid
    condition: http_401_rate > 1%
    severity: critical
    
  - name: unusual_api_usage
    condition: daily_cost > 2x average
    severity: warning
```

---

## 文档版本

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-01-31 | 初始版本 |

---

**注意**: 本文档仅定义密钥管理规范，不包含任何实际密钥值。实际密钥应通过安全渠道分发给开发团队成员。
