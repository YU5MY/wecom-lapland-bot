"""
企业微信拉普兰德AI机器人 - FastAPI 主入口
"""
import asyncio, random
import re
from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse, Response
from loguru import logger

from config import config
import wecom
from bot import bot as lapland_bot
from testcase import tc_generator
from quality import quality_asserter

app = FastAPI(title="拉普兰德 - 企业微信AI机器人")


@app.get("/callback")
async def callback_verify(
    msg_signature: str = Query(..., alias="msg_signature"),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...),
):
    """
    企业微信后台URL验证。
    返回解密后的echostr明文即表示验证通过。
    """
    try:
        import sys
        print(f"[DEBUG] callback params: msg_signature={msg_signature}, timestamp={timestamp}, nonce={nonce}, echostr_len={len(echostr)}", flush=True)
        decrypted = wecom.verify_url(msg_signature, timestamp, nonce, echostr)
        logger.info("回调URL验证通过")
        print(f"[DEBUG] verification SUCCESS: {decrypted}", flush=True)
        return PlainTextResponse(decrypted)
    except Exception as e:
        logger.error(f"回调URL验证失败: {e}")
        print(f"[DEBUG] verification FAILED: {e}", flush=True)
        return PlainTextResponse(f"verify failed: {e}", status_code=403)


@app.post("/callback")
async def callback_receive(request: Request):
    """
    接收企业微信回调消息
    """
    # 获取请求参数
    msg_signature = request.query_params.get("msg_signature", "")
    timestamp = request.query_params.get("timestamp", "")
    nonce = request.query_params.get("nonce", "")

    # 读取原始XML
    body = await request.body()
    xml_body = body.decode("utf-8")

    # 如果是加密模式，先解密
    if config.WECOM_ENCODING_AES_KEY:
        try:
            msg_dict = wecom.decrypt_message(msg_signature, timestamp, nonce, xml_body)
        except Exception as e:
            logger.error(f"消息解密失败: {e}")
            return PlainTextResponse("decrypt failed", status_code=403)
    else:
        # 明文模式直接解析
        import xmltodict
        msg_dict = xmltodict.parse(xml_body)

    logger.debug(f"收到消息: {msg_dict}")

    # 提取消息内容
    msg_info = msg_dict.get("xml", {})
    msg_type = msg_info.get("MsgType", "")
    content = msg_info.get("Content", "")
    from_user = msg_info.get("FromUserName", "")

    # 只处理文本消息
    if msg_type == "text" and content and from_user:
        logger.info(f"来自 {from_user}: {content}")

        # 异步回复：在后台获取AI回复并发送
        asyncio.create_task(_handle_message(from_user, content))

    # 企业微信要求立即返回成功（空字符串或 "ok"）
    return PlainTextResponse("ok")


async def _handle_message(user_id: str, message: str):
    """后台处理消息并发送回复（分句逐条发送）"""
    import time
    try:
        cmd = message.strip()
        if cmd in ["/reset", "/clear", "/重置", "/清除"]:
            lapland_bot.clear_history(user_id)
            reply = "呵——切了重来。有什么想说的现在说吧。"
        elif cmd.startswith("/tc") or cmd.startswith("/测试用例"):
            desc = cmd.replace("/tc", "").replace("/测试用例", "").strip()
            if not desc:
                reply = "……需求描述呢？你总得给我点东西咬吧。\n用法：/tc 登录页面，输入框需要校验邮箱格式"
            else:
                reply = await tc_generator.generate(desc)
        elif cmd == "/quality" or cmd == "/质量":
            summary = quality_asserter.summary()
            reply = (
                f"【质量报告】\n"
                f"调用次数：{summary['total_calls']}\n"
                f"异常次数：{summary['failure_count']}\n"
                f"通过率：{summary['pass_rate']}%\n"
                f"平均响应：{summary['avg_response_time_ms']}ms"
            )
        else:
            t0 = time.time()
            reply = await lapland_bot.get_response(user_id, message)
            rt = time.time() - t0
            qr = quality_asserter.assert_response_quality(reply, message, rt)
            if not qr["pass"]:
                logger.warning(f"质量告警 [{user_id}]: {qr['issues']}")

        # 按标点切分为短句，逐条发送
        sentences = _split_sentences(reply)
        for s in sentences:
            result = await wecom.send_text_message(user_id, s)
            logger.info(f"发送片段: {result}")
            await asyncio.sleep(random.uniform(0.75, 1.0))

    except Exception as e:
        logger.error(f"处理消息异常: {e}")


def _split_sentences(text: str) -> list[str]:
    """按标点符号将文本切分为短句列表"""
    parts = re.split(r'(……|\.{3,}|[。！？～!?][！？]*)', text)
    sentences = []
    for i in range(0, len(parts) - 1, 2):
        s = (parts[i] + parts[i + 1]).strip()
        if s:
            sentences.append(s)
    if len(parts) % 2 == 1:
        s = parts[-1].strip()
        if s:
            sentences.append(s)
    return sentences



@app.get("/health")

async def health():
    return {"status": "alive", "bot": "拉普兰德"}


if __name__ == "__main__":
    import uvicorn
    logger.add("logs/bot.log", rotation="1 day", retention="7 days")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=False,
    )



