# 拉普兰德 —— 企业微信 AI 机器人

一个基于 FastAPI + OpenAI 兼容 API 的企业微信智能助手，搭载拉普兰德（《明日方舟》）人格系统，支持角色形态切换、AI 测试用例生成、回复质量监控。

---

## 功能

| 功能 | 说明 | 触发方式 |
|------|------|----------|
| **AI 对话** | 拉普兰德人格回复，含荒芜形态切换 | 直接发消息 |
| **清除上下文** | 重置对话历史 | `/reset` / `/clear` / `/重置` |
| **AI 测试用例生成** | 输入需求描述，自动生成结构化测试用例 | `/tc <需求描述>` |
| **质量报告** | 查看 AI 回复质量统计 | `/quality` / `/质量` |

## 架构

```
企业微信 ──HTTP──> FastAPI Server ──OpenAI API──> LLM
                        │
                        ├── 回调加解密 (AES)
                        ├── 对话上下文管理 (滑动窗口)
                        ├── 质量断言模块
                        └── 测试用例生成模块
```

## 快速开始

### 前置准备

- 一个 [企业微信账号](https://work.weixin.qq.com/)
- 一个 OpenAI 兼容 API Key
- Docker（推荐）或 Python 3.10+

### 1. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，填入你的配置：

| 变量 | 说明 |
|------|------|
| `WECOM_CORP_ID` | 企业微信 CorpID |
| `WECOM_AGENT_ID` | 应用 AgentId |
| `WECOM_CORP_SECRET` | 应用 Secret |
| `WECOM_TOKEN` | 回调 Token（自定义） |
| `WECOM_ENCODING_AES_KEY` | 回调 EncodingAESKey |
| `OPENAI_API_KEY` | OpenAI 兼容 API Key |
| `OPENAI_BASE_URL` | API 地址 |
| `OPENAI_MODEL` | 模型名（默认 gpt-4o） |

### 2. 启动

**Docker（推荐）：**

```bash
docker compose up -d
```

**直接运行：**

```bash
pip install -r requirements.txt
python main.py
```

### 3. 企业微信后台配置

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 进入 **应用管理 → 自建 → 创建应用**
3. 填写 `回调URL`：`http(s)://你的域名:8080/callback`
4. 将 Token 和 EncodingAESKey 填入 `.env`

## 命令列表

| 命令 | 说明 |
|------|------|
| `/reset` `/清除` | 重置对话上下文 |
| `/tc <需求>` | 生成 AI 测试用例 |
| `/quality` `/质量` | 查看质量报告 |

## 开发

```bash
# 安装依赖
pip install -r requirements.txt

# 运行测试
pytest tests/ -v
```

CI 流水线（GitHub Actions）在每次推送时自动运行测试 + Docker 构建。

## 许可

MIT
