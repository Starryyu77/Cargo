
# Project: CARGO 技术资料库 - 字段说明文档

## 一、核心数据模型

### 1. TechnicalManualEntry (技术手册条目)

#### 1.1 标识字段

| 字段名 | 类型 | 必需 | 描述 | 示例 |
|-------|------|-----|------|------|
| `entry_id` | string | 是 | 唯一标识符，格式：[CATEGORY]-[SUB]-[NUM]-[REV] | PWR-RTG-0042-REVC |
| `legacy_id` | string | 否 | 旧版文档编号 | MMOD-RTG-PLUTONIUM-2100 |

#### 1.2 分类字段

| 字段名 | 类型 | 必需 | 描述 | 枚举值 |
|-------|------|-----|------|-------|
| `category.primary` | string | 是 | 主分类 | PWR, CHEM, MECH, MED, ELEC, NAV, ENV, COM |
| `category.secondary` | string | 否 | 子分类 | 放射性同位素发电 |
| `category.code` | string | 是 | 分类代码 | PWR-RTG |
| `category.display_name` | string | 否 | 显示名称 | 动力系统 - 放射性同位素热电机 |

#### 1.3 标题字段

| 字段名 | 类型 | 必需 | 描述 | 约束 |
|-------|------|-----|------|------|
| `title.full` | string | 是 | 完整标题 | - |
| `title.short` | string | 是 | 短标题 | 最大50字符 |
| `title.document_number` | string | 否 | 文档编号 | TM-PWR-RTG-0042 |

#### 1.4 技术内容字段

| 字段名 | 类型 | 必需 | 描述 |
|-------|------|-----|------|
| `technical_content.abstract` | string | 否 | 技术摘要 |
| `technical_content.description.overview` | string | 是 | 概述 |
| `technical_content.description.principles` | array | 否 | 工作原理段落 |
| `technical_content.description.applications` | array | 否 | 应用场景 |
| `technical_content.description.limitations` | array | 否 | 限制条件 |

#### 1.5 图纸字段 (diagrams)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `diagram_id` | string | 图纸唯一ID |
| `type` | enum | 图纸类型 |
| `title` | string | 图纸标题 |
| `source.type` | enum | svg, png, jpg, interactive_svg, canvas |
| `source.url` | string | 资源URL |
| `annotations` | array | 图纸标注 |

**图纸类型枚举：**
- `schematic` - 原理图
- `cross_section` - 剖面图
- `flow_chart` - 流程图
- `block_diagram` - 框图
- `wiring_diagram` - 接线图
- `isometric` - 等轴测图
- `exploded_view` - 爆炸图
- `data_plot` - 数据图表

#### 1.6 规格表字段 (specifications)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `table_id` | string | 表格ID |
| `title` | string | 表格标题 |
| `columns` | array | 列定义 |
| `rows` | array | 数据行 |
| `notes` | array | 表格注释 |

#### 1.7 公式字段 (formulas)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `formula_id` | string | 公式ID |
| `name` | string | 公式名称 |
| `latex` | string | LaTeX格式 |
| `plain_text` | string | 纯文本格式 |
| `variables` | array | 变量定义 |
| `conditions` | array | 适用条件 |

#### 1.8 安全警告字段 (safety_warnings)

| 字段名 | 类型 | 描述 | 枚举值 |
|-------|------|------|-------|
| `level` | enum | 警告级别 | DANGER, WARNING, CAUTION, NOTICE |
| `code` | string | 警告代码 | PWR-RTG-S001 |
| `message` | string | 警告信息 | - |
| `conditions` | string | 触发条件 | - |
| `consequences` | string | 后果 | - |
| `mitigation` | string | 缓解措施 | - |

**警告级别说明：**
- `DANGER` - 危险：将导致死亡或严重伤害
- `WARNING` - 警告：可能导致死亡或严重伤害
- `CAUTION` - 注意：可能导致轻微伤害或设备损坏
- `NOTICE` - 注意：重要信息

#### 1.9 程序字段 (procedures)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `procedure_id` | string | 程序ID |
| `title` | string | 程序标题 |
| `type` | enum | 程序类型 |
| `prerequisites` | array | 前置条件 |
| `steps` | array | 步骤列表 |

**程序类型枚举：**
- `installation` - 安装
- `operation` - 操作
- `maintenance` - 维护
- `emergency` - 紧急
- `calibration` - 校准
- `inspection` - 检查

#### 1.10 背景故事字段 (lore_snippet)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `title` | string | 故事标题 |
| `content` | string | 故事内容 |
| `source.type` | enum | 来源类型 |
| `source.author` | string | 作者 |
| `source.date` | string | 日期 |
| `source.classification` | string | 密级 |
| `unlock_condition` | string | 解锁条件 |
| `related_characters` | array | 相关角色 |

#### 1.11 难度等级字段 (difficulty_level)

| 字段名 | 类型 | 范围 | 描述 |
|-------|------|------|------|
| `technical` | integer | 1-5 | 技术难度 |
| `comprehension` | integer | 1-5 | 理解难度 |
| `required_clearance` | enum | - | 所需权限 |

**权限级别枚举：**
- `PUBLIC` - 公开
- `RESTRICTED` - 受限
- `CONFIDENTIAL` - 机密
- `SECRET` - 秘密
- `TOP_SECRET` - 绝密

#### 1.12 版本信息字段 (version_info)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `revision` | string | 修订版本 |
| `status` | enum | 文档状态 |
| `effective_date` | date | 生效日期 |
| `supersedes` | array | 替代的旧版本 |
| `change_summary` | string | 变更摘要 |
| `approver` | string | 批准人 |

**文档状态枚举：**
- `DRAFT` - 草稿
- `REVIEW` - 审核中
- `APPROVED` - 已批准
- `SUPERSEDED` - 已替代
- `OBSOLETE` - 已废弃

#### 1.13 元数据字段 (metadata)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `created_date` | datetime | 创建日期 |
| `last_modified` | datetime | 最后修改 |
| `author` | string | 作者 |
| `reviewer` | string | 审核人 |
| `department` | string | 部门 |
| `classification` | string | 密级 |
| `distribution` | string | 分发范围 |
| `page_count` | integer | 页数 |
| `word_count` | integer | 字数 |

#### 1.14 RAG索引字段 (rag_index)

| 字段名 | 类型 | 描述 |
|-------|------|------|
| `text_chunks` | array | 文本分块 |
| `embedding_vector` | array | 向量嵌入 |
| `searchable_text` | string | 可搜索文本 |

---

## 二、前端组件数据结构

### 2.1 文档树 (document_tree)

```
document_tree
├── tree_id
├── title
├── version
└── chapters[]
    ├── chapter_id
    ├── title
    ├── chapter_number
    ├── collapsed
    └── pages[]
        ├── page_id
        ├── title
        ├── page_number
        ├── entry_ref
        └── paragraphs[]
            ├── paragraph_id
            ├── type
            ├── content_ref
            ├── collapsible
            └── highlighted
```

### 2.2 搜索索引 (search_index)

```
search_index
├── index_version
├── last_updated
├── total_entries
├── categories[]
│   ├── category_code
│   ├── display_name
│   ├── entry_count
│   └── icon
├── entries[]
│   ├── entry_id
│   ├── title
│   ├── category
│   ├── abstract
│   ├── difficulty
│   ├── clearance
│   ├── keywords[]
│   ├── searchable_text
│   ├── text_chunks[]
│   └── embedding_id
└── filters
```

### 2.3 交互式图表 (interactive_diagram)

```
interactive_diagram
├── diagram_id
├── title
├── diagram_type
├── base_svg
├── view_config
│   ├── default_zoom
│   ├── min_zoom
│   ├── max_zoom
│   ├── pan_enabled
│   ├── zoom_enabled
│   └── layers[]
├── hotspots[]
│   ├── hotspot_id
│   ├── label
│   ├── shape
│   ├── coordinates
│   ├── tooltip
│   └── linked_entry
├── annotations[]
├── data_binding
└── interactions
```

---

## 三、数据类型定义

### 3.1 基础类型

| 类型 | 描述 | 示例 |
|-----|------|------|
| `string` | 字符串 | "MMOD-2100型RTG" |
| `integer` | 整数 | 110 |
| `number` | 浮点数 | 6.3 |
| `boolean` | 布尔值 | true |
| `array` | 数组 | ["tag1", "tag2"] |
| `object` | 对象 | {...} |
| `date` | 日期 | "2146-11-01" |
| `datetime` | 日期时间 | "2146-10-28T14:30:00Z" |

### 3.2 枚举类型

| 枚举名 | 可选值 |
|-------|-------|
| `CategoryPrimary` | PWR, CHEM, MECH, MED, ELEC, NAV, ENV, COM |
| `DiagramType` | schematic, cross_section, flow_chart, block_diagram, wiring_diagram, isometric, exploded_view, data_plot |
| `WarningLevel` | DANGER, WARNING, CAUTION, NOTICE |
| `ProcedureType` | installation, operation, maintenance, emergency, calibration, inspection |
| `ClearanceLevel` | PUBLIC, RESTRICTED, CONFIDENTIAL, SECRET, TOP_SECRET |
| `DocumentStatus` | DRAFT, REVIEW, APPROVED, SUPERSEDED, OBSOLETE |

---

## 四、数据验证规则

### 4.1 entry_id 格式

```
格式: [CATEGORY]-[SUBCATEGORY]-[NUMBER]-[REV]

正则表达式: ^[A-Z]{2,4}-[A-Z]{2,4}-\d{3,5}-REV[\dA-Z]$

示例:
- PWR-RTG-0042-REVC ✓
- CHEM-SYN-0187-REVB ✓
- PWR-001-REV1 ✗ (子分类太短)
```

### 4.2 必填字段验证

创建新条目时必须包含：
- `entry_id`
- `category.primary`
- `category.code`
- `title.full`
- `title.short`
- `technical_content.description.overview`
- `version_info.revision`
- `version_info.status`
- `metadata.created_date`
- `metadata.last_modified`
- `metadata.author`

### 4.3 数值范围验证

| 字段 | 最小值 | 最大值 |
|-----|-------|-------|
| `difficulty_level.technical` | 1 | 5 |
| `difficulty_level.comprehension` | 1 | 5 |
| `title.short` 长度 | 1 | 50 |

---

## 五、存储优化建议

### 5.1 数据分片策略

```
主文档集合 (technical_manual_entries)
├── 核心字段 (entry_id, category, title, metadata)
├── 内容字段 (technical_content.description)
└── 引用ID (diagrams_refs, formulas_refs)

独立集合
├── diagrams (图纸数据)
├── specifications (规格表数据)
├── formulas (公式数据)
├── procedures (程序数据)
└── lore_snippets (背景故事)
```

### 5.2 索引建议

```javascript
// MongoDB 索引配置
db.technical_manual_entries.createIndex({ "entry_id": 1 }, { unique: true });
db.technical_manual_entries.createIndex({ "category.primary": 1, "category.secondary": 1 });
db.technical_manual_entries.createIndex({ "tags": 1 });
db.technical_manual_entries.createIndex({ "keywords": "text" });
db.technical_manual_entries.createIndex({ "difficulty_level.technical": 1 });
db.technical_manual_entries.createIndex({ "version_info.status": 1 });
db.technical_manual_entries.createIndex({ "metadata.last_modified": -1 });
```

---

## 六、API 接口规范

### 6.1 条目查询接口

```
GET /api/manual/entries
参数:
  - category: 主分类过滤
  - difficulty: 难度等级过滤
  - tags: 标签过滤
  - search: 关键词搜索
  - page: 页码
  - limit: 每页数量

响应:
{
  "total": 156,
  "page": 1,
  "limit": 20,
  "entries": [...]
}
```

### 6.2 条目详情接口

```
GET /api/manual/entries/{entry_id}

响应:
{
  "entry_id": "PWR-RTG-0042-REVC",
  "title": {...},
  "technical_content": {...},
  ...
}
```

### 6.3 搜索接口

```
POST /api/manual/search
请求体:
{
  "query": "RTG 热电转换",
  "filters": {
    "categories": ["PWR"],
    "difficulty": [1, 2, 3]
  },
  "options": {
    "semantic_search": true,
    "highlight": true
  }
}
```
