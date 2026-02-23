# 本地 AI 知识库对话系统

基于 Rasa + BeautifulSoup 的本地 FAQ 知识库问答系统，支持从 Confluence 导出的 HTML 文件中提取答案。

**✨ 新特性：支持大模型 API 增强**

- 🤖 **AI 答案优化**：将原始 HTML 文本提炼为简洁、自然的问答语言
- 🎯 **模糊提问理解**：支持"怎么上线代码？"匹配"如何部署服务"
- 💬 **对话引导**：自动生成多轮追问，提升用户体验

## 快速开始

### 1. 安装依赖

```bash
# Windows (PowerShell)
python -m venv venv
venv\Scripts\activate
.\setup.bat

# Windows (CMD)
python -m venv venv
venv\Scripts\activate
setup.bat

# Linux/Mac
python -m venv venv
source venv/bin/activate
./setup.sh
```

### 2. 配置 AI（必需）（必需）

```bash
# Windows (PowerShell)
copy .env.example .env

# Windows (CMD)
copy .env.example .env

# Linux/Mac
cp .env.example .env

# 编辑 .env 文件，填入 API 密钥
# 示例（OpenAI）:
LLM_TYPE=openai
OPENAI_API_KEY=sk-your-key-here

# 示例（DeepSeek - 兼容 OpenAI API，成本更低）:
# LLM_TYPE=deepseek
# DEEPSEEK_API_KEY=sk-your-deepseek-key-here
```

**支持的 AI 提供商**：
- OpenAI (GPT-3.5/GPT-4)
- Anthropic (Claude)
- 阿里云通义千问
- Deepseek
- 本地模型 (Qwen2.5-7B 等)

### 3. 准备数据

将 Confluence 导出的 HTML 文件放入 `confluence_html/` 目录：

```bash
# Windows
mkdir confluence_html

# Linux/Mac
mkdir -p confluence_html

# 将你的 HTML 文件复制到此目录
```

### 4. 构建 FAQ

```bash
# Windows (PowerShell/CMD)
python scripts\build_faq_enhanced.py

# Linux/Mac
python scripts/build_faq_enhanced.py

# 方式 1: 使用 AI 增强（推荐，需要 .env 配置）
# （如果 .env 存在，自动使用 AI）

# 方式 2: 必须使用 AI（基础模式）
# Windows
python scripts\build_faq_enhanced.py --no-enhance

# Linux/Mac
python scripts/build_faq_enhanced.py --no-enhance
```

### 5. 训练 Rasa 模型

```bash
# Windows (PowerShell/CMD)
rasa train

# Linux/Mac
rasa train
```

### 6. 启动服务

```bash
# Windows
start.bat

# Linux/Mac
./start.sh
```

### 7. 使用系统

在浏览器中打开 `webchat/index.html`，开始提问。

## 使用示例

**问**: "怎么上线代码？"

**答**（AI 增强版）:
```
📄 如何将服务部署到生产环境？

部署服务需要三个步骤：首先准备配置文件，包括环境变量和服务端口设置；然后运行 docker-compose up -d 启动服务容器；最后通过 docker ps 检查服务状态，确保所有容器正常运行。

🔗 文档: 部署指南
📁 文件: deployment_guide.html

💡 可能还想知道：
• 部署失败如何排查？
• 如何回滚已部署的服务？
• 多环境部署有什么最佳实践？
```

## 日常维护

### 更新知识库

当有新的 HTML 文件时：

```bash
# 将新文件放入 confluence_html/ 目录
python scripts/build_faq_enhanced.py
rasa train  # 重新训练模型（必需）
```

### 停止服务

```bash
# Windows
stop.bat

# Linux/Mac
./stop.sh
```

## 目录结构

```
kmp-innersource/
├── confluence_html/       # HTML 文件存放目录
├── data/                  # Rasa 训练数据和 FAQ
│   ├── nlu.yml          # NLU 训练数据（手写通用意图）
│   ├── nlu_generated.yml # 自动生成的 FAQ 训练数据（运行 build_faq_enhanced.py 生成）
│   ├── faq_enhanced.json # 增强型 FAQ（AI 优化，运行 build_faq_enhanced.py 生成）
│   └── keyword_index_enhanced.json # 增强关键词索引（含同义词，运行 build_faq_enhanced.py 生成）
├── scripts/               # Python 脚本
│   ├── html_parser.py    # HTML 解析
│   ├── faq_enhancer.py   # AI 优化模块
│   └── build_faq_enhanced.py  # FAQ 构建脚本（支持 AI 增强）
├── actions/               # Rasa 自定义动作
│   └── actions.py       # 增强型动作（支持同义词、模糊匹配、对话引导）
├── rasa_config/           # Rasa 配置文件
├── webchat/               # Webchat 前端
├── .env.example           # 环境变量配置模板
├── requirements.txt       # Python 依赖
├── setup.bat             # 初始化脚本 (Windows)
├── setup.sh              # 初始化脚本 (Linux/Mac)
├── start.bat             # 启动脚本 (Windows)
├── start.sh              # 启动脚本 (Linux/Mac)
├── stop.bat              # 停止脚本 (Windows)
├── stop.sh               # 停止脚本 (Linux/Mac)
├── update_kb.bat         # 更新 FAQ 脚本 (Windows)
└── update_kb.sh          # 更新 FAQ 脚本 (Linux/Mac)
```

## 技术栈

- **Rasa 3.x**: 对话框架
- **BeautifulSoup4**: HTML 解析
- **jieba**: 中文分词
- **OpenAI/Anthropic/通义千问**: 大模型 API（必需）
- **自定义 Web 聊天界面**: 聊天界面

## 特性

### 基础特性（需要 AI）
- ✅ 完全本地运行
- ✅ 支持中文问答
- ✅ 零反爬处理（直接读取 HTML 文件）
- ✅ 维护成本低（新增文件自动更新）
- ✅ 返回原文链接
- ✅ 基于关键词匹配

### AI 增强特性（需要 API 密钥）
- ✨ **答案优化**：将原始 HTML 文本提炼为简洁、自然的问答语言
- ✨ **模糊提问理解**：支持"怎么上线代码？"匹配"如何部署服务"（同义词匹配）
- ✨ **对话引导**：自动生成多轮追问，提升用户满意度
- ✨ **同义词扩展**：自动扩展关键词同义词，提高匹配率
- ✨ **批量优化**：批量处理降低 API 成本
- ✨ **必需使用**：可以选择是否启用 AI 增强，完全向后兼容

## 架构说明

### 基础版（无 AI）

```
用户提问 → Rasa NLU → 关键词匹配 → 返回预存答案
```

### 增强版（有 AI）

```
HTML 文件 → HTML 解析 → 大模型优化 → FAQ JSON → Rasa 问答
              ↓
         (答案提炼、同义词扩展、对话引导生成）
```

## 成本估算

以 OpenAI GPT-3.5-turbo 为例：

| FAQ 数量 | 批处理 | 预估成本 | 构建时间 |
|---------|-------|---------|---------|
| 50 条 | 1 批 | ~$0.001 | 30秒 |
| 100 条 | 5 批 | ~$0.002 | 1分钟 |
| 200 条 | 10 批 | ~$0.004 | 2分钟 |

**提示**：FAQ 增强后可永久使用，无需重复调用 API。

## 常见问题

### Q: 首次运行速度慢？

A: 首次运行需要安装 spaCy 中文模型，之后会缓存到本地。

### Q: 必须使用 AI 增强吗？

A: **不需要！** 基础版完全不依赖大模型，可以正常使用。AI 增强是必需的升级。

### Q: 如何切换 AI 提供商？

A: 编辑 `.env` 文件，修改 `LLM_TYPE` 环境变量：
```bash
LLM_TYPE=openai          # OpenAI
LLM_TYPE=anthropic       # Anthropic Claude
LLM_TYPE=qwen           # 阿里云通义千问
LLM_TYPE=local          # 本地模型
```

### Q: 支持离线运行？

A: 是的，首次安装依赖后，可以完全离线运行（AI 增强除外）。

### Q: 为什么不使用向量检索？

A: 本系统采用基于规则的 FAQ 架构，具有以下优势：
- 响应速度更快（< 1s）
- 维护成本更低
- 匹配逻辑透明，易于调试
- 无需复杂的向量化流程

### Q: 如何添加自定义关键词同义词？

A: 编辑 `actions/actions.py` 中的 `_semantic_match` 方法，添加自定义映射。

## 详细文档

- **REQUIREMENTS.md** - 系统架构和详细需求（唯一需求文档）
- **QUICKSTART.md** - Windows 快速开始指南
- **TROUBLESHOOTING.md** - 故障排除指南

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
