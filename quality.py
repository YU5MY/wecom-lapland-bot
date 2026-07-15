"""
质量保障模块
- 响应质量断言（关键词命中、异常模式、内容完整性）
- 质量指标追踪与汇总
"""
import re
import time
from dataclasses import dataclass, field


@dataclass
class QualityMetrics:
    """质量指标原始数据"""
    n_calls: int = 0
    n_failures: int = 0
    total_response_time: float = 0.0


class QualityAsserter:
    """响应质量断言器

    对 AI 回复做轻量级质量门禁检测：
    - 内容完整性：空回复/过短回复
    - 异常模式：AI 常见的逃脱话术
    - 响应时间：超过阈值记录
    """

    # 异常模式 —— 出现这些说明回复偏离了拉普兰德人设
    ANOMALY_PATTERNS = [
        r'(抱歉|对不起|我无法|我不能|我不确定|我不清楚|我没有办法)',
        r'(我是AI|我是一个AI|作为AI|作为一个人工智能|作为一个AI)',
        r'(很抱歉|不好意思|非常抱歉|深感抱歉)',
    ]

    RESPONSE_TIME_WARN_MS = 5000  # 超过5秒告警

    def __init__(self):
        self.metrics = QualityMetrics()

    def assert_response_quality(
        self, reply: str, user_message: str, response_time: float
    ) -> dict:
        """对单条回复做质量断言，返回质检报告"""
        self.metrics.n_calls += 1
        self.metrics.total_response_time += response_time

        issues = []

        # 1. 内容完整性
        stripped = reply.strip()
        if not stripped:
            issues.append("empty_response")
        elif len(stripped) < 3:
            issues.append("response_too_short")

        # 2. 异常模式检测
        for pattern in self.ANOMALY_PATTERNS:
            if re.search(pattern, reply):
                issues.append(f"anomaly: '{pattern}'")

        # 3. 响应时间预警
        rt_ms = response_time * 1000
        if rt_ms > self.RESPONSE_TIME_WARN_MS:
            issues.append(f"slow_response: {rt_ms:.0f}ms")

        if issues:
            self.metrics.n_failures += 1

        return {
            "pass": len(issues) == 0,
            "issues": issues,
            "response_time_ms": round(rt_ms),
            "response_length": len(reply),
        }

    def summary(self) -> dict:
        """获取累计质量汇总"""
        total = max(self.metrics.n_calls, 1)
        return {
            "total_calls": self.metrics.n_calls,
            "failure_count": self.metrics.n_failures,
            "pass_rate": round(
                (self.metrics.n_calls - self.metrics.n_failures) / total * 100, 1
            ),
            "avg_response_time_ms": round(
                self.metrics.total_response_time / total * 1000, 1
            ),
        }


# 全局单例
quality_asserter = QualityAsserter()
