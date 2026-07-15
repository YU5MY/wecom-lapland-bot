"""
质量断言模块单元测试
"""
import pytest
from quality import QualityAsserter


def test_quality_pass():
    qa = QualityAsserter()
    result = qa.assert_response_quality(
        "呵——有点意思。你想让我做什么？", "你好", 0.5
    )
    assert result["pass"] is True
    assert len(result["issues"]) == 0


def test_quality_empty_response():
    qa = QualityAsserter()
    result = qa.assert_response_quality("", "你好", 0.3)
    assert result["pass"] is False
    assert "empty_response" in result["issues"]


def test_quality_too_short():
    qa = QualityAsserter()
    result = qa.assert_response_quality("嗯", "你好", 0.3)
    assert result["pass"] is False
    assert "response_too_short" in result["issues"]


def test_quality_anomaly_detected():
    qa = QualityAsserter()
    result = qa.assert_response_quality("抱歉，我无法回答这个问题。", "test", 0.5)
    assert result["pass"] is False
    assert any("anomaly" in issue for issue in result["issues"])


def test_quality_slow_response_warn():
    qa = QualityAsserter()
    result = qa.assert_response_quality("还行。", "你好", 6.0)
    assert "slow_response" in result["issues"]


def test_quality_summary():
    qa = QualityAsserter()
    qa.assert_response_quality("不错嘛。", "你好", 0.5)
    qa.assert_response_quality("嗯", "你好", 0.3)
    summary = qa.summary()
    assert summary["total_calls"] == 2
    assert summary["failure_count"] >= 1
    assert summary["pass_rate"] <= 50.0


def test_quality_metrics_tracking():
    qa = QualityAsserter()
    for _ in range(10):
        qa.assert_response_quality("呵，行啊。", "你好", 0.3)
    summary = qa.summary()
    assert summary["total_calls"] == 10
    assert summary["avg_response_time_ms"] == 300


def test_quality_anomaly_patterns_loaded():
    qa = QualityAsserter()
    assert len(qa.ANOMALY_PATTERNS) >= 3


def test_quality_response_time_ms():
    qa = QualityAsserter()
    result = qa.assert_response_quality("好。", "hi", 1.234)
    assert result["response_time_ms"] == 1234


def test_quality_response_length():
    qa = QualityAsserter()
    result = qa.assert_response_quality("呵——有点意思。", "hi", 0.5)
    assert result["response_length"] == 8
