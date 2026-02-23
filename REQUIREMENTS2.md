# 📄 产品需求说明文档（PRD）  
## 项目名称：Confluence AI 知识助手（Always-on LLM Edition）

### 1. 🎯 产品目标
构建一个**始终使用大模型 API**的本地对话系统，让开发/测试团队通过自然语言提问（如“如何部署服务”），即时获得从 Confluence 导出 HTML 中提取并由大模型优化的精准答案。  

**核心原则**：  
- ✅ **必须始终调用大模型**（无“纯本地”降级模式）  
- ✅ **不使用向量数据库 / RAG / chunking**  
- ✅ **数据源 = Confluence 导出的 HTML 文件（1 页面 = 1 文件）**  
- ✅ **维护成本极低**（放 HTML → 自动更新）

---

### 2. 🧩 核心功能需求

| 功能模块 | 需求描述 | 技术实现要求 |
|---------|--------|------------|
| **数据摄入** | 从 `./confluence_html/` 目录读取 `.html` 文件 | 使用 `BeautifulSoup` 提取纯文本，保留图片/流程图链接 |
| **答案生成** | **必须调用大模型 API** 将原始 HTML 内容转化为简洁、自然的问答语句 | 每次生成 FAQ 时批量调用一次 API（非逐条调用） |
| **对话交互** | 用户提问 → 匹配问题标题 → 返回大模型优化后的答案 | 使用 Rasa + 自定义 Action 实现 |
| **前端界面** | 提供 Web 聊天窗口，支持中文输入/输出 | 使用 `rasa-webchat` 嵌入式组件 |
| **自动更新** | 新增/修改 HTML 文件后，重新运行脚本即可更新知识库 | 提供一键更新命令 |

---

### 3. ⚙️ 技术架构要求

#### 3.1 整体架构
[Confluence HTML 文件]
↓
[extract_faq.py] → 调用大模型 API → 生成优化版 faq.json
↓
[Rasa NLU] → 识别用户意图（ask_faq）
↓
[Custom Action] → 从 faq.json 返回预生成答案
↓
[Webchat 前端] ←→ 用户
text

编辑




#### 3.2 关键约束
- **必须使用大模型**：禁用任何“无 API”回退逻辑  
- **无向量组件**：不得引入 Chroma/FAISS/Pinecone 等  
- **无文本分块**：每个 HTML 文件作为整体处理  
- **API 支持**：优先阿里云百炼（DashScope），兼容 OpenAI  

---

### 4. 📁 项目文件结构（AI IDE 必须生成）
confluence-ai-kb/
├── confluence_html/ # Confluence 导出的 HTML 文件目录
│ └── 如何部署服务.html # 示例文件
├── data/
│ └── faq.json # 大模型优化后的问答库（JSON 格式）
├── actions/
│ └── actions.py # 自定义 Action 逻辑
├── extract_faq.py # HTML → 大模型优化 → FAQ
├── webchat.html # 前端聊天界面
├── config.yml # Rasa 配置
├── credentials.yml # 凭据
├── domain.yml # 对话域
├── endpoints.yml # Action Server 地址
├── .env # API 密钥配置（必须存在）
├── requirements.txt # 依赖列表
└── README.md # 部署与使用指南
text

编辑




---

### 5. 📝 文件内容规范（AI IDE 生成细则）

#### 5.1 `.env`（必须包含以下字段）
```env
# 大模型 API 配置（二选一）
DASHSCOPE_API_KEY=your_dashscope_key_here
# 或
OPENAI_API_KEY=your_openai_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# 模型选择（可选）
LLM_MODEL=qwen-max  # DashScope 默认
# LLM_MODEL=gpt-3.5-turbo  # OpenAI 默认
```

5.2 extract_faq.py（核心逻辑）
必须调用大模型：构造 prompt 批量优化所有 FAQ 条目
输入：confluence_html/*.html
输出：data/faq.json（格式：[{"question": "...", "answer": "..."}]）
错误处理：若 API 调用失败，抛出异常（不允许静默降级）

5.3 actions/actions.py
从 data/faq.json 加载预生成答案
用户提问时，精确匹配 question 字段
若未匹配，返回：“未找到相关答案，请尝试以下问题：\n- [问题1]\n- [问题2]...”

5.4 其他配置文件
domain.yml：定义 ask_faq intent 和 action_answer_faq
endpoints.yml：指向 http://localhost:5055/webhook
webchat.html：集成 rasa-webchat，支持中文

6. 🚀 部署与使用流程（写入 README.md）

6.1 初始化
bash

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置 API 密钥
cp .env.example .env
# 编辑 .env 填入 DASHSCOPE_API_KEY 或 OPENAI_API_KEY
6.2 生成知识库
bash

编辑



# 3. 放入 Confluence HTML 文件到 confluence_html/
# 4. 生成优化版 FAQ（必须调用大模型）
python extract_faq.py
6.3 启动服务
bash

编辑



# 5. 启动 Action Server（终端1）
rasa run actions

# 6. 启动 Rasa Core（终端2）
rasa train && rasa run --enable-api --cors "*"
6.4 访问
打开 webchat.html 开始对话
更新知识库：放入新 HTML → 重新运行 python extract_faq.py → 重启 Rasa
7. ❌ 禁止事项（AI IDE 不得生成）
任何向量数据库相关代码（Chroma/FAISS 等）
文本分块（chunking）逻辑
“无 API”降级模式或本地 fallback
爬虫或 Confluence API 调用代码
Dockerfile（除非明确要求）
8. ✅ 验收标准（AI IDE 输出必须满足）
项目结构完整，所有文件按规范生成
extract_faq.py 必须调用大模型 API（DashScope 或 OpenAI）
运行 python extract_faq.py 后生成有效的 faq.json
Rasa 能正确加载 FAQ 并通过 Webchat 返回答案
README.md 包含清晰的部署步骤和 API 配置说明

请基于此 PRD，在当前工作区自动生成完整的项目文件，确保：
始终使用大模型（无降级逻辑）
1 Confluence 页面 = 1 HTML 文件 = 1 FAQ 条目
零向量数据库、零 chunking、零爬虫
提供开箱即用的部署指南