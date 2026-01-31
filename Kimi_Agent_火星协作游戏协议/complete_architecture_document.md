# Project: CARGO - The Manual Engine 架构文档

> 技术资料库前端数据架构设计
> 版本: 1.0.0
> 日期: 2024

---

## 目录

1. [JSON Schema定义](#1-json-schema定义)
2. [示例条目（RTG）](#2-示例条目rtg)
3. [前端组件数据结构](#3-前端组件数据结构)
4. [RAG检索适配方案](#4-rag检索适配方案)
5. [字段说明文档](#5-字段说明文档)

---

## 1. JSON Schema定义

### 1.1 TechnicalManualEntry Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://project-cargo.game/schemas/technical-manual-entry.json",
  "title": "TechnicalManualEntry",
  "description": "Project: CARGO 技术资料库条目 - 模仿NASA技术手册风格的交互式文档数据结构",
  "type": "object",
  "required": [
    "entry_id",
    "category",
    "title",
    "technical_content",
    "version_info",
    "metadata"
  ],
  "properties": {
    "entry_id": {
      "type": "string",
      "description": "唯一标识符，格式: [CATEGORY]-[SUBCATEGORY]-[NUMBER]-[REV]",
      "pattern": "^[A-Z]{2,4}-[A-Z]{2,4}-\\d{3,5}-REV[\\dA-Z]$",
      "examples": [
        "PWR-RTG-0042-REVC",
        "CHEM-SYN-0187-REVB"
      ]
    },
    "legacy_id": {
      "type": "string",
      "description": "旧版文档编号（用于向后兼容）"
    },
    "category": {
      "type": "object",
      "required": [
        "primary",
        "code"
      ],
      "properties": {
        "primary": {
          "type": "string",
          "enum": [
            "PWR",
            "CHEM",
            "MECH",
            "MED",
            "ELEC",
            "NAV",
            "ENV",
            "COM"
          ],
          "description": "主分类: 动力/化学/机械/医疗/电子/导航/环境/通信"
        },
        "secondary": {
          "type": "string",
          "description": "子分类"
        },
        "code": {
          "type": "string",
          "description": "分类代码"
        },
        "display_name": {
          "type": "string",
          "description": "显示名称"
        }
      }
    },
    "title": {
      "type": "object",
      "required": [
        "full",
        "short"
      ],
      "properties": {
        "full": {
          "type": "string",
          "description": "完整标题"
        },
        "short": {
          "type": "string",
          "maxLength": 50,
          "description": "短标题（用于导航）"
        },
        "document_number": {
          "type": "string",
          "description": "文档编号"
        }
      }
    },
    "technical_content": {
      "type": "object",
      "required": [
        "description"
      ],
      "properties": {
        "abstract": {
          "type": "string",
          "description": "技术摘要（用于快速预览）"
        },
        "description": {
          "type": "object",
          "required": [
            "overview"
          ],
          "properties": {
            "overview": {
              "type": "string",
              "description": "概述"
            },
            "principles": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "工作原理段落列表"
            },
            "applications": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "应用场景"
            },
            "limitations": {
              "type": "array",
              "items": {
                "type": "string"
              },
              "description": "限制条件"
            }
          }
        },
        "diagrams": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "diagram_id",
              "type"
            ],
            "properties": {
              "diagram_id": {
                "type": "string",
                "description": "图纸唯一ID"
              },
              "type": {
                "type": "string",
                "enum": [
                  "schematic",
                  "cross_section",
                  "flow_chart",
                  "block_diagram",
                  "wiring_diagram",
                  "isometric",
                  "exploded_view",
                  "data_plot"
                ],
                "description": "图纸类型"
              },
              "title": {
                "type": "string",
                "description": "图纸标题"
              },
              "source": {
                "type": "object",
                "properties": {
                  "type": {
                    "type": "string",
                    "enum": [
                      "svg",
                      "png",
                      "jpg",
                      "interactive_svg",
                      "canvas"
                    ]
                  },
                  "url": {
                    "type": "string",
                    "format": "uri"
                  },
                  "svg_content": {
                    "type": "string",
                    "description": "内联SVG内容"
                  },
                  "interactive_config": {
                    "type": "object",
                    "description": "交互式图表配置"
                  }
                }
              },
              "annotations": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "id": {
                      "type": "string"
                    },
                    "label": {
                      "type": "string"
                    },
                    "description": {
                      "type": "string"
                    },
                    "position": {
                      "type": "object",
                      "properties": {
                        "x": {
                          "type": "number"
                        },
                        "y": {
                          "type": "number"
                        }
                      }
                    },
                    "hotspot": {
                      "type": "object",
                      "properties": {
                        "x": {
                          "type": "number"
                        },
                        "y": {
                          "type": "number"
                        },
                        "width": {
                          "type": "number"
                        },
                        "height": {
                          "type": "number"
                        }
                      }
                    }
                  }
                },
                "description": "图纸标注"
              },
              "callouts": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "id": {
                      "type": "string"
                    },
                    "text": {
                      "type": "string"
                    },
                    "related_part": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        },
        "specifications": {
          "type": "object",
          "properties": {
            "tables": {
              "type": "array",
              "items": {
                "type": "object",
                "required": [
                  "table_id",
                  "title",
                  "rows"
                ],
                "properties": {
                  "table_id": {
                    "type": "string"
                  },
                  "title": {
                    "type": "string"
                  },
                  "subtitle": {
                    "type": "string"
                  },
                  "columns": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "key": {
                          "type": "string"
                        },
                        "header": {
                          "type": "string"
                        },
                        "unit": {
                          "type": "string"
                        },
                        "data_type": {
                          "type": "string",
                          "enum": [
                            "string",
                            "number",
                            "boolean",
                            "range"
                          ]
                        }
                      }
                    }
                  },
                  "rows": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "additionalProperties": true
                    }
                  },
                  "notes": {
                    "type": "array",
                    "items": {
                      "type": "string"
                    }
                  }
                }
              }
            }
          }
        },
        "formulas": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "formula_id": {
                "type": "string"
              },
              "name": {
                "type": "string"
              },
              "latex": {
                "type": "string",
                "description": "LaTeX格式公式"
              },
              "plain_text": {
                "type": "string",
                "description": "纯文本描述"
              },
              "variables": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "symbol": {
                      "type": "string"
                    },
                    "name": {
                      "type": "string"
                    },
                    "unit": {
                      "type": "string"
                    },
                    "description": {
                      "type": "string"
                    }
                  }
                }
              },
              "conditions": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        },
        "safety_warnings": {
          "type": "array",
          "items": {
            "type": "object",
            "required": [
              "level",
              "message"
            ],
            "properties": {
              "level": {
                "type": "string",
                "enum": [
                  "DANGER",
                  "WARNING",
                  "CAUTION",
                  "NOTICE"
                ],
                "description": "警告级别"
              },
              "code": {
                "type": "string"
              },
              "message": {
                "type": "string"
              },
              "conditions": {
                "type": "string"
              },
              "consequences": {
                "type": "string"
              },
              "mitigation": {
                "type": "string"
              }
            }
          }
        },
        "procedures": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "procedure_id": {
                "type": "string"
              },
              "title": {
                "type": "string"
              },
              "type": {
                "type": "string",
                "enum": [
                  "installation",
                  "operation",
                  "maintenance",
                  "emergency",
                  "calibration",
                  "inspection"
                ]
              },
              "steps": {
                "type": "array",
                "items": {
                  "type": "object",
                  "properties": {
                    "step_number": {
                      "type": "integer"
                    },
                    "instruction": {
                      "type": "string"
                    },
                    "caution_refs": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    },
                    "tool_required": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      }
                    },
                    "verification": {
                      "type": "string"
                    }
                  }
                }
              },
              "prerequisites": {
                "type": "array",
                "items": {
                  "type": "string"
                }
              }
            }
          }
        }
      }
    },
    "lore_snippet": {
      "type": "object",
      "properties": {
        "title": {
          "type": "string"
        },
        "content": {
          "type": "string"
        },
        "source": {
          "type": "object",
          "properties": {
            "type": {
              "type": "string",
              "enum": [
                "log_entry",
                "memo",
                "transcript",
                "note",
                "archive"
              ]
            },
            "author": {
              "type": "string"
            },
            "date": {
              "type": "string"
            },
            "classification": {
              "type": "string"
            }
          }
        },
        "unlock_condition": {
          "type": "string"
        },
        "related_characters": {
          "type": "array",
          "items": {
            "type": "string"
          }
        }
      }
    },
    "tags": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "检索标签"
    },
    "keywords": {
      "type": "array",
      "items": {
        "type": "string"
      },
      "description": "关键词（用于搜索）"
    },
    "difficulty_level": {
      "type": "object",
      "properties": {
        "technical": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5,
          "description": "技术难度 1-5"
        },
        "comprehension": {
          "type": "integer",
          "minimum": 1,
          "maximum": 5,
          "description": "理解难度 1-5"
        },
        "required_clearance": {
          "type": "string",
          "enum": [
            "PUBLIC",
            "RESTRICTED",
            "CONFIDENTIAL",
            "SECRET",
            "TOP_SECRET"
          ]
        }
      }
    },
    "related_entries": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "entry_id": {
            "type": "string"
          },
          "relationship": {
            "type": "string",
            "enum": [
              "prerequisite",
              "supersedes",
              "component_of",
              "requires",
              "references",
              "similar_to",
              "contrasts_with"
            ]
          },
          "description": {
            "type": "string"
          }
        }
      }
    },
    "version_info": {
      "type": "object",
      "required": [
        "revision",
        "status"
      ],
      "properties": {
        "revision": {
          "type": "string"
        },
        "status": {
          "type": "string",
          "enum": [
            "DRAFT",
            "REVIEW",
            "APPROVED",
            "SUPERSEDED",
            "OBSOLETE"
          ]
        },
        "effective_date": {
          "type": "string",
          "format": "date"
        },
        "supersedes": {
          "type": "array",
          "items": {
            "type": "string"
          }
        },
        "change_summary": {
          "type": "string"
        },
        "approver": {
          "type": "string"
        }
      }
    },
    "metadata": {
      "type": "object",
      "required": [
        "created_date",
        "last_modified",
        "author"
      ],
      "properties": {
        "created_date": {
          "type": "string",
          "format": "date-time"
        },
        "last_modified": {
          "type": "string",
          "format": "date-time"
        },
        "author": {
          "type": "string"
        },
        "reviewer": {
          "type": "string"
        },
        "department": {
          "type": "string"
        },
        "classification": {
          "type": "string"
        },
        "distribution": {
          "type": "string"
        },
        "page_count": {
          "type": "integer"
        },
        "word_count": {
          "type": "integer"
        }
      }
    },
    "rag_index": {
      "type": "object",
      "description": "RAG检索专用索引数据",
      "properties": {
        "text_chunks": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "chunk_id": {
                "type": "string"
              },
              "content": {
                "type": "string"
              },
              "chunk_type": {
                "type": "string",
                "enum": [
                  "title",
                  "abstract",
                  "body",
                  "specs",
                  "procedure",
                  "lore"
                ]
              },
              "embedding_id": {
                "type": "string"
              },
              "token_count": {
                "type": "integer"
              }
            }
          }
        },
        "embedding_vector": {
          "type": "array",
          "items": {
            "type": "number"
          },
          "description": "向量嵌入（运行时填充）"
        },
        "searchable_text": {
          "type": "string",
          "description": "合并的可搜索文本"
        }
      }
    }
  }
}
```

---

## 2. 示例条目（RTG）

### 2.1 RTG条目完整数据

```json
{
  "entry_id": "PWR-RTG-0042-REVC",
  "legacy_id": "MMOD-RTG-PLUTONIUM-2100-REV3",
  "category": {
    "primary": "PWR",
    "secondary": "放射性同位素发电",
    "code": "PWR-RTG",
    "display_name": "动力系统 - 放射性同位素热电机"
  },
  "title": {
    "full": "MMOD-2100型 多任务放射性同位素热电机系统技术手册",
    "short": "MMOD-2100 RTG系统",
    "document_number": "TM-PWR-RTG-0042"
  },
  "technical_content": {
    "abstract": "本文档详细说明了MMOD-2100型多任务放射性同位素热电机(RTG)的设计规格、操作程序和安全要求。该设备采用钚-238二氧化物燃料芯块，设计寿命不少于17年，额定电功率输出110W。本手册适用于深空探测、极地科考站及密闭环境生命维持系统的电力供应应用。",
    "description": {
      "overview": "MMOD-2100型RTG是一种基于塞贝克效应的热电转换装置，通过放射性同位素衰变产生的热能直接转换为电能。该设备无需运动部件，具有极高的可靠性，适用于无法使用太阳能电池板或传统燃料发电机的极端环境。\n\n本系统由以下主要子系统组成：\n- 通用热源(GPHS)模块：包含钚-238燃料芯块\n- 热电转换模块：硅锗(SiGe)热电偶阵列\n- 散热系统：铝制散热鳍片组\n- 多层绝缘(MLI)外壳：提供热保护和辐射屏蔽\n- 电气接口：标准28V直流输出\n\n本设备符合NASA-STD-8719.23放射性同位素动力系统安全标准，并已通过DOE批准用于空间任务应用。",
      "principles": [
        "塞贝克效应原理：当两种不同导体或半导体构成回路且两个接点处于不同温度时，回路中会产生热电势。MMOD-2100采用P型与N型硅锗合金热电偶，热端温度维持约1273K，冷端温度约573K，产生约700mV的单对热电偶输出电压。",
        "热源设计：通用热源(GPHS)模块包含4个独立的燃料包壳，每个包壳内有2个钚-238二氧化物燃料芯块。燃料芯块采用烧结工艺制成，直径约50mm，高度约50mm，初始热功率约62.5W。燃料包壳由铱合金制成，可承受再入大气层时的极端条件。",
        "热电转换效率：系统总热电转换效率约为6.3%，这是由硅锗材料在操作温度范围内的性能特性决定的。虽然效率较低，但系统的无运动部件设计提供了无与伦比的长期可靠性。",
        "功率衰减：由于钚-238的半衰期为87.7年，系统电功率输出将以约0.787%/年的速率衰减。任务规划时必须考虑此衰减特性，确保任务末期仍有足够的功率余量。"
      ],
      "applications": [
        "深空探测器主电源：适用于超出木星轨道、太阳辐射不足以支持太阳能板供电的任务",
        "极地科考站辅助电源：在极夜期间提供持续电力供应",
        "地下设施生命维持系统：为密闭环境提供可靠电力",
        "行星表面着陆器：在尘暴频繁或光照条件恶劣的行星表面",
        "应急备用电源：关键基础设施的备用电力系统"
      ],
      "limitations": [
        "功率质量比限制：RTG系统的比功率约为5.4 W/kg，远低于太阳能电池板或燃料电池",
        "热管理要求：系统运行时产生大量废热，需要有效的散热设计",
        "辐射屏蔽需求：虽然外壳提供辐射屏蔽，但在人员接近区域需要额外防护措施",
        "发射前审批：由于涉及核材料，发射前需要获得核管理委员会(NRC)和国务院的批准",
        "成本因素：燃料生产和系统制造成本高昂，仅适用于高价值任务"
      ]
    },
    "diagrams": [
      {
        "diagram_id": "PWR-RTG-0042-D001",
        "type": "cross_section",
        "title": "图1：MMOD-2100 RTG 剖面图",
        "source": {
          "type": "interactive_svg",
          "url": "/assets/diagrams/pwr-rtg-0042-d001.svg",
          "interactive_config": {
            "zoom_levels": [
              0.5,
              1.0,
              1.5,
              2.0
            ],
            "hotspots_enabled": true,
            "layers": [
              "structure",
              "thermal",
              "electrical"
            ]
          }
        },
        "annotations": [
          {
            "id": "A1",
            "label": "1",
            "description": "通用热源(GPHS)模块 - 包含钚-238燃料芯块",
            "position": {
              "x": 50,
              "y": 50
            },
            "hotspot": {
              "x": 45,
              "y": 45,
              "width": 20,
              "height": 20
            }
          },
          {
            "id": "A2",
            "label": "2",
            "description": "热电偶阵列 - 312对SiGe热电偶",
            "position": {
              "x": 80,
              "y": 50
            },
            "hotspot": {
              "x": 75,
              "y": 40,
              "width": 15,
              "height": 25
            }
          },
          {
            "id": "A3",
            "label": "3",
            "description": "铝制散热鳍片 - 提供冷端散热",
            "position": {
              "x": 110,
              "y": 50
            },
            "hotspot": {
              "x": 100,
              "y": 30,
              "width": 25,
              "height": 40
            }
          },
          {
            "id": "A4",
            "label": "4",
            "description": "多层绝缘(MLI)外壳 - 热保护和辐射屏蔽",
            "position": {
              "x": 30,
              "y": 80
            },
            "hotspot": {
              "x": 20,
              "y": 20,
              "width": 100,
              "height": 80
            }
          },
          {
            "id": "A5",
            "label": "5",
            "description": "电气输出接口 - 28V DC标准输出",
            "position": {
              "x": 120,
              "y": 90
            },
            "hotspot": {
              "x": 115,
              "y": 85,
              "width": 15,
              "height": 15
            }
          }
        ],
        "callouts": [
          {
            "id": "C1",
            "text": "燃料芯块直径：50.8mm",
            "related_part": "A1"
          },
          {
            "id": "C2",
            "text": "热电偶间距：3.2mm",
            "related_part": "A2"
          },
          {
            "id": "C3",
            "text": "散热鳍片总面积：1.2m²",
            "related_part": "A3"
          }
        ]
      },
      {
        "diagram_id": "PWR-RTG-0042-D002",
        "type": "schematic",
        "title": "图2：热电转换电路原理图",
        "source": {
          "type": "svg",
          "url": "/assets/diagrams/pwr-rtg-0042-d002.svg"
        },
        "annotations": [
          {
            "id": "B1",
            "label": "P/N",
            "description": "P型/N型热电偶对",
            "position": {
              "x": 60,
              "y": 40
            }
          },
          {
            "id": "B2",
            "label": "OUT",
            "description": "28V DC输出端子",
            "position": {
              "x": 120,
              "y": 50
            }
          }
        ]
      },
      {
        "diagram_id": "PWR-RTG-0042-D003",
        "type": "data_plot",
        "title": "图3：功率输出衰减曲线（BOL至EOL）",
        "source": {
          "type": "interactive_svg",
          "url": "/assets/diagrams/pwr-rtg-0042-d003.svg",
          "interactive_config": {
            "data_points": true,
            "tooltip_enabled": true
          }
        }
      }
    ],
    "specifications": {
      "tables": [
        {
          "table_id": "T1",
          "title": "表1：电气性能规格",
          "subtitle": "标准测试条件：环境温度293K，真空环境",
          "columns": [
            {
              "key": "parameter",
              "header": "参数",
              "data_type": "string"
            },
            {
              "key": "value",
              "header": "数值",
              "data_type": "string"
            },
            {
              "key": "unit",
              "header": "单位",
              "data_type": "string"
            },
            {
              "key": "condition",
              "header": "条件",
              "data_type": "string"
            }
          ],
          "rows": [
            {
              "parameter": "额定电功率输出",
              "value": "110",
              "unit": "W",
              "condition": "BOL, 真空"
            },
            {
              "parameter": "最小电功率输出",
              "value": "95",
              "unit": "W",
              "condition": "EOL(17年), 真空"
            },
            {
              "parameter": "输出电压",
              "value": "28±2",
              "unit": "V DC",
              "condition": "额定负载"
            },
            {
              "parameter": "输出电流",
              "value": "3.93",
              "unit": "A",
              "condition": "额定功率"
            },
            {
              "parameter": "内部电阻",
              "value": "5.2",
              "unit": "Ω",
              "condition": "25°C"
            },
            {
              "parameter": "功率衰减率",
              "value": "0.787",
              "unit": "%/年",
              "condition": "标称值"
            },
            {
              "parameter": "热电转换效率",
              "value": "6.3",
              "unit": "%",
              "condition": "设计值"
            }
          ],
          "notes": [
            "BOL = Beginning of Life (寿命初期)",
            "EOL = End of Life (寿命末期)",
            "所有数值为设计目标值，实际性能可能有±5%偏差"
          ]
        },
        {
          "table_id": "T2",
          "title": "表2：热性能规格",
          "columns": [
            {
              "key": "parameter",
              "header": "参数",
              "data_type": "string"
            },
            {
              "key": "value",
              "header": "数值",
              "unit": "单位",
              "data_type": "string"
            }
          ],
          "rows": [
            {
              "parameter": "燃料初始热功率",
              "value": "2000",
              "unit": "W"
            },
            {
              "parameter": "热端温度",
              "value": "1273",
              "unit": "K"
            },
            {
              "parameter": "冷端温度",
              "value": "573",
              "unit": "K"
            },
            {
              "parameter": "温差",
              "value": "700",
              "unit": "K"
            },
            {
              "parameter": "废热功率",
              "value": "1890",
              "unit": "W"
            },
            {
              "parameter": "表面温度(运行中)",
              "value": "423-473",
              "unit": "K"
            },
            {
              "parameter": "表面温度(储存)",
              "value": "<333",
              "unit": "K"
            }
          ]
        },
        {
          "table_id": "T3",
          "title": "表3：物理规格",
          "columns": [
            {
              "key": "parameter",
              "header": "参数",
              "data_type": "string"
            },
            {
              "key": "value",
              "header": "数值",
              "unit": "单位",
              "data_type": "string"
            }
          ],
          "rows": [
            {
              "parameter": "总长度",
              "value": "1130",
              "unit": "mm"
            },
            {
              "parameter": "最大直径",
              "value": "420",
              "unit": "mm"
            },
            {
              "parameter": "总质量",
              "value": "20.4",
              "unit": "kg"
            },
            {
              "parameter": "燃料质量(Pu-238)",
              "value": "4.8",
              "unit": "kg"
            },
            {
              "parameter": "比功率",
              "value": "5.4",
              "unit": "W/kg"
            },
            {
              "parameter": "外壳材料",
              "value": "铝-锂合金",
              "unit": "-"
            },
            {
              "parameter": "散热鳍片材料",
              "value": "6061-T6铝",
              "unit": "-"
            }
          ]
        }
      ]
    },
    "formulas": [
      {
        "formula_id": "F1",
        "name": "塞贝克电压",
        "latex": "V = n \\cdot \u0007lpha \\cdot \\Delta T",
        "plain_text": "V = n × α × ΔT",
        "variables": [
          {
            "symbol": "V",
            "name": "输出电压",
            "unit": "V",
            "description": "热电偶阵列总输出电压"
          },
          {
            "symbol": "n",
            "name": "热电偶对数",
            "unit": "-",
            "description": "串联的热电偶对数量"
          },
          {
            "symbol": "α",
            "name": "塞贝克系数",
            "unit": "V/K",
            "description": "SiGe材料塞贝克系数，约150μV/K"
          },
          {
            "symbol": "ΔT",
            "name": "温差",
            "unit": "K",
            "description": "热端与冷端温度差"
          }
        ],
        "conditions": [
          "适用于稳态操作条件",
          "假设热电偶性能均匀"
        ]
      },
      {
        "formula_id": "F2",
        "name": "放射性衰变功率衰减",
        "latex": "P(t) = P_0 \\cdot e^{-\\lambda t} = P_0 \\cdot 2^{-t/t_{1/2}}",
        "plain_text": "P(t) = P₀ × e^(-λt) = P₀ × 2^(-t/t₁/₂)",
        "variables": [
          {
            "symbol": "P(t)",
            "name": "t时刻功率",
            "unit": "W",
            "description": "时间t时的功率输出"
          },
          {
            "symbol": "P₀",
            "name": "初始功率",
            "unit": "W",
            "description": "t=0时的功率输出"
          },
          {
            "symbol": "λ",
            "name": "衰变常数",
            "unit": "1/年",
            "description": "λ = ln(2)/t₁/₂"
          },
          {
            "symbol": "t",
            "name": "时间",
            "unit": "年",
            "description": "经过的时间"
          },
          {
            "symbol": "t₁/₂",
            "name": "半衰期",
            "unit": "年",
            "description": "Pu-238半衰期为87.7年"
          }
        ],
        "conditions": [
          "仅考虑放射性衰变因素",
          "忽略热电偶老化效应"
        ]
      },
      {
        "formula_id": "F3",
        "name": "热电转换效率",
        "latex": "\\eta = \frac{P_{elec}}{P_{thermal}} \times 100\\%",
        "plain_text": "η = (P_电 / P_热) × 100%",
        "variables": [
          {
            "symbol": "η",
            "name": "转换效率",
            "unit": "%",
            "description": "热电转换效率百分比"
          },
          {
            "symbol": "P_电",
            "name": "电功率输出",
            "unit": "W",
            "description": "有效电功率输出"
          },
          {
            "symbol": "P_热",
            "name": "热功率输入",
            "unit": "W",
            "description": "燃料衰变产生的热功率"
          }
        ],
        "conditions": [
          "稳态操作条件"
        ]
      }
    ],
    "safety_warnings": [
      {
        "level": "DANGER",
        "code": "PWR-RTG-S001",
        "message": "放射性材料暴露风险 - 未经授权打开外壳将导致致命辐射暴露",
        "conditions": "外壳完整性受损、未经授权拆解",
        "consequences": "急性辐射综合征，可能致死",
        "mitigation": "仅由持证技术人员在授权设施内操作；佩戴剂量计；使用远程操作设备"
      },
      {
        "level": "WARNING",
        "code": "PWR-RTG-S002",
        "message": "高温表面 - 运行期间外壳表面温度可达200°C",
        "conditions": "设备运行中、启动后2小时内",
        "consequences": "严重烧伤",
        "mitigation": "保持安全距离；佩戴隔热手套；等待充分冷却后再接触"
      },
      {
        "level": "CAUTION",
        "code": "PWR-RTG-S003",
        "message": "静电敏感设备 - 热电偶阵列对静电放电敏感",
        "conditions": "电气连接操作期间",
        "consequences": "设备损坏、性能下降",
        "mitigation": "使用接地腕带；在防静电工作台上操作"
      },
      {
        "level": "NOTICE",
        "code": "PWR-RTG-S004",
        "message": "大气再入安全 - 燃料包壳设计可承受再入条件，但不应故意测试此功能",
        "conditions": "发射失败场景",
        "consequences": "潜在的放射性物质释放",
        "mitigation": "遵循发射安全协议；燃料包壳通过全向撞击测试验证"
      }
    ],
    "procedures": [
      {
        "procedure_id": "PROC-001",
        "title": "启动前检查程序",
        "type": "operation",
        "prerequisites": [
          "持有RTG操作认证",
          "佩戴个人剂量计",
          "确认环境辐射水平正常",
          "检查所有安全联锁功能正常"
        ],
        "steps": [
          {
            "step_number": 1,
            "instruction": "目视检查设备外壳完整性，确认无可见损伤、变形或腐蚀",
            "caution_refs": [
              "PWR-RTG-S002"
            ],
            "verification": "记录检查结果，拍照存档"
          },
          {
            "step_number": 2,
            "instruction": "使用便携式辐射监测仪测量设备表面剂量率",
            "caution_refs": [],
            "verification": "剂量率应在0.5-2.0 mSv/h范围内"
          },
          {
            "step_number": 3,
            "instruction": "检查电气接口连接器，确认无氧化、污染或物理损伤",
            "caution_refs": [
              "PWR-RTG-S003"
            ],
            "tool_required": [
              "放大镜",
              "清洁布"
            ],
            "verification": "连接器针脚应清洁、无变形"
          },
          {
            "step_number": 4,
            "instruction": "测量开路电压，确认热电偶阵列功能正常",
            "caution_refs": [],
            "tool_required": [
              "数字万用表"
            ],
            "verification": "开路电压应在22-26V范围内"
          },
          {
            "step_number": 5,
            "instruction": "连接负载电阻，测量带载输出电压和电流",
            "caution_refs": [],
            "tool_required": [
              "电子负载",
              "数据记录仪"
            ],
            "verification": "输出功率应在额定值的±10%范围内"
          }
        ]
      },
      {
        "procedure_id": "PROC-002",
        "title": "紧急停机程序",
        "type": "emergency",
        "prerequisites": [
          "发现异常情况或接到停机指令"
        ],
        "steps": [
          {
            "step_number": 1,
            "instruction": "立即断开所有电气负载",
            "caution_refs": [],
            "verification": "确认负载电流读数为零"
          },
          {
            "step_number": 2,
            "instruction": "记录停机时间和当时的运行参数",
            "caution_refs": [],
            "verification": "填写紧急停机报告表"
          },
          {
            "step_number": 3,
            "instruction": "疏散所有非必要人员至安全距离外（至少10米）",
            "caution_refs": [
              "PWR-RTG-S001"
            ],
            "verification": "确认人员清点完成"
          },
          {
            "step_number": 4,
            "instruction": "通知辐射安全官员和任务控制中心",
            "caution_refs": [],
            "verification": "等待进一步指示"
          }
        ]
      }
    ]
  },
  "lore_snippet": {
    "title": "任务日志摘录 #RTG-2100-047",
    "content": "[加密级别：RESTRICTED]\n\n日期：2147年3月15日\n记录者：工程师 M. Vasquez\n\n这是我们在K-79矿站的第147天。RTG-2（序列号PWR-RTG-0042）已经稳定运行了超过四个月，但昨天发生了一件奇怪的事。\n\n凌晨0300，我正在值班室监控电力系统。突然，RTG-2的输出功率出现了0.3%的异常波动。这在理论上是不可能的——钚的衰变是恒定的，热电偶没有活动部件。我检查了所有传感器，它们都显示正常。\n\n更奇怪的是，波动持续了正好47分钟，然后恢复了正常。47分钟——这个数字让我想起了那个古老的传说。老矿工们说，这个矿脉在被人类发现之前就已经存在了某种...东西。某种沉睡的东西。\n\n我查看了历史数据，发现同样的47分钟波动模式在过去三个月内出现了三次，每次都间隔大约28天。就像某种周期性的信号。\n\n我把这些数据报告给了站点主管，他只是让我\"继续监控\"，但他的眼神告诉我，他知道些什么。\n\n今天我在RTG-2附近工作时，听到了一种奇怪的声音。不是机械的声音，更像是...低语。可能是我的幻觉吧。这里的孤立环境会让人产生各种奇怪的想法。\n\n但有一件事我很确定：当我靠近RTG-2时，我的剂量计读数比平时高了0.02 mSv。这还在安全范围内，但...它不应该波动。\n\n明天我要检查一下RTG-2周围的辐射屏蔽。也许只是某个地方的铅板松动了。\n\n[日志结束]",
    "source": {
      "type": "log_entry",
      "author": "M. Vasquez",
      "date": "2147-03-15",
      "classification": "RESTRICTED"
    },
    "unlock_condition": "阅读RTG技术手册后自动解锁",
    "related_characters": [
      "M. Vasquez",
      "站点主管",
      "老矿工"
    ]
  },
  "tags": [
    "RTG",
    "放射性同位素",
    "钚-238",
    "热电转换",
    "深空电源",
    "核电池",
    "塞贝克效应",
    "GPHS",
    "硅锗热电偶",
    "长寿命电源"
  ],
  "keywords": [
    "radioisotope thermoelectric generator",
    "plutonium-238",
    "thermoelectric conversion",
    "Seebeck effect",
    "deep space power",
    "nuclear battery",
    "SiGe thermocouple",
    "GPHS module",
    "放射性同位素热电机",
    "钚燃料"
  ],
  "difficulty_level": {
    "technical": 4,
    "comprehension": 3,
    "required_clearance": "RESTRICTED"
  },
  "related_entries": [
    {
      "entry_id": "PWR-FC-0015-REVA",
      "relationship": "similar_to",
      "description": "燃料电池系统 - 另一种深空电源方案"
    },
    {
      "entry_id": "CHEM-PLT-0089-REVB",
      "relationship": "references",
      "description": "钚-238化学性质与安全处理"
    },
    {
      "entry_id": "ENV-RAD-0033-REVC",
      "relationship": "prerequisite",
      "description": "辐射防护基础"
    },
    {
      "entry_id": "PWR-SOL-0201-REVA",
      "relationship": "contrasts_with",
      "description": "太阳能电池阵列 - 对比电源系统"
    }
  ],
  "version_info": {
    "revision": "REVC",
    "status": "APPROVED",
    "effective_date": "2146-11-01",
    "supersedes": [
      "PWR-RTG-0042-REVB"
    ],
    "change_summary": "更新了安全警告PWR-RTG-S001；增加了紧急停机程序PROC-002；修订了功率衰减曲线数据",
    "approver": "Dr. Elena Rostova, 首席工程师"
  },
  "metadata": {
    "created_date": "2145-06-15T09:00:00Z",
    "last_modified": "2146-10-28T14:30:00Z",
    "author": "Dr. James Chen",
    "reviewer": "Dr. Elena Rostova",
    "department": "动力系统工程部",
    "classification": "RESTRICTED",
    "distribution": "授权人员",
    "page_count": 42,
    "word_count": 15847
  },
  "rag_index": {
    "text_chunks": [
      {
        "chunk_id": "PWR-RTG-0042-C001",
        "content": "MMOD-2100型RTG是一种基于塞贝克效应的热电转换装置，通过放射性同位素衰变产生的热能直接转换为电能。",
        "chunk_type": "abstract",
        "token_count": 45
      },
      {
        "chunk_id": "PWR-RTG-0042-C002",
        "content": "塞贝克效应原理：当两种不同导体或半导体构成回路且两个接点处于不同温度时，回路中会产生热电势。",
        "chunk_type": "body",
        "token_count": 38
      }
    ],
    "searchable_text": "MMOD-2100 RTG 放射性同位素热电机 钚-238 硅锗热电偶 塞贝克效应 深空电源"
  }
}
```

---

## 3. 前端组件数据结构

### 3.1 组件Schema定义

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://project-cargo.game/schemas/frontend-components.json",
  "title": "FrontendComponentData",
  "description": "Project: CARGO 前端组件数据结构 - 用于渲染交互式技术文档",
  "document_tree": {
    "type": "object",
    "description": "文档树结构 - 章节-页面-段落层级",
    "properties": {
      "tree_id": {
        "type": "string"
      },
      "title": {
        "type": "string"
      },
      "version": {
        "type": "string"
      },
      "chapters": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "chapter_id": {
              "type": "string"
            },
            "title": {
              "type": "string"
            },
            "chapter_number": {
              "type": "string"
            },
            "collapsed": {
              "type": "boolean"
            },
            "pages": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "page_id": {
                    "type": "string"
                  },
                  "title": {
                    "type": "string"
                  },
                  "page_number": {
                    "type": "string"
                  },
                  "entry_ref": {
                    "type": "string"
                  },
                  "paragraphs": {
                    "type": "array",
                    "items": {
                      "type": "object",
                      "properties": {
                        "paragraph_id": {
                          "type": "string"
                        },
                        "type": {
                          "type": "string",
                          "enum": [
                            "text",
                            "heading",
                            "list",
                            "table",
                            "diagram",
                            "formula",
                            "warning",
                            "code"
                          ]
                        },
                        "content_ref": {
                          "type": "string"
                        },
                        "collapsible": {
                          "type": "boolean"
                        },
                        "highlighted": {
                          "type": "boolean"
                        }
                      }
                    }
                  }
                }
              }
            }
          }
        }
      }
    }
  },
  "search_index": {
    "type": "object",
    "description": "搜索索引数据结构",
    "properties": {
      "index_version": {
        "type": "string"
      },
      "last_updated": {
        "type": "string",
        "format": "date-time"
      },
      "total_entries": {
        "type": "integer"
      },
      "categories": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "category_code": {
              "type": "string"
            },
            "display_name": {
              "type": "string"
            },
            "entry_count": {
              "type": "integer"
            },
            "icon": {
              "type": "string"
            }
          }
        }
      },
      "entries": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "entry_id": {
              "type": "string"
            },
            "title": {
              "type": "string"
            },
            "category": {
              "type": "string"
            },
            "abstract": {
              "type": "string"
            },
            "difficulty": {
              "type": "integer"
            },
            "clearance": {
              "type": "string"
            },
            "keywords": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "searchable_text": {
              "type": "string"
            },
            "text_chunks": {
              "type": "array",
              "items": {
                "type": "object",
                "properties": {
                  "chunk_id": {
                    "type": "string"
                  },
                  "text": {
                    "type": "string"
                  },
                  "weight": {
                    "type": "number"
                  },
                  "section": {
                    "type": "string"
                  }
                }
              }
            },
            "embedding_id": {
              "type": "string"
            }
          }
        }
      },
      "filters": {
        "type": "object",
        "properties": {
          "categories": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "difficulty_levels": {
            "type": "array",
            "items": {
              "type": "integer"
            }
          },
          "clearance_levels": {
            "type": "array",
            "items": {
              "type": "string"
            }
          },
          "tags": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  },
  "interactive_diagram": {
    "type": "object",
    "description": "交互式图表数据结构",
    "properties": {
      "diagram_id": {
        "type": "string"
      },
      "title": {
        "type": "string"
      },
      "diagram_type": {
        "type": "string",
        "enum": [
          "schematic",
          "cross_section",
          "flow_chart",
          "block_diagram",
          "wiring_diagram",
          "isometric",
          "exploded_view",
          "data_plot",
          "interactive_3d"
        ]
      },
      "base_svg": {
        "type": "string"
      },
      "view_config": {
        "type": "object",
        "properties": {
          "default_zoom": {
            "type": "number"
          },
          "min_zoom": {
            "type": "number"
          },
          "max_zoom": {
            "type": "number"
          },
          "pan_enabled": {
            "type": "boolean"
          },
          "zoom_enabled": {
            "type": "boolean"
          },
          "layers": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "layer_id": {
                  "type": "string"
                },
                "name": {
                  "type": "string"
                },
                "visible": {
                  "type": "boolean"
                },
                "opacity": {
                  "type": "number"
                },
                "selectable": {
                  "type": "boolean"
                }
              }
            }
          }
        }
      },
      "hotspots": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "hotspot_id": {
              "type": "string"
            },
            "label": {
              "type": "string"
            },
            "shape": {
              "type": "string",
              "enum": [
                "rect",
                "circle",
                "polygon"
              ]
            },
            "coordinates": {
              "type": "object"
            },
            "tooltip": {
              "type": "string"
            },
            "detail_content": {
              "type": "string"
            },
            "linked_entry": {
              "type": "string"
            },
            "highlight_color": {
              "type": "string"
            },
            "animation": {
              "type": "string"
            }
          }
        }
      },
      "annotations": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "annotation_id": {
              "type": "string"
            },
            "text": {
              "type": "string"
            },
            "position": {
              "type": "object"
            },
            "leader_line": {
              "type": "boolean"
            },
            "style": {
              "type": "string"
            }
          }
        }
      },
      "data_binding": {
        "type": "object",
        "properties": {
          "source_entry": {
            "type": "string"
          },
          "dynamic_elements": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "element_id": {
                  "type": "string"
                },
                "data_path": {
                  "type": "string"
                },
                "display_format": {
                  "type": "string"
                },
                "update_trigger": {
                  "type": "string"
                }
              }
            }
          }
        }
      },
      "interactions": {
        "type": "object",
        "properties": {
          "on_click": {
            "type": "string"
          },
          "on_hover": {
            "type": "string"
          },
          "on_double_click": {
            "type": "string"
          },
          "context_menu": {
            "type": "array"
          }
        }
      }
    }
  },
  "page_render_state": {
    "type": "object",
    "description": "页面渲染状态管理",
    "properties": {
      "current_entry": {
        "type": "string"
      },
      "current_chapter": {
        "type": "string"
      },
      "current_page": {
        "type": "string"
      },
      "scroll_position": {
        "type": "number"
      },
      "expanded_sections": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "highlighted_terms": {
        "type": "array",
        "items": {
          "type": "string"
        }
      },
      "active_filters": {
        "type": "object",
        "properties": {
          "category": {
            "type": "string"
          },
          "difficulty": {
            "type": "integer"
          },
          "clearance": {
            "type": "string"
          },
          "tags": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      },
      "reading_progress": {
        "type": "object",
        "properties": {
          "percentage": {
            "type": "number"
          },
          "time_spent": {
            "type": "integer"
          },
          "sections_read": {
            "type": "array",
            "items": {
              "type": "string"
            }
          }
        }
      }
    }
  },
  "user_annotations": {
    "type": "object",
    "description": "用户书签和笔记数据",
    "properties": {
      "bookmarks": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "bookmark_id": {
              "type": "string"
            },
            "entry_id": {
              "type": "string"
            },
            "location": {
              "type": "string"
            },
            "title": {
              "type": "string"
            },
            "created_at": {
              "type": "string"
            },
            "color": {
              "type": "string"
            }
          }
        }
      },
      "notes": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "note_id": {
              "type": "string"
            },
            "entry_id": {
              "type": "string"
            },
            "location": {
              "type": "string"
            },
            "content": {
              "type": "string"
            },
            "created_at": {
              "type": "string"
            },
            "updated_at": {
              "type": "string"
            },
            "is_private": {
              "type": "boolean"
            }
          }
        }
      }
    }
  }
}
```

---

## 4. RAG检索适配方案

### 4.1 RAG Adapter Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://project-cargo.game/schemas/rag-adapter.json",
  "title": "RAGAdapter",
  "description": "Project: CARGO RAG检索适配方案",
  "text_chunking": {
    "type": "object",
    "description": "文本分块策略配置",
    "properties": {
      "strategy": {
        "type": "string",
        "enum": [
          "semantic",
          "fixed_size",
          "hierarchical",
          "hybrid"
        ],
        "description": "分块策略类型"
      },
      "config": {
        "type": "object",
        "properties": {
          "chunk_size": {
            "type": "integer",
            "default": 512,
            "description": "每个文本块的token数量"
          },
          "chunk_overlap": {
            "type": "integer",
            "default": 50,
            "description": "相邻块之间的重叠token数"
          },
          "semantic_boundaries": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "语义边界标记（如段落标题）"
          },
          "hierarchy_levels": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "level": {
                  "type": "integer"
                },
                "chunk_size": {
                  "type": "integer"
                },
                "priority": {
                  "type": "integer"
                }
              }
            }
          }
        }
      },
      "content_type_weights": {
        "type": "object",
        "description": "不同内容类型的权重配置",
        "properties": {
          "title": {
            "type": "number",
            "default": 2.0
          },
          "abstract": {
            "type": "number",
            "default": 1.5
          },
          "body": {
            "type": "number",
            "default": 1.0
          },
          "specs": {
            "type": "number",
            "default": 1.2
          },
          "procedure": {
            "type": "number",
            "default": 1.3
          },
          "lore": {
            "type": "number",
            "default": 0.8
          },
          "warning": {
            "type": "number",
            "default": 1.4
          }
        }
      }
    }
  },
  "vector_embedding": {
    "type": "object",
    "description": "向量嵌入配置",
    "properties": {
      "embedding_model": {
        "type": "string",
        "description": "使用的嵌入模型"
      },
      "vector_dimension": {
        "type": "integer",
        "default": 768,
        "description": "向量维度"
      },
      "fields_to_embed": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "field_path": {
              "type": "string"
            },
            "field_name": {
              "type": "string"
            },
            "weight": {
              "type": "number"
            },
            "preprocessing": {
              "type": "string"
            }
          }
        },
        "default": [
          {
            "field_path": "title.full",
            "field_name": "标题",
            "weight": 2.0
          },
          {
            "field_path": "technical_content.abstract",
            "field_name": "摘要",
            "weight": 1.5
          },
          {
            "field_path": "technical_content.description.overview",
            "field_name": "概述",
            "weight": 1.2
          },
          {
            "field_path": "tags",
            "field_name": "标签",
            "weight": 1.3
          },
          {
            "field_path": "keywords",
            "field_name": "关键词",
            "weight": 1.4
          }
        ]
      },
      "chunk_embedding": {
        "type": "object",
        "properties": {
          "enabled": {
            "type": "boolean",
            "default": true
          },
          "store_in_entry": {
            "type": "boolean",
            "default": false
          },
          "external_storage": {
            "type": "string"
          }
        }
      }
    }
  },
  "metadata_filtering": {
    "type": "object",
    "description": "元数据过滤配置",
    "properties": {
      "filterable_fields": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "field": {
              "type": "string"
            },
            "type": {
              "type": "string",
              "enum": [
                "string",
                "number",
                "array",
                "boolean",
                "date"
              ]
            },
            "operators": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "facetable": {
              "type": "boolean"
            }
          }
        },
        "default": [
          {
            "field": "category.primary",
            "type": "string",
            "operators": [
              "eq",
              "in"
            ],
            "facetable": true
          },
          {
            "field": "difficulty_level.technical",
            "type": "number",
            "operators": [
              "eq",
              "gt",
              "lt",
              "range"
            ],
            "facetable": true
          },
          {
            "field": "difficulty_level.required_clearance",
            "type": "string",
            "operators": [
              "eq",
              "in"
            ],
            "facetable": true
          },
          {
            "field": "tags",
            "type": "array",
            "operators": [
              "contains",
              "in"
            ],
            "facetable": true
          },
          {
            "field": "version_info.status",
            "type": "string",
            "operators": [
              "eq"
            ],
            "facetable": false
          },
          {
            "field": "metadata.last_modified",
            "type": "date",
            "operators": [
              "gt",
              "lt",
              "range"
            ],
            "facetable": false
          }
        ]
      },
      "predefined_filters": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "filter_id": {
              "type": "string"
            },
            "name": {
              "type": "string"
            },
            "description": {
              "type": "string"
            },
            "conditions": {
              "type": "object"
            }
          }
        },
        "default": [
          {
            "filter_id": "beginner-friendly",
            "name": "入门级内容",
            "description": "技术难度1-2的内容",
            "conditions": {
              "difficulty_level.technical": {
                "lte": 2
              }
            }
          },
          {
            "filter_id": "approved-only",
            "name": "已批准文档",
            "description": "仅显示已批准的正式文档",
            "conditions": {
              "version_info.status": "APPROVED"
            }
          },
          {
            "filter_id": "power-systems",
            "name": "动力系统",
            "description": "所有动力相关文档",
            "conditions": {
              "category.primary": "PWR"
            }
          }
        ]
      }
    }
  },
  "retrieval_result": {
    "type": "object",
    "description": "RAG检索结果格式",
    "properties": {
      "query_id": {
        "type": "string"
      },
      "query_text": {
        "type": "string"
      },
      "results": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "rank": {
              "type": "integer"
            },
            "entry_id": {
              "type": "string"
            },
            "entry_title": {
              "type": "string"
            },
            "chunk_id": {
              "type": "string"
            },
            "chunk_content": {
              "type": "string"
            },
            "chunk_type": {
              "type": "string"
            },
            "score": {
              "type": "number"
            },
            "vector_score": {
              "type": "number"
            },
            "keyword_score": {
              "type": "number"
            },
            "metadata_match": {
              "type": "object"
            },
            "highlighted_snippet": {
              "type": "string"
            },
            "relevant_sections": {
              "type": "array",
              "items": {
                "type": "string"
              }
            },
            "context_chunks": {
              "type": "array",
              "items": {
                "type": "string"
              }
            }
          }
        }
      },
      "aggregations": {
        "type": "object",
        "properties": {
          "by_category": {
            "type": "object"
          },
          "by_difficulty": {
            "type": "object"
          },
          "by_clearance": {
            "type": "object"
          }
        }
      },
      "suggested_queries": {
        "type": "array",
        "items": {
          "type": "string"
        }
      }
    }
  },
  "context_assembly": {
    "type": "object",
    "description": "检索结果上下文组装配置",
    "properties": {
      "max_context_length": {
        "type": "integer",
        "default": 4000,
        "description": "最大上下文长度（token数）"
      },
      "assembly_strategy": {
        "type": "string",
        "enum": [
          "sequential",
          "relevance_ranked",
          "hierarchical"
        ],
        "default": "relevance_ranked"
      },
      "include_metadata": {
        "type": "boolean",
        "default": true
      },
      "include_source_links": {
        "type": "boolean",
        "default": true
      },
      "format_template": {
        "type": "string",
        "default": "\n[文档: {entry_title}]\n[分类: {category}]\n[相关度: {score}]\n\n{chunk_content}\n\n---\n"
      }
    }
  }
}
```


# RAG检索适配方案说明

## 1. 文本分块策略

### 1.1 分块类型

| 分块类型 | 描述 | 适用场景 |
|---------|------|---------|
| **语义分块** | 基于内容语义边界分割 | 技术文档、叙述性内容 |
| **固定大小分块** | 按固定token数分割 | 结构化数据、代码 |
| **层次分块** | 多级粒度分块 | 复杂技术手册 |
| **混合分块** | 组合多种策略 | 综合场景 |

### 1.2 技术文档专用分块规则

```
技术文档分块优先级：
1. 标题块 (title.full) - 权重2.0
2. 摘要块 (abstract) - 权重1.5
3. 原理段落块 (principles[i]) - 权重1.2
4. 规格表块 (specifications.tables[i]) - 权重1.2
5. 警告块 (safety_warnings[i]) - 权重1.4
6. 程序步骤块 (procedures[i].steps[j]) - 权重1.3
7. 背景故事块 (lore_snippet) - 权重0.8
```

### 1.3 分块示例

```json
{
  "text_chunks": [
    {
      "chunk_id": "PWR-RTG-0042-C001",
      "content": "MMOD-2100型RTG是一种基于塞贝克效应的热电转换装置...",
      "chunk_type": "abstract",
      "token_count": 45,
      "weight": 1.5
    },
    {
      "chunk_id": "PWR-RTG-0042-C002",
      "content": "塞贝克效应原理：当两种不同导体或半导体构成回路...",
      "chunk_type": "body",
      "token_count": 38,
      "weight": 1.2
    }
  ]
}
```

## 2. 向量嵌入字段

### 2.1 嵌入字段配置

| 字段路径 | 字段名称 | 权重 | 说明 |
|---------|---------|------|------|
| title.full | 完整标题 | 2.0 | 最高权重，标题包含核心信息 |
| technical_content.abstract | 技术摘要 | 1.5 | 摘要浓缩了关键内容 |
| technical_content.description.overview | 概述 | 1.2 | 整体描述 |
| technical_content.description.principles | 原理 | 1.2 | 技术原理 |
| tags | 检索标签 | 1.3 | 结构化标签 |
| keywords | 关键词 | 1.4 | 英文关键词 |

### 2.2 嵌入向量存储

```json
{
  "rag_index": {
    "embedding_vector": [0.023, -0.156, 0.892, ...], // 768维向量
    "embedding_model": "text-embedding-3-large",
    "embedding_timestamp": "2146-10-28T14:30:00Z"
  }
}
```

## 3. 元数据过滤

### 3.1 可过滤字段

| 字段 | 类型 | 可用操作符 | 分面支持 |
|-----|------|-----------|---------|
| category.primary | string | eq, in | 是 |
| difficulty_level.technical | number | eq, gt, lt, range | 是 |
| difficulty_level.required_clearance | string | eq, in | 是 |
| tags | array | contains, in | 是 |
| version_info.status | string | eq | 否 |
| metadata.last_modified | date | gt, lt, range | 否 |

### 3.2 预定义过滤器

```json
{
  "predefined_filters": [
    {
      "filter_id": "beginner-friendly",
      "name": "入门级内容",
      "conditions": {"difficulty_level.technical": {"lte": 2}}
    },
    {
      "filter_id": "high-clearance",
      "name": "机密文档",
      "conditions": {"difficulty_level.required_clearance": {"in": ["SECRET", "TOP_SECRET"]}}
    }
  ]
}
```

## 4. 检索流程

```
用户查询
    ↓
[1] 查询预处理
    - 关键词提取
    - 意图识别
    - 元数据过滤条件解析
    ↓
[2] 混合检索
    - 向量检索 (相似度匹配)
    - 关键词检索 (BM25/TF-IDF)
    - 元数据过滤
    ↓
[3] 结果融合与排序
    - RRF (Reciprocal Rank Fusion)
    - 加权评分
    ↓
[4] 上下文组装
    - 选择Top-K结果
    - 按相关性排序
    - 格式化输出
    ↓
[5] 返回增强上下文
    - 格式化的文档片段
    - 源引用信息
    - 相关度分数
```

## 5. 前端集成

### 5.1 搜索组件数据结构

```typescript
interface SearchState {
  query: string;
  filters: {
    categories: string[];
    difficultyRange: [number, number];
    clearance: string[];
    tags: string[];
  };
  results: SearchResult[];
  aggregations: {
    categoryCounts: Record<string, number>;
    difficultyDistribution: number[];
  };
  isLoading: boolean;
}
```

### 5.2 搜索结果展示

```typescript
interface SearchResult {
  entryId: string;
  title: string;
  category: string;
  abstract: string;
  score: number;
  highlightedSnippet: string;
  relevantSections: string[];
  thumbnail?: string;
}
```


---

## 5. 字段说明文档


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


---

## 附录

### A. 分类代码对照表

| 代码 | 名称 | 说明 |
|-----|------|------|
| PWR | 动力系统 | 发电、储能、配电 |
| CHEM | 化学 | 合成、反应、材料 |
| MECH | 机械 | 结构、传动、液压 |
| MED | 医疗 | 诊断、治疗、急救 |
| ELEC | 电子 | 电路、信号、控制 |
| NAV | 导航 | 定位、制导、通信 |
| ENV | 环境 | 生命维持、气候控制 |
| COM | 通信 | 数据传输、网络 |

### B. 文档状态流转

```
DRAFT → REVIEW → APPROVED
                ↓
           SUPERSEDED → OBSOLETE
```

### C. 权限级别层级

```
PUBLIC < RESTRICTED < CONFIDENTIAL < SECRET < TOP_SECRET
```
