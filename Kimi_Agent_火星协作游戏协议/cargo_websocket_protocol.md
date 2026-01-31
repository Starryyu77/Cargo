# Project: CARGO - WebSocket 数据交互协议

> 版本: v1.0.0  
> 最后更新: 2024年  
> 适用场景: 火星-地球低带宽文本通信

---

## 目录

1. [协议概述](#1-协议概述)
2. [消息类型枚举](#2-消息类型枚举)
3. [消息格式JSON Schema](#3-消息格式json-schema)
4. [通信时序图](#4-通信时序图)
5. [延迟模拟机制](#5-延迟模拟机制)
6. [错误处理与重连策略](#6-错误处理与重连策略)
7. [附录](#7-附录)

---

## 1. 协议概述

### 1.1 设计目标

Project: CARGO 的通信协议专为火星-地球低带宽环境设计，核心特性包括：

- **盲盒执行**: 指令发送后无即时视觉反馈，符合真实通信延迟
- **状态同步**: 支持断线重连后的完整状态恢复
- **消息可靠性**: 确保关键消息不丢失，支持消息重传
- **带宽优化**: 最小化消息体积，适应低带宽环境

### 1.2 通信模型

```
┌─────────────┐      WebSocket      ┌─────────────┐
│   玩家客户端   │ <----------------> │    服务器    │
│  (地球控制台)  │   (低带宽/高延迟)   │  (火星中继站) │
└─────────────┘                     └─────────────┘
                                           │
                                           ▼
                                    ┌─────────────┐
                                    │  AI 系统    │
                                    │ - Jack LLM  │
                                    │ - 物理引擎   │
                                    │ - 状态管理   │
                                    └─────────────┘
```

### 1.3 消息结构通用格式

所有消息遵循统一的结构：

```json
{
  "type": "消息类型",
  "payload": {  },
  "metadata": {  },
  "timestamp": 1234567890,
  "sequence": 42,
  "session_id": "sess_xxx"
}
```

---

## 2. 消息类型枚举

### 2.1 客户端 -> 服务器 (Client to Server)

| 消息类型 | 代码值 | 描述 | 优先级 |
|---------|--------|------|--------|
| `INSTRUCTION` | 0x01 | 玩家发送的指令 | HIGH |
| `QUERY` | 0x02 | 查询当前状态 | MEDIUM |
| `PING` | 0x03 | 心跳检测 | LOW |
| `ACK` | 0x04 | 消息确认 | HIGH |
| `RECONNECT` | 0x05 | 重连请求 | CRITICAL |
| `SESSION_INIT` | 0x06 | 会话初始化 | CRITICAL |

### 2.2 服务器 -> 客户端 (Server to Client)

| 消息类型 | 代码值 | 描述 | 优先级 |
|---------|--------|------|--------|
| `JACK_MESSAGE` | 0x81 | Jack的回复消息 | HIGH |
| `STATE_UPDATE` | 0x82 | 状态更新（延迟后推送） | HIGH |
| `SYSTEM_EVENT` | 0x83 | 系统事件（危机触发等） | CRITICAL |
| `CONNECTION_STATUS` | 0x84 | 连接状态变化 | MEDIUM |
| `ERROR` | 0x85 | 错误信息 | HIGH |
| `PONG` | 0x86 | 心跳响应 | LOW |
| `ACK_CONFIRM` | 0x87 | 确认响应 | HIGH |
| `STATE_SYNC` | 0x88 | 完整状态同步 | CRITICAL |
| `MESSAGE_QUEUE` | 0x89 | 离线消息队列 | HIGH |

### 2.3 消息优先级说明

- **CRITICAL**: 必须立即发送，不重试机制
- **HIGH**: 确保送达，支持重试
- **MEDIUM**: 可延迟发送，丢包容忍
- **LOW**: 可丢弃，非关键消息

---

## 3. 消息格式 JSON Schema

### 3.1 通用消息头 Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-message-header",
  "title": "CARGO Message Header",
  "description": "所有消息的通用头部结构",
  "type": "object",
  "required": ["type", "timestamp", "sequence"],
  "properties": {
    "type": {
      "type": "string",
      "enum": [
        "INSTRUCTION", "QUERY", "PING", "ACK", "RECONNECT", "SESSION_INIT",
        "JACK_MESSAGE", "STATE_UPDATE", "SYSTEM_EVENT", "CONNECTION_STATUS",
        "ERROR", "PONG", "ACK_CONFIRM", "STATE_SYNC", "MESSAGE_QUEUE"
      ],
      "description": "消息类型"
    },
    "timestamp": {
      "type": "integer",
      "minimum": 0,
      "description": "Unix时间戳（毫秒）"
    },
    "sequence": {
      "type": "integer",
      "minimum": 0,
      "description": "消息序列号，用于排序和去重"
    },
    "session_id": {
      "type": "string",
      "pattern": "^sess_[a-zA-Z0-9]{16,32}$",
      "description": "会话唯一标识"
    },
    "message_id": {
      "type": "string",
      "pattern": "^msg_[a-zA-Z0-9]{16,32}$",
      "description": "消息唯一标识"
    },
    "payload": {
      "type": "object",
      "description": "消息内容负载"
    },
    "metadata": {
      "type": "object",
      "description": "元数据信息"
    }
  }
}
```

### 3.2 C2S: INSTRUCTION (玩家指令)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-instruction",
  "title": "CARGO Instruction Message",
  "description": "玩家发送的指令消息",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "INSTRUCTION"
    },
    "payload": {
      "type": "object",
      "required": ["text"],
      "properties": {
        "text": {
          "type": "string",
          "minLength": 1,
          "maxLength": 500,
          "description": "玩家输入的指令文本"
        },
        "category": {
          "type": "string",
          "enum": ["movement", "interaction", "system", "emergency", "general"],
          "default": "general",
          "description": "指令类别（客户端预分类）"
        },
        "target": {
          "type": "string",
          "maxLength": 100,
          "description": "指令目标对象（如设备ID）"
        },
        "priority": {
          "type": "string",
          "enum": ["low", "normal", "high", "critical"],
          "default": "normal",
          "description": "指令优先级"
        },
        "context": {
          "type": "object",
          "description": "上下文信息",
          "properties": {
            "location": { "type": "string" },
            "active_tasks": { 
              "type": "array",
              "items": { "type": "string" }
            }
          }
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "client_version": {
          "type": "string",
          "pattern": "^\\d+\\.\\d+\\.\\d+$",
          "description": "客户端版本号"
        },
        "platform": {
          "type": "string",
          "enum": ["web", "desktop", "mobile"],
          "description": "客户端平台"
        },
        "input_method": {
          "type": "string",
          "enum": ["keyboard", "voice", "preset"],
          "description": "输入方式"
        }
      }
    },
    "timestamp": {
      "type": "integer",
      "description": "客户端发送时间戳"
    },
    "sequence": {
      "type": "integer",
      "description": "消息序列号"
    },
    "session_id": {
      "type": "string",
      "description": "会话ID"
    },
    "message_id": {
      "type": "string",
      "description": "消息唯一ID"
    }
  }
}
```

**示例:**

```json
{
  "type": "INSTRUCTION",
  "payload": {
    "text": "检查氧气储备并报告当前状态",
    "category": "system",
    "priority": "high",
    "context": {
      "location": "command_center",
      "active_tasks": ["oxygen_monitoring"]
    }
  },
  "metadata": {
    "client_version": "1.0.0",
    "platform": "web",
    "input_method": "keyboard"
  },
  "timestamp": 1704067200000,
  "sequence": 15,
  "session_id": "sess_a1b2c3d4e5f67890",
  "message_id": "msg_x1y2z3w4v5u6t7r8"
}
```

### 3.3 C2S: QUERY (状态查询)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-query",
  "title": "CARGO Query Message",
  "description": "状态查询消息",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "QUERY"
    },
    "payload": {
      "type": "object",
      "required": ["query_type"],
      "properties": {
        "query_type": {
          "type": "string",
          "enum": ["full_state", "partial_state", "message_history", "system_status"],
          "description": "查询类型"
        },
        "fields": {
          "type": "array",
          "items": { "type": "string" },
          "description": "部分查询时指定的字段列表"
        },
        "since": {
          "type": "integer",
          "description": "查询此时间戳之后的数据"
        },
        "filter": {
          "type": "object",
          "description": "过滤条件",
          "properties": {
            "message_types": {
              "type": "array",
              "items": { "type": "string" }
            },
            "limit": {
              "type": "integer",
              "minimum": 1,
              "maximum": 100
            }
          }
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" }
  }
}
```

### 3.4 C2S: PING (心跳检测)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-ping",
  "title": "CARGO Ping Message",
  "description": "心跳检测消息",
  "type": "object",
  "required": ["type", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "PING"
    },
    "payload": {
      "type": "object",
      "properties": {
        "latency_check": {
          "type": "boolean",
          "default": false,
          "description": "是否进行延迟检测"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" }
  }
}
```

### 3.5 C2S: ACK (消息确认)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-ack",
  "title": "CARGO ACK Message",
  "description": "消息确认",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "ACK"
    },
    "payload": {
      "type": "object",
      "required": ["acknowledged_messages"],
      "properties": {
        "acknowledged_messages": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["message_id", "received_at"],
            "properties": {
              "message_id": { "type": "string" },
              "received_at": { "type": "integer" }
            }
          },
          "description": "已确认接收的消息列表"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" }
  }
}
```

### 3.6 C2S: RECONNECT (重连请求)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-reconnect",
  "title": "CARGO Reconnect Message",
  "description": "断线重连请求",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "RECONNECT"
    },
    "payload": {
      "type": "object",
      "required": ["previous_session_id", "last_sequence"],
      "properties": {
        "previous_session_id": {
          "type": "string",
          "description": "之前的会话ID"
        },
        "last_sequence": {
          "type": "integer",
          "description": "客户端最后收到的消息序列号"
        },
        "last_timestamp": {
          "type": "integer",
          "description": "客户端最后收到消息的时间戳"
        },
        "disconnect_reason": {
          "type": "string",
          "enum": ["network_error", "timeout", "client_close", "server_close", "unknown"],
          "description": "断开原因"
        },
        "offline_duration": {
          "type": "integer",
          "description": "离线时长（毫秒）"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" }
  }
}
```

### 3.7 S2C: JACK_MESSAGE (Jack回复)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-jack-message",
  "title": "CARGO Jack Message",
  "description": "Jack的回复消息",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "JACK_MESSAGE"
    },
    "payload": {
      "type": "object",
      "required": ["text", "emotion", "timestamp"],
      "properties": {
        "text": {
          "type": "string",
          "minLength": 1,
          "description": "Jack的回复文本"
        },
        "emotion": {
          "type": "string",
          "enum": ["calm", "worried", "panicked", "excited", "focused", "tired", "confused"],
          "description": "Jack当前的情绪状态"
        },
        "stress_level": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100,
          "description": "压力值 (0-100)"
        },
        "health_status": {
          "type": "object",
          "properties": {
            "physical": {
              "type": "integer",
              "minimum": 0,
              "maximum": 100,
              "description": "身体状况"
            },
            "mental": {
              "type": "integer",
              "minimum": 0,
              "maximum": 100,
              "description": "精神状态"
            },
            "oxygen": {
              "type": "integer",
              "minimum": 0,
              "maximum": 100,
              "description": "氧气水平"
            }
          }
        },
        "timestamp": {
          "type": "integer",
          "description": "消息生成时间戳"
        },
        "delay_simulated": {
          "type": "integer",
          "minimum": 0,
          "description": "模拟的通信延迟（毫秒）"
        },
        "in_response_to": {
          "type": "string",
          "description": "响应的指令消息ID"
        },
        "action_taken": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "action": { "type": "string" },
              "status": { 
                "type": "string",
                "enum": ["pending", "completed", "failed"]
              },
              "result": { "type": "string" }
            }
          },
          "description": "已执行的动作列表"
        },
        "attachments": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "type": { 
                "type": "string",
                "enum": ["image", "data", "log"]
              },
              "url": { "type": "string" },
              "description": { "type": "string" }
            }
          },
          "description": "附件数据"
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "processing_time": {
          "type": "integer",
          "description": "AI处理耗时（毫秒）"
        },
        "llm_model": {
          "type": "string",
          "description": "使用的AI模型"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "回复置信度"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" },
    "message_id": { "type": "string" }
  }
}
```

**示例:**

```json
{
  "type": "JACK_MESSAGE",
  "payload": {
    "text": "收到指令。正在检查氧气储备...当前氧气水平为78%，预计还能维持约6小时。生命维持系统运行正常。",
    "emotion": "calm",
    "stress_level": 25,
    "health_status": {
      "physical": 85,
      "mental": 70,
      "oxygen": 78
    },
    "timestamp": 1704067500000,
    "delay_simulated": 180000,
    "in_response_to": "msg_x1y2z3w4v5u6t7r8",
    "action_taken": [
      {
        "action": "check_oxygen_level",
        "status": "completed",
        "result": "78%"
      }
    ]
  },
  "metadata": {
    "processing_time": 1200,
    "llm_model": "gpt-4",
    "confidence": 0.95
  },
  "timestamp": 1704067500000,
  "sequence": 23,
  "session_id": "sess_a1b2c3d4e5f67890",
  "message_id": "msg_jack_reply_001"
}
```

### 3.8 S2C: STATE_UPDATE (状态更新)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-state-update",
  "title": "CARGO State Update",
  "description": "游戏状态更新",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "STATE_UPDATE"
    },
    "payload": {
      "type": "object",
      "required": ["delta", "timestamp"],
      "properties": {
        "delta": {
          "type": "object",
          "description": "状态增量变化",
          "properties": {
            "jack": {
              "type": "object",
              "description": "Jack状态变化",
              "properties": {
                "location": { "type": "string" },
                "health": { "type": "object" },
                "inventory": { "type": "array" },
                "current_action": { "type": "string" }
              }
            },
            "environment": {
              "type": "object",
              "description": "环境状态变化",
              "properties": {
                "time": { "type": "integer" },
                "weather": { "type": "string" },
                "temperature": { "type": "number" },
                "radiation": { "type": "number" },
                "oxygen_level": { "type": "number" }
              }
            },
            "systems": {
              "type": "object",
              "description": "系统状态变化",
              "properties": {
                "life_support": { "type": "object" },
                "communication": { "type": "object" },
                "power": { "type": "object" }
              }
            },
            "mission": {
              "type": "object",
              "description": "任务状态变化",
              "properties": {
                "active_objectives": { "type": "array" },
                "completed_objectives": { "type": "array" },
                "progress": { "type": "object" }
              }
            }
          }
        },
        "full_state": {
          "type": "boolean",
          "default": false,
          "description": "是否为完整状态（非增量）"
        },
        "triggered_by": {
          "type": "string",
          "description": "触发此更新的消息ID或事件"
        },
        "timestamp": {
          "type": "integer",
          "description": "状态更新时间戳"
        },
        "update_type": {
          "type": "string",
          "enum": ["immediate", "delayed", "periodic", "event_driven"],
          "description": "更新类型"
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "update_reason": {
          "type": "string",
          "description": "更新原因说明"
        },
        "affected_systems": {
          "type": "array",
          "items": { "type": "string" }
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" },
    "message_id": { "type": "string" }
  }
}
```

### 3.9 S2C: SYSTEM_EVENT (系统事件)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-system-event",
  "title": "CARGO System Event",
  "description": "系统事件通知",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "SYSTEM_EVENT"
    },
    "payload": {
      "type": "object",
      "required": ["event_type", "severity", "message"],
      "properties": {
        "event_type": {
          "type": "string",
          "enum": [
            "crisis_alert", "warning", "info", "achievement",
            "milestone", "system_failure", "resource_low",
            "discovery", "time_event", "connection_change"
          ],
          "description": "事件类型"
        },
        "severity": {
          "type": "string",
          "enum": ["critical", "high", "medium", "low", "info"],
          "description": "严重程度"
        },
        "message": {
          "type": "string",
          "description": "事件描述"
        },
        "title": {
          "type": "string",
          "description": "事件标题"
        },
        "details": {
          "type": "object",
          "description": "事件详细信息"
        },
        "actions_required": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "action_id": { "type": "string" },
              "description": { "type": "string" },
              "priority": { 
                "type": "string",
                "enum": ["optional", "recommended", "required"]
              }
            }
          },
          "description": "建议采取的行动"
        },
        "auto_triggered": {
          "type": "boolean",
          "description": "是否自动触发"
        },
        "dismissible": {
          "type": "boolean",
          "default": true,
          "description": "是否可关闭"
        },
        "expiry": {
          "type": "integer",
          "description": "事件过期时间戳"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" },
    "message_id": { "type": "string" }
  }
}
```

**示例 (危机事件):**

```json
{
  "type": "SYSTEM_EVENT",
  "payload": {
    "event_type": "crisis_alert",
    "severity": "critical",
    "title": "氧气泄漏警报",
    "message": "检测到舱室B氧气压力下降，可能存在泄漏。",
    "details": {
      "location": "module_B",
      "affected_systems": ["life_support", "oxygen_supply"],
      "current_pressure": "18.5 kPa",
      "normal_pressure": "21.0 kPa"
    },
    "actions_required": [
      {
        "action_id": "isolate_module_b",
        "description": "隔离B舱室",
        "priority": "required"
      },
      {
        "action_id": "initiate_repair",
        "description": "启动维修程序",
        "priority": "recommended"
      }
    ],
    "auto_triggered": true,
    "dismissible": false
  },
  "timestamp": 1704067800000,
  "sequence": 25,
  "session_id": "sess_a1b2c3d4e5f67890",
  "message_id": "msg_crisis_001"
}
```

### 3.10 S2C: CONNECTION_STATUS (连接状态)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-connection-status",
  "title": "CARGO Connection Status",
  "description": "连接状态变化通知",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "CONNECTION_STATUS"
    },
    "payload": {
      "type": "object",
      "required": ["status"],
      "properties": {
        "status": {
          "type": "string",
          "enum": ["connected", "disconnected", "reconnecting", "degraded", "limited"],
          "description": "连接状态"
        },
        "previous_status": {
          "type": "string",
          "description": "之前的连接状态"
        },
        "reason": {
          "type": "string",
          "description": "状态变化原因"
        },
        "estimated_delay": {
          "type": "integer",
          "description": "预估延迟（毫秒）"
        },
        "signal_quality": {
          "type": "integer",
          "minimum": 0,
          "maximum": 100,
          "description": "信号质量 (0-100)"
        },
        "bandwidth_available": {
          "type": "integer",
          "description": "可用带宽 (bps)"
        },
        "reconnect_attempt": {
          "type": "integer",
          "description": "重连尝试次数"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" }
  }
}
```

### 3.11 S2C: ERROR (错误信息)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-error",
  "title": "CARGO Error Message",
  "description": "错误信息",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "ERROR"
    },
    "payload": {
      "type": "object",
      "required": ["code", "message"],
      "properties": {
        "code": {
          "type": "string",
          "description": "错误代码"
        },
        "message": {
          "type": "string",
          "description": "错误描述"
        },
        "details": {
          "type": "object",
          "description": "错误详情"
        },
        "recoverable": {
          "type": "boolean",
          "description": "是否可恢复"
        },
        "retry_after": {
          "type": "integer",
          "description": "建议重试时间（毫秒）"
        },
        "original_message": {
          "type": "object",
          "description": "导致错误的原始消息"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" },
    "message_id": { "type": "string" }
  }
}
```

**错误代码表:**

| 错误代码 | 描述 | 可恢复 | 建议操作 |
|---------|------|--------|----------|
| `E001` | 消息格式错误 | 是 | 检查消息格式 |
| `E002` | 会话已过期 | 是 | 重新初始化会话 |
| `E003` | 消息过大 | 是 | 压缩或分割消息 |
| `E004` | 速率限制 | 是 | 稍后重试 |
| `E005` | 服务不可用 | 是 | 稍后重试 |
| `E006` | 内部服务器错误 | 是 | 联系支持 |
| `E007` | 无效的消息类型 | 否 | 检查协议版本 |
| `E008` | 会话不存在 | 否 | 创建新会话 |

### 3.12 S2C: STATE_SYNC (完整状态同步)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-state-sync",
  "title": "CARGO State Sync",
  "description": "完整状态同步（重连后）",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "STATE_SYNC"
    },
    "payload": {
      "type": "object",
      "required": ["state", "sync_timestamp"],
      "properties": {
        "state": {
          "type": "object",
          "description": "完整游戏状态",
          "properties": {
            "jack": {
              "type": "object",
              "properties": {
                "id": { "type": "string" },
                "name": { "type": "string" },
                "location": { "type": "string" },
                "health": {
                  "type": "object",
                  "properties": {
                    "physical": { "type": "integer" },
                    "mental": { "type": "integer" },
                    "oxygen": { "type": "integer" }
                  }
                },
                "stress_level": { "type": "integer" },
                "emotion": { "type": "string" },
                "inventory": { "type": "array" },
                "current_action": { "type": "string" },
                "skills": { "type": "object" }
              }
            },
            "environment": {
              "type": "object",
              "properties": {
                "sol": { "type": "integer" },
                "time": { "type": "integer" },
                "location": { "type": "string" },
                "weather": { "type": "string" },
                "temperature": { "type": "number" },
                "pressure": { "type": "number" },
                "radiation": { "type": "number" },
                "oxygen_level": { "type": "number" },
                "dust_storm_active": { "type": "boolean" }
              }
            },
            "base": {
              "type": "object",
              "properties": {
                "systems": { "type": "object" },
                "resources": { "type": "object" },
                "modules": { "type": "array" }
              }
            },
            "mission": {
              "type": "object",
              "properties": {
                "current_objective": { "type": "string" },
                "objectives": { "type": "array" },
                "progress": { "type": "object" },
                "time_remaining": { "type": "integer" }
              }
            },
            "events": {
              "type": "object",
              "properties": {
                "active_events": { "type": "array" },
                "pending_events": { "type": "array" }
              }
            }
          }
        },
        "sync_timestamp": {
          "type": "integer",
          "description": "状态快照时间戳"
        },
        "sync_type": {
          "type": "string",
          "enum": ["full", "partial"],
          "description": "同步类型"
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" },
    "message_id": { "type": "string" }
  }
}
```

### 3.13 S2C: MESSAGE_QUEUE (离线消息队列)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "cargo-message-queue",
  "title": "CARGO Message Queue",
  "description": "离线期间的消息队列",
  "type": "object",
  "required": ["type", "payload", "timestamp", "sequence"],
  "properties": {
    "type": {
      "const": "MESSAGE_QUEUE"
    },
    "payload": {
      "type": "object",
      "required": ["messages", "queue_info"],
      "properties": {
        "messages": {
          "type": "array",
          "items": {
            "type": "object",
            "description": "消息对象（可以是任何S2C消息类型）"
          },
          "description": "离线期间的消息列表"
        },
        "queue_info": {
          "type": "object",
          "properties": {
            "total_count": { "type": "integer" },
            "critical_count": { "type": "integer" },
            "from_sequence": { "type": "integer" },
            "to_sequence": { "type": "integer" },
            "from_timestamp": { "type": "integer" },
            "to_timestamp": { "type": "integer" },
            "truncated": {
              "type": "boolean",
              "description": "是否被截断（消息过多）"
            }
          }
        }
      }
    },
    "timestamp": { "type": "integer" },
    "sequence": { "type": "integer" },
    "session_id": { "type": "string" },
    "message_id": { "type": "string" }
  }
}
```

---

## 4. 通信时序图

### 4.1 流程1: 正常指令执行

```
时间 ---------------------------------------------------------------------

玩家          客户端            服务器         AI解释器      物理引擎      Jack LLM
 |              |                 |              |             |            |
 | 输入指令     |                 |              |             |            |
 |------------->|                 |              |             |            |
 |              |                 |              |             |            |
 |              |  INSTRUCTION    |              |             |            |
 |              |---------------->|  分析指令    |             |            |
 |              |                 |------------->|             |            |
 |              |                 |              |             |            |
 |              |                 |  执行状态变更              |            |
 |              |                 |--------------------------->|            |
 |              |                 |              |             |            |
 |              |                 |  状态更新完成              |            |
 |              |                 |<---------------------------|            |
 |              |                 |              |             |            |
 |              |                 |  生成回复                  |            |
 |              |                 |---------------------------------------->|
 |              |                 |              |             |            |
 |              |                 |  [延迟模拟: 3-22分钟]                    |
 |              |                 |              |             |            |
 |              |                 |  JACK_MESSAGE            |            |
 |              |                 |<----------------------------------------|
 |              |                 |              |             |            |
 |              |                 |  STATE_UPDATE             |            |
 |              |                 |<---------------------------|            |
 |              |                 |              |             |            |
 |              |  显示消息       |              |             |            |
 |              |<---------------|              |             |            |
 | 看到回复     |                 |              |             |            |
 |<-------------|                 |              |             |            |
 |              |                 |              |             |            |
```

**说明:**
1. 玩家输入指令，客户端发送 `INSTRUCTION` 消息
2. 服务器通过 AI 解释器分析指令意图
3. 物理引擎执行状态变更（如移动、使用物品等）
4. Jack LLM 根据新状态生成自然语言回复
5. 模拟火星-地球通信延迟（3-22分钟）
6. 服务器发送 `JACK_MESSAGE` 和 `STATE_UPDATE`
7. 客户端显示回复，玩家看到结果

### 4.2 流程2: 危机事件触发

```
时间 ---------------------------------------------------------------------

物理引擎         服务器         危机检测器      Jack LLM       客户端
    |              |               |              |              |
    | 检测到异常   |               |              |              |
    |------------->|               |              |              |
    |              |               |              |              |
    |              | 触发事件      |              |              |
    |              |-------------->|              |              |
    |              |               |              |              |
    |              | SYSTEM_EVENT  |              |              |
    |              |------------------------------|------------->|
    |              | (危机警告)    |              |              |
    |              |               |              |              |
    |              | 生成感知描述  |              |              |
    |              |---------------|------------->|              |
    |              |               |              |              |
    |              | [延迟模拟]    |              |              |
    |              |               |              |              |
    |              | JACK_MESSAGE  |              |              |
    |              |------------------------------|------------->|
    |              | (Jack的反应)  |              |              |
    |              |               |              |              |
```

**说明:**
1. 物理引擎检测到异常（如氧气泄漏、设备故障）
2. 危机检测器评估严重程度
3. 立即发送 `SYSTEM_EVENT`（危机警告）
4. Jack LLM 根据危机情况生成感知描述
5. 延迟后发送 `JACK_MESSAGE`（Jack的恐慌/担忧反应）

### 4.3 流程3: 断线重连

```
时间 ---------------------------------------------------------------------

客户端           服务器         状态存储       消息队列
   |               |              |              |
   | 连接断开      |              |              |
   |<------------->|              |              |
   |               |              |              |
   | [离线期间]    |              |              |
   |               | 持续保存状态 |              |
   |               |------------->|              |
   |               | 缓存消息     |              |
   |               |---------------------------->|
   |               |              |              |
   | 重连请求      |              |              |
   |-------------->|              |              |
   |               |              |              |
   | RECONNECT     |              |              |
   |-------------->|              |              |
   |               |              |              |
   | 验证会话      |              |              |
   |               |------------->|              |
   |               |<-------------|              |
   |               |              |              |
   | STATE_SYNC    |              |              |
   |<--------------|              |              |
   | (完整状态)    |              |              |
   |               |              |              |
   | MESSAGE_QUEUE |              |              |
   |<--------------|              |              |
   | (离线消息)    |              |              |
   |               |              |              |
   | ACK           |              |              |
   |-------------->|              |              |
   | (确认接收)    |              |              |
   |               |              |              |
   | [恢复通信]    |              |              |
   |               |              |              |
```

**说明:**
1. 连接意外断开
2. 离线期间，服务器持续保存状态，缓存消息
3. 客户端检测到重连条件，发送 `RECONNECT` 请求
4. 服务器验证会话有效性
5. 发送 `STATE_SYNC` 恢复完整状态
6. 发送 `MESSAGE_QUEUE` 恢复离线期间的消息
7. 客户端发送 `ACK` 确认接收
8. 恢复正常通信

### 4.4 流程4: 心跳与连接质量检测

```
时间 ---------------------------------------------------------------------

客户端           服务器
   |               |
   | 定时心跳      |
   |-------------->|
   | PING          |
   |               |
   |               | 计算延迟
   |               |
   |<--------------|
   | PONG          |
   | (携带延迟信息)|
   |               |
   | [延迟过高]    |
   |               |
   |<--------------|
   | CONNECTION_STATUS
   | (degraded)    |
   |               |
   | [延迟恢复]    |
   |               |
   |<--------------|
   | CONNECTION_STATUS
   | (connected)   |
   |               |
```

---

## 5. 延迟模拟机制

### 5.1 延迟模型

```
+------------------------------------------------------------------+
|                    火星-地球通信延迟模型                           |
+------------------------------------------------------------------+
|                                                                   |
|  距离范围: 54.6M - 401M km                                       |
|                                                                   |
|    最短延迟 (最近距离)                                            |
|    +-- 3 分钟 (光速往返)                                         |
|                                                                   |
|    最长延迟 (最远距离)                                            |
|    +-- 22 分钟 (光速往返)                                        |
|                                                                   |
|    随机抖动: +-10%                                                |
|                                                                   |
|    网络拥塞加成: +0-5 分钟                                       |
|                                                                   |
|  实际延迟 = 基础延迟 + 抖动 + 拥塞加成                             |
|                                                                   |
+------------------------------------------------------------------+
```

### 5.2 延迟计算公式

```python
import random

def calculate_delay(base_distance_factor, congestion_level=0):
    """
    计算通信延迟
    
    Args:
        base_distance_factor: 0.0-1.0, 0=最近距离, 1=最远距离
        congestion_level: 0-10, 网络拥塞程度
    
    Returns:
        delay_ms: 延迟时间（毫秒）
    """
    # 基础延迟: 3-22分钟
    MIN_DELAY = 3 * 60 * 1000   # 3分钟
    MAX_DELAY = 22 * 60 * 1000  # 22分钟
    
    # 根据距离因子计算基础延迟
    base_delay = MIN_DELAY + (MAX_DELAY - MIN_DELAY) * base_distance_factor
    
    # 随机抖动: +-10%
    jitter = random.uniform(-0.1, 0.1) * base_delay
    
    # 拥塞加成: 0-5分钟
    congestion_delay = (congestion_level / 10) * 5 * 60 * 1000
    
    # 最终延迟
    total_delay = base_delay + jitter + congestion_delay
    
    return int(total_delay)
```

### 5.3 延迟配置参数

```json
{
  "delay_simulation": {
    "enabled": true,
    "mode": "dynamic",
    "static_delay_ms": 600000,
    "dynamic_range": {
      "min_ms": 180000,
      "max_ms": 1320000
    },
    "jitter_percent": 10,
    "congestion": {
      "enabled": true,
      "max_additional_delay_ms": 300000
    },
    "realistic_orbit": {
      "enabled": false,
      "orbital_period_days": 687,
      "current_sol": 1
    }
  }
}
```

### 5.4 消息队列机制

```
+------------------------------------------------------------------+
|                      消息队列管理                                 |
+------------------------------------------------------------------+
|                                                                   |
|  +-------------+    +-------------+    +-------------+          |
|  |  发送队列    |    |  延迟队列    |    |  离线队列    |          |
|  |  (待发送)   |--->|  (延迟中)   |--->|  (待重连)   |          |
|  +-------------+    +-------------+    +-------------+          |
|         |                  |                  |                  |
|         v                  v                  v                  |
|  +-----------------------------------------------------+        |
|  |                  消息调度器                          |        |
|  |  - 优先级排序  - 延迟控制  - 重试机制  - 去重处理    |        |
|  +-----------------------------------------------------+        |
|                                                                   |
|  队列容量:                                                        |
|  - 发送队列: 100条                                                |
|  - 延迟队列: 无限制（按时间排序）                                  |
|  - 离线队列: 500条（超过则丢弃旧消息）                             |
|                                                                   |
|  消息保留时间: 24小时                                              |
|                                                                   |
+------------------------------------------------------------------+
```

---

## 6. 错误处理与重连策略

### 6.1 连接超时处理

```
+------------------------------------------------------------------+
|                     连接超时处理流程                              |
+------------------------------------------------------------------+
|                                                                   |
|  超时类型              超时时间          处理动作                  |
|  ---------------------------------------------------------------- |
|  心跳超时              30秒            发送重连请求                |
|  发送超时              10秒            重试发送(最多3次)           |
|  连接建立超时          10秒            指数退避重连                |
|  重连超时              60秒            提示用户手动重连            |
|                                                                   |
|  指数退避策略:                                                    |
|  第1次重连: 立即                                                  |
|  第2次重连: 2秒后                                                 |
|  第3次重连: 4秒后                                                 |
|  第4次重连: 8秒后                                                 |
|  第5次重连: 16秒后                                                |
|  最大间隔: 60秒                                                   |
|                                                                   |
+------------------------------------------------------------------+
```

### 6.2 消息丢失检测

```
+------------------------------------------------------------------+
|                     消息丢失检测机制                              |
+------------------------------------------------------------------+
|                                                                   |
|  检测方法: 序列号连续性检查                                        |
|                                                                   |
|  客户端                          服务器                            |
|     |                              |                             |
|     |  发送消息 (seq=10)           |                             |
|     |----------------------------->|                             |
|     |                              |                             |
|     |  发送消息 (seq=11)           |                             |
|     |----------------------------->|                             |
|     |                              |                             |
|     |  发送消息 (seq=12) [丢失]    |                             |
|     |-----------X                  |                             |
|     |                              |                             |
|     |  发送消息 (seq=13)           |                             |
|     |----------------------------->|                             |
|     |                              |                             |
|     |<-----------------------------|  回复 (ack_seq=11)          |
|     |                              |  检测到缺失: 12, 13         |
|     |                              |                             |
|     |  重发消息 (seq=12)           |                             |
|     |----------------------------->|                             |
|     |                              |                             |
|     |<-----------------------------|  回复 (ack_seq=13)          |
|     |                              |                             |
|                                                                   |
|  ACK策略:                                                         |
|  - 每5条消息或每5秒发送一次ACK                                     |
|  - 未确认消息在3秒后重发                                          |
|  - 最多重试3次                                                    |
|                                                                   |
+------------------------------------------------------------------+
```

### 6.3 状态同步机制

```
+------------------------------------------------------------------+
|                     状态同步策略                                  |
+------------------------------------------------------------------+
|                                                                   |
|  同步触发条件:                                                    |
|  1. 客户端重连成功                                                |
|  2. 检测到状态不一致                                              |
|  3. 客户端主动请求 (QUERY)                                        |
|  4. 定期同步 (每5分钟)                                            |
|                                                                   |
|  同步类型:                                                        |
|  +-----------------+-------------------------------------------+ |
|  | 增量同步 (delta) | 只发送变化的部分，适用于正常游戏过程       | |
|  | 完整同步 (full)  | 发送完整状态，适用于重连后                 | |
|  | 部分同步 (partial)| 发送指定字段，适用于查询特定信息          | |
|  +-----------------+-------------------------------------------+ |
|                                                                   |
|  状态版本控制:                                                    |
|  - 每个状态更新包含版本号 (state_version)                         |
|  - 客户端维护本地状态版本                                         |
|  - 版本不匹配时触发完整同步                                       |
|                                                                   |
|  冲突解决:                                                        |
|  - 服务器状态为准（权威源）                                       |
|  - 客户端本地预测状态可保留，收到服务器状态后覆盖                   |
|                                                                   |
+------------------------------------------------------------------+
```

### 6.4 会话恢复策略

```
+------------------------------------------------------------------+
|                     会话恢复策略                                  |
+------------------------------------------------------------------+
|                                                                   |
|  会话状态存储:                                                    |
|  +-----------------------------------------------------------+   |
|  |  存储位置: Redis (内存) + 数据库 (持久化)                   |   |
|  |  过期时间: 24小时                                           |   |
|  |  存储内容:                                                  |   |
|  |    - 游戏状态快照                                           |   |
|  |    - 消息历史 (最近100条)                                   |   |
|  |    - 玩家偏好设置                                           |   |
|  |    - 会话元数据                                             |   |
|  +-----------------------------------------------------------+   |
|                                                                   |
|  恢复流程:                                                        |
|                                                                   |
|  1. 重连请求                                                      |
|     客户端发送 RECONNECT 消息，携带:                              |
|     - previous_session_id                                         |
|     - last_sequence (最后收到的消息序号)                          |
|     - last_timestamp (最后活动时间)                               |
|                                                                   |
|  2. 会话验证                                                      |
|     服务器检查:                                                   |
|     - 会话是否存在                                                |
|     - 会话是否过期                                                |
|     - 玩家身份是否匹配                                            |
|                                                                   |
|  3. 状态恢复                                                      |
|     如果会话有效:                                                 |
|     a. 发送 STATE_SYNC (完整状态)                                 |
|     b. 发送 MESSAGE_QUEUE (离线消息)                              |
|                                                                   |
|  4. 会话续期                                                      |
|     生成新的 session_id，继承原会话状态                           |
|                                                                   |
|  恢复失败处理:                                                    |
|  +-----------------+----------------------------------------+   |
|  | 会话过期 (>24h)  | 创建新会话，从检查点开始               |   |
|  | 会话不存在       | 创建新会话                             |   |
|  | 身份验证失败     | 拒绝连接，要求重新登录                 |   |
|  | 数据损坏         | 回滚到最近检查点                       |   |
|  +-----------------+----------------------------------------+   |
|                                                                   |
+------------------------------------------------------------------+
```

### 6.5 错误处理流程图

```
                         +-------------+
                         |   错误发生   |
                         +------+------+
                                |
                                v
                    +-----------------------+
                    |    错误分类            |
                    +-----------+-----------+
                                |
           +--------------------+--------------------+
           |                    |                    |
           v                    v                    v
    +-------------+      +-------------+      +-------------+
    |  可恢复错误  |      |  不可恢复   |      |  致命错误   |
    |  (网络/超时) |      |  (数据/会话) |      |  (系统崩溃) |
    +------+------+      +------+------+      +------+------+
           |                    |                    |
           v                    v                    v
    +-------------+      +-------------+      +-------------+
    |  自动重试    |      |  提示用户    |      |  紧急保存    |
    |  (指数退避)  |      |  提供选项    |      |  状态        |
    +------+------+      +------+------+      +------+------+
           |                    |                    |
           v                    v                    v
    +-------------+      +-------------+      +-------------+
    |  重试成功?   |      |  用户选择    |      |  重新启动    |
    +------+------+      +------+------+      +------+------+
           |                    |                    |
      +----+----+          +----+----+          +----+----+
      |         |          |         |          |         |
      v         v          v         v          v         v
  +------+  +------+   +------+  +------+   +------+  +------+
  | 成功  |  | 失败  |   | 重连  |  | 新游戏|   | 恢复  |  | 放弃  |
  | 继续  |  | 降级  |   |      |  |      |   |      |  |      |
  +------+  +------+   +------+  +------+   +------+  +------+
```

---

## 7. 附录

### 7.1 协议版本历史

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0.0 | 2024 | 初始版本，支持基础通信、延迟模拟、断线重连 |

### 7.2 消息大小限制

| 消息类型 | 最大大小 | 说明 |
|---------|---------|------|
| INSTRUCTION | 2KB | 指令文本 |
| JACK_MESSAGE | 10KB | 包含可能的附件 |
| STATE_UPDATE | 5KB | 增量更新 |
| STATE_SYNC | 50KB | 完整状态 |
| MESSAGE_QUEUE | 100KB | 离线消息队列 |
| 其他 | 1KB | 小型消息 |

### 7.3 压缩策略

```
消息大小 > 1KB: 启用 gzip 压缩
压缩级别: 6 (平衡速度和压缩率)
```

### 7.4 安全考虑

- 所有消息使用 WSS (WebSocket Secure)
- 会话令牌定期轮换
- 敏感操作需要二次确认
- 消息完整性校验 (HMAC)

---

**文档结束**

> 如有问题，请联系开发团队
