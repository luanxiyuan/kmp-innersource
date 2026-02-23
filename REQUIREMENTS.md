# 本地 AI 知识库对话系统 - 项目需求文档

## 项目概述

为开发/测试团队搭建一个基于本地 HTML 文件的 AI 知识库问答系统，支持通过自然语言提问获取准确答案和原文链接。

**✨ 核心特性**：支持大模型 API 增强，提供更智能的问答体验

## 核心需求

### 1. 数据源
- **来源**: 从 `./confluence_html/` 目录读取 Confluence 导出的 `.html` 文件
- **特点**: 无需 API，无需爬虫，纯本地文件读取
- **更新方式**: 放入新 HTML 文件 → 自动更新知识库

### 2. 核心功能
- **用户提问**: 支持自然语言提问（如"如何部署服务"、"数据库配置方法"）
- **答案返回**: 
  - 从 HTML 内容中提取准确答案
  - 提供原文链接（文件路径或页面标识）
  - 支持中文问答
- **匹配方式**: 基于关键词匹配、同义词扩展和 Rasa NLU 意图分类

### 3. AI 增强功能（可选但推荐）

#### 3.1 答案优化
- 将原始 HTML 文本提炼为简洁、自然的问答语言
- 批量处理降低 API 成本
- 永久保存优化结果

#### 3.2 模糊提问理解
- 支持同义词匹配（"上线" → "部署"、"发布"）
- 语义映射（自动识别同义表达）
- 关键词增强（自动扩展同义词）

#### 3.3 对话引导
- 自动生成多轮追问
- 基于 FAQ 内容推荐相关问题
- 提升用户满意度

### 4. 技术栈

#### 后端
- **Rasa 3.x**: 开源对话框架
  - NLU: 自然语言理解（意图识别）
  - Core: 对话管理
  - Actions: 自定义动作执行
- **Python 3.9+**: 脚本语言
  - BeautifulSoup4: HTML 解析
  - jieba: 中文分词

#### AI 增强模块（可选）
- **OpenAI**: GPT-3.5/GPT-4
- **Anthropic**: Claude 系列
- **阿里云**: 通义千问
- **本地模型**: Qwen2.5-7B/3B 等

#### 前端
- **HTML/CSS/JS**: 简单集成页面

### 5. 关键约束

#### 零反爬处理
- ❌ 不使用爬虫技术
- ❌ 不处理反爬机制（headers、cookies、代理等）
- ✅ 直接读取本地 HTML 文件

#### 维护成本≈0
- ✅ 新增 HTML 文件到目录即自动更新
- ✅ 无需手动标注训练数据（自动生成 NLU 训练数据）
- ✅ 无需频繁调参
- ✅ 自动生成 FAQ JSON
- ✅ AI 增强后永久复用

#### 完全本地运行
- ✅ 不依赖云服务（OpenAI、Azure 等）用于核心功能
- ✅ 所有数据存储在本地
- ✅ 支持离线运行（AI 增强除外）

#### 中文支持
- ✅ 中文分词（jieba）
- ✅ 中文对话理解（spaCy 中文模型）

#### 无向量依赖
- ❌ 不使用任何向量数据库
- ❌ 不使用 embedding 模型
- ❌ 不使用语义检索
- ❌ 不进行相似度计算
- ✅ 纯基于规则和关键词匹配

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面                              │
│                    (自定义 Web 聊天界面)                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Rasa 服务器                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │    NLU       │  │    Core      │  │   Actions    │    │
│  │ (意图识别)    │  │  (对话管理)   │  │ (关键词匹配)  │    │
│  │              │  │              │  │ + 同义词支持 │    │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘    │
└─────────┼─────────────────┼─────────────────┼─────────────┘
          │                 │                 │
          ▼                 ▼                 ▼
┌─────────────────────────────────────────────────────────────┐
│                  FAQ JSON 数据库                             │
│          (存储问答对和关键词索引)                            │
│  ┌────────────────────────────────────────────────────┐    │
│  │  基础版 FAQ (无 AI)                                │    │
│  │  - question: 原始问题                              │    │
│  │  - answer: HTML 文本摘要                          │    │
│  │  - keywords: 基础关键词列表                       │    │
│  └────────────────────────────────────────────────────┘    │
│  ┌────────────────────────────────────────────────────┐    │
│  │  增强版 FAQ (有 AI)                                │    │
│  │  - question: AI 优化的自然语言问题                │    │
│  │  - answer: AI 提炼的简洁答案                      │    │
│  │  - keywords: 扩展关键词                            │    │
│  │  - synonyms: 同义词字典                           │    │
│  │  - conversation_starters: 对话引导                │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              FAQ 构建流程                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ HTML 解析    │  │ AI 优化      │  │ 生成索引     │    │
│  │ (BeautifulSoup│→ │ (大模型 API) │→ │ (关键词+同义词)│    │
│  │  提取文本)   │  │  答案提炼)   │  │              │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 功能模块

### 1. HTML 解析模块
- 扫描 `./confluence_html/` 目录
- 使用 BeautifulSoup 解析 HTML
- 提取文本内容（去除 HTML 标签、脚本、样式）
- 提取元数据（标题、文件名、相对路径）
- 提取关键词（基于预设关键词列表）
- 生成问题（将标题转换为问题形式）
- 生成答案（取内容前 500 字作为摘要）

### 2. FAQ 增强模块
- 从解析后的数据生成 FAQ 条目
- 调用大模型 API 批量优化：
  - 优化问题为自然语言形式
  - 提炼答案为简洁专业的表述
  - 扩展关键词和同义词
  - 生成对话引导
- 生成 `data/faq_enhanced.json` - 增强型 FAQ 数据库
- 生成 `data/keyword_index_enhanced.json` - 增强关键词索引（含同义词）
- 生成 `data/conversation_guides.json` - 对话引导数据
- 自动生成 `data/nlu_generated.yml` - Rasa NLU 训练数据
  - 与手写的 `data/nlu.yml`（通用意图）合并使用

### 3. FAQ 检索模块
- **关键词/同义词匹配**：
  - 使用关键词索引快速定位
  - 支持同义词匹配
  - 统计关键词匹配数量
  - 返回匹配最多的条目
- **语义相似度**：
  - 预设语义映射字典
  - 支持"怎么上线代码？" → "如何部署服务"
- **标题模糊匹配**：
  - 检查查询是否在标题中
  - 检查查询词汇在标题中的覆盖率
- **字符串相似度**：
  - 简单的字符串包含检查

### 4. Rasa 对话模块
- 手写的 NLU 训练数据（通用意图）
- 自动生成的 FAQ 训练数据
- 预定义的对话流程
- 自定义动作调用 FAQ 检索
- 返回结构化答案 + 对话引导

## 部署要求

### 硬件要求
- CPU: 2核以上
- 内存: 4GB+（基础版）
- 内存: 8GB+（AI 增强版）
- 硬盘: 5GB+

### 软件要求
- Python 3.9+
- Rasa 3.6+
- 现代浏览器（Chrome/Firefox/Edge）

### 安装步骤
```bash
# 1. 创建虚拟环境
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置 AI（可选）
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env

# 编辑 .env 文件，填入 API 密钥

# 4. 准备数据
# Windows
mkdir confluence_html

# Linux/Mac
mkdir -p confluence_html

# 将 Confluence 导出的 HTML 文件放入此目录

# 5. 构建 FAQ
python scripts/build_faq_enhanced.py
# 或不使用 AI: python scripts/build_faq_enhanced.py --no-enhance

# 6. 训练 Rasa 模型
rasa train

# 7. 启动服务
# Windows (新窗口)
start cmd /k "rasa run --enable-api --cors "*""
start cmd /k "rasa run actions"

# Linux/Mac (后台运行)
rasa run --enable-api --cors "*" &
rasa run actions

# 8. 打开前端
# 在浏览器中打开 index.html
```

## 使用流程

### 初次使用
1. 将 Confluence 导出的 HTML 文件放入 `./confluence_html/` 目录
2. （可选）配置 `.env` 文件，填入 AI API 密钥
3. 运行 `python scripts/build_faq_enhanced.py` 生成增强型 FAQ
4. 运行 `rasa train` 训练对话模型
5. 运行 `rasa run --enable-api --cors "*"` 启动 Rasa 服务器
6. 运行 `rasa run actions` 启动动作服务器
7. 在浏览器中打开 `index.html` 开始对话

### 日常更新
1. 将新的 HTML 文件放入 `./confluence_html/` 目录
2. 运行 `python scripts/build_faq_enhanced.py` 重新生成：
   - `data/faq_enhanced.json` - 增强型 FAQ 数据库
   - `data/keyword_index_enhanced.json` - 增强关键词索引（含同义词）
   - `data/conversation_guides.json` - 对话引导数据
   - `data/nlu_generated.yml` - 自动生成的 NLU 训练数据
3. 运行 `rasa train` 重新训练模型（合并手写和自动生成的 NLU 数据）
4. 重启 Rasa 服务
5. 问答系统自动包含新内容

## 数据流示例

### 用户提问："如何部署服务？"
```
用户: "如何部署服务？"
  ↓
Rasa NLU: 识别意图（ask_question）
  ↓
Rasa Core: 调用 action_search_faq
  ↓
Custom Action:
  1. 加载增强型 FAQ JSON 和关键词索引
  2. 关键词匹配: 找到包含"部署"的 FAQ
  3. 同义词匹配: "上线"、"发布"等也能匹配
  4. 标题匹配: 找到标题包含"部署"的 FAQ
  5. 返回最佳匹配
  ↓
前端显示:
  📄 如何将服务部署到生产环境？
  
  部署服务需要三个步骤：首先准备配置文件，包括环境变量和服务端口设置；然后运行 docker-compose up -d 启动服务容器；最后通过 docker ps 检查服务状态，确保所有容器正常运行。
  
  🔗 文档: 部署指南
  📁 文件: deployment_guide.html
  
  💡 可能还想知道：
  • 部署失败如何排查？
  • 如何回滚已部署的服务？
  • 多环境部署有什么最佳实践？
```

## 项目文件结构

```
kmp-innersource/
├── confluence_html/              # HTML 文件目录
│   ├── page1.html
│   └── page2.html
├── data/                         # 数据目录
│   ├── nlu.yml                  # NLU 训练数据（手写通用意图）
│   ├── nlu_generated.yml        # 自动生成的 FAQ 训练数据（运行 build_faq_enhanced.py 生成）
│   ├── stories.yml              # 对话故事
│   ├── rules.yml                # 规则
│   ├── domain.yml               # 领域配置
│   ├── faq_enhanced.json       # FAQ 数据库（运行 build_faq_enhanced.py 生成）
│   ├── keyword_index_enhanced.json # 关键词索引（运行 build_faq_enhanced.py 生成）
│   └── conversation_guides.json # 对话引导数据（运行 build_faq_enhanced.py 生成）
├── models/                       # Rasa 模型目录
├── scripts/                      # Python 脚本
│   ├── html_parser.py           # HTML 解析
│   ├── faq_enhancer.py          # AI 优化模块
│   └── build_faq_enhanced.py    # 生成 FAQ
├── actions/                      # Rasa 自定义动作
│   └── actions.py               # 增强型动作（支持同义词、模糊匹配、对话引导）
├── rasa_config/                  # Rasa 配置
│   ├── config.yml
│   ├── credentials.yml
│   └── endpoints.yml
├── webchat/                      # Webchat 前端
│   └── index.html
├── .env.example                  # 环境变量配置模板
├── requirements.txt              # Python 依赖
├── setup.bat/setup.sh            # 初始化脚本
├── start.bat/start.sh            # 启动脚本
├── stop.bat/stop.sh              # 停止脚本
├── update_kb.bat/update_kb.sh    # 更新 FAQ 脚本
├── README.md                     # 使用说明
├── LLM_ENHANCEMENT.md           # AI 增强功能详细说明
├── docs/                         # 文档目录
│   └── LLM_INTEGRATION.md       # 大模型集成指南
└── REQUIREMENTS.md              # 本文档
```

## 性能指标

### 响应时间
- 关键词匹配: < 0.1s
- 同义词匹配: < 0.2s
- 标题匹配: < 0.5s
- 总体响应: < 1s

### 准确率
- 精确关键词匹配: > 95%
- 模糊匹配: > 80%
- AI 增强后: > 85%

### 可扩展性
- 支持 1000+ HTML 文件
- 支持 10000+ FAQ 条目

### AI 增强成本
- 100 条 FAQ: ~$0.002 (OpenAI GPT-3.5)
- 构建时间: ~1 分钟
- 优化结果永久使用

## 安全与隐私

- ✅ 所有数据本地存储
- ✅ 核心功能不向外部发送任何数据
- ✅ 支持完全离线运行（AI 增强除外）
- ✅ 用户对话日志可选保存
- ✅ API 密钥通过环境变量安全管理

## 后续优化方向

1. **多模态支持**: 支持从 PDF、Word 文档提取内容
2. **语义映射扩展**: 使用 LLM 自动生成更多同义词
3. **多轮对话**: 支持追问和上下文理解
4. **分类标签**: 为 FAQ 添加分类标签
5. **反馈机制**: 收集用户反馈优化匹配
6. **本地大模型**: 完全本地化的 AI 增强方案

## 附录：技术选型理由

### Rasa
- 开源免费
- 成熟的对话框架
- 支持自定义动作
- 活跃的社区

### BeautifulSoup
- 轻量级 HTML 解析
- 简单易用
- Python 标准库生态

### jieba
- 高效中文分词
- 支持自定义词典
- 轻量级

### OpenAI API
- 质量最高的通用大模型
- 稳定可靠
- 批处理支持
- 成本可控

### FAQ 架构优势
- 无需向量化，速度快
- 维护成本低
- 匹配逻辑透明
- 易于调试和优化
- 支持 AI 增强但不强制依赖
