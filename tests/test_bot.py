"""
Bot 模块单元测试
"""
import pytest
from bot import LaplandBot, LAPLAND_SYSTEM_PROMPT
from main import _split_sentences


# ─── 句子切分测试 ───

def test_split_sentences_basic():
    text = "呵——有点意思。你想让我做什么？没问题！"
    parts = _split_sentences(text)
    assert len(parts) >= 2
    assert all(p.strip() for p in parts)


def test_split_sentences_with_ellipsis():
    text = "呵呵……你确定？……行吧。"
    parts = _split_sentences(text)
    assert len(parts) >= 1


def test_split_sentences_single():
    text = "没意思。"
    parts = _split_sentences(text)
    assert len(parts) == 1
    assert parts[0] == "没意思。"


def test_split_sentences_no_punctuation():
    text = "就这"
    parts = _split_sentences(text)
    assert len(parts) == 1


def test_split_sentences_with_newline():
    text = "第一句。\n第二句！"
    parts = _split_sentences(text)
    assert len(parts) >= 2


def test_split_sentences_empty():
    parts = _split_sentences("")
    assert len(parts) == 0


# ─── 上下文管理测试 ───

def test_bot_add_and_get_history():
    bot = LaplandBot()
    bot._add_message("u1", "user", "你好")
    bot._add_message("u1", "assistant", "呵呵，你好啊。")
    bot._add_message("u2", "user", "测试")

    history = bot._get_history("u1")
    assert len(history) == 2

    history2 = bot._get_history("u2")
    assert len(history2) == 1


def test_bot_clear_history():
    bot = LaplandBot()
    bot._add_message("u1", "user", "你好")
    bot.clear_history("u1")
    assert len(bot._get_history("u1")) == 0


def test_bot_history_preserves_order():
    bot = LaplandBot()
    bot._add_message("u1", "user", "第一句")
    bot._add_message("u1", "assistant", "第一句回复")
    bot._add_message("u1", "user", "第二句")

    history = bot._get_history("u1")
    assert len(history) == 3
    assert history[0]["content"] == "第一句"
    assert history[2]["content"] == "第二句"


def test_bot_history_window_limit():
    bot = LaplandBot()
    for i in range(150):
        bot._add_message("u1", "user", f"msg_{i}")
    assert len(bot._get_history("u1")) == 100


def test_bot_unknown_user_returns_empty():
    bot = LaplandBot()
    assert bot._get_history("nobody") == []


# ─── System Prompt 内容测试 ───

def test_system_prompt_contains_core_elements():
    assert "拉普兰德" in LAPLAND_SYSTEM_PROMPT
    assert "鲁珀" in LAPLAND_SYSTEM_PROMPT
    assert "荒芜形态" in LAPLAND_SYSTEM_PROMPT


def test_system_prompt_contains_style_guidelines():
    assert "短句为主" in LAPLAND_SYSTEM_PROMPT
    assert "中文回复" in LAPLAND_SYSTEM_PROMPT
    assert "简练" in LAPLAND_SYSTEM_PROMPT


def test_system_prompt_contains_lapland_traits():
    assert "亲爱的" in LAPLAND_SYSTEM_PROMPT
    assert "撕碎" in LAPLAND_SYSTEM_PROMPT or "拆掉" in LAPLAND_SYSTEM_PROMPT
