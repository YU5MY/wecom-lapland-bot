"""
企业微信 API 封装
- 获取 AccessToken
- 发送应用消息（文本）
- 回调消息解密 / 响应加密
"""
import hashlib
import time
import xml.etree.ElementTree as ET
import xmltodict
import httpx
from loguru import logger
from config import config

# ──────────── AccessToken ────────────

_token_cache: dict = {"token": None, "expires_at": 0}


async def get_access_token() -> str:
    if _token_cache["token"] and time.time() < _token_cache["expires_at"] - 60:
        return _token_cache["token"]

    url = "https://qyapi.weixin.qq.com/cgi-bin/gettoken"
    params = {
        "corpid": config.WECOM_CORP_ID,
        "corpsecret": config.WECOM_CORP_SECRET,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        data = resp.json()
        if data.get("errcode") != 0:
            raise RuntimeError(f"获取 token 失败: {data}")
        _token_cache["token"] = data["access_token"]
        _token_cache["expires_at"] = time.time() + data["expires_in"]
        logger.info("AccessToken 已刷新")
        return _token_cache["token"]


async def send_text_message(user_id: str, content: str) -> dict:
    token = await get_access_token()
    url = f"https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={token}"
    payload = {
        "touser": user_id,
        "msgtype": "text",
        "agentid": config.WECOM_AGENT_ID,
        "text": {"content": content},
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(url, json=payload)
        data = resp.json()
        if data.get("errcode") != 0:
            logger.error(f"发送消息失败: {data}")
        return data


# ──────────── 回调验证 ────────────


def verify_url(msg_signature: str, timestamp: str, nonce: str, echo_str: str) -> str:
    from WXBizMsgCrypt import WXBizMsgCrypt
    wxcpt = WXBizMsgCrypt(config.WECOM_TOKEN, config.WECOM_ENCODING_AES_KEY, config.WECOM_CORP_ID)
    ret, decrypted = wxcpt.VerifyURL(msg_signature, timestamp, nonce, echo_str)
    if ret != 0:
        raise RuntimeError(f"URL 验证失败: errcode={ret}")
    return decrypted


def decrypt_message(msg_signature: str, timestamp: str, nonce: str, xml_body: str) -> dict:
    from WXBizMsgCrypt import WXBizMsgCrypt
    wxcpt = WXBizMsgCrypt(config.WECOM_TOKEN, config.WECOM_ENCODING_AES_KEY, config.WECOM_CORP_ID)
    ret, decrypted_xml = wxcpt.DecryptMsg(xml_body, msg_signature, timestamp, nonce)
    if ret != 0:
        raise RuntimeError(f"消息解密失败: errcode={ret}")
    return xmltodict.parse(decrypted_xml)


def encrypt_reply(msg: str, nonce: str, timestamp: str) -> str:
    from WXBizMsgCrypt import WXBizMsgCrypt
    wxcpt = WXBizMsgCrypt(config.WECOM_TOKEN, config.WECOM_ENCODING_AES_KEY, config.WECOM_CORP_ID)
    ret, encrypted_xml = wxcpt.EncryptMsg(msg, nonce, timestamp)
    if ret != 0:
        raise RuntimeError(f"消息加密失败: errcode={ret}")
    return encrypted_xml


def generate_timestamp() -> str:
    return str(int(time.time()))


def generate_nonce() -> str:
    import random
    return str(random.randint(100000, 999999))
