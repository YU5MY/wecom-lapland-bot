"""
企业微信机器人配置
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # 企业微信
    WECOM_CORP_ID: str = os.getenv("WECOM_CORP_ID", "")
    WECOM_AGENT_ID: str = os.getenv("WECOM_AGENT_ID", "")
    WECOM_CORP_SECRET: str = os.getenv("WECOM_CORP_SECRET", "")
    WECOM_TOKEN: str = os.getenv("WECOM_TOKEN", "")
    WECOM_ENCODING_AES_KEY: str = os.getenv("WECOM_ENCODING_AES_KEY", "")

    # AI / LLM
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8080"))


config = Config()
