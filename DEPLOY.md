# 拉普兰德企业微信机器人 - 部署指南

## 前置准备

1. **一个企业微信账号**（注册地址：https://work.weixin.qq.com/）
2. **一个OpenAI兼容的API密钥**（可以是OpenAI官方、Azure OpenAI、或其他兼容服务）
3. **一台有公网IP的服务器**（或者可以用内网穿透工具如 ngrok/frp）

---

## 第一步：企业微信后台配置

1. 登录 [企业微信管理后台](https://work.weixin.qq.com/wework_admin/frame)
2. 进入 **应用管理 → 自建 → 创建应用**
3. 填写应用信息（名称：拉普兰德，logo随便传一个）
4. 创建后记录：**AgentId** 和 **Secret**
5. 进入 **我的企业**，复制 **企业ID（CorpId）**

### 配置回调URL

1. 在应用详情页找到 **企业可信IP**，填入你服务器的IP
2. 找到 **回调配置**，点击"设置"
3. URL格式：`http://你的域名:8080/callback`（建议用HTTPS，可以用Nginx反代）
4. Token：自己生成一个随机字符串
5. EncodingAESKey：点击"随机获取"
6. 保存后会验证URL——验证逻辑已经写在代码里了

---

## 第二步：配置环境变量

```bash
cd wecom-lapland-bot
cp .env.example .env
```

编辑 `.env` 填入你的配置：

```
WECOM_CORP_ID=你的企业ID
WECOM_AGENT_ID=你的应用AgentId
WECOM_CORP_SECRET=你的应用Secret
WECOM_TOKEN=你设置的回调Token
WECOM_ENCODING_AES_KEY=回调EncodingAESKey

OPENAI_API_KEY=sk-你的API密钥
OPENAI_BASE_URL=https://api.openai.com/v1  # 如果使用代理或兼容服务，改这里
OPENAI_MODEL=gpt-4o

HOST=0.0.0.0
PORT=8080
```

---

## 第三步：启动

### 方式一：Docker（推荐）

```bash
docker compose up -d
```

### 方式二：直接运行

```bash
pip install -r requirements.txt
python main.py
```

---

## 第四步：验证

1. 访问 `http://你的域名:8080/health` -> 返回 `{"status":"alive","bot":"拉普兰德"}`
2. 在企业微信中向你的应用发送消息
3. 机器人会用拉普兰德的口吻回复你

---

## 可选优化

### HTTPS + Nginx 反代

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location /callback {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

设置好后在企业微信回调URL改为 `https://your-domain.com/callback`

### 内网穿透（开发测试用）

```bash
ngrok http 8080
```

然后把回调URL设为 `https://xxxx.ngrok.io/callback`

---

## 命令

| 功能 | 命令 |
|------|------|
| 查看日志 | `docker compose logs -f` |
| 停止服务 | `docker compose down` |
| 重启服务 | `docker compose restart` |
| 清除对话 | 发送 `/reset` |
