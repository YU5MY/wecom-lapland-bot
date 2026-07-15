"""
主模块单元测试
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_endpoint():
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "alive"
    assert "拉普兰德" in data["bot"]


def test_callback_get_missing_params():
    """GET /callback 缺少必要参数应返回 422"""
    resp = client.get("/callback")
    assert resp.status_code == 422


def test_callback_get_with_partial_params():
    """只传部分参数也应返回 422"""
    resp = client.get("/callback?msg_signature=abc&timestamp=123")
    assert resp.status_code == 422


def test_callback_post_returns_ok():
    """POST /callback 缺少参数时正常应返回 422"""
    resp = client.post("/callback")
    assert resp.status_code == 422


def test_split_sentences_import():
    """验证 _split_sentences 函数可导入"""
    from main import _split_sentences
    assert callable(_split_sentences)


def test_callback_get_all_params_type_error():
    """GET /callback 传了全部参数但 echostr 格式异常走业务逻辑"""
    resp = client.get(
        "/callback?msg_signature=abc&timestamp=123&nonce=456&echostr=test"
    )
    # 由于没有真实 AES 密钥，会走异常路径返回 403
    assert resp.status_code in (200, 403)


def test_root_endpoint():
    resp = client.get("/")
    assert resp.status_code == 404
