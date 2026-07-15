"""
测试用例生成模块单元测试
"""
import pytest
from testcase import TC_SYSTEM_PROMPT


def test_tc_system_prompt_contains_key_elements():
    assert "测试用例" in TC_SYSTEM_PROMPT
    assert "TC-" in TC_SYSTEM_PROMPT
    assert "测试步骤" in TC_SYSTEM_PROMPT
    assert "预期结果" in TC_SYSTEM_PROMPT
    assert "优先级" in TC_SYSTEM_PROMPT


def test_tc_system_prompt_has_structure():
    assert "前置条件" in TC_SYSTEM_PROMPT


def test_tc_generator_import():
    from testcase import TestCaseGenerator
    assert TestCaseGenerator is not None


def test_tc_generator_has_generate_method():
    from testcase import TestCaseGenerator
    assert hasattr(TestCaseGenerator, "generate")
    assert callable(TestCaseGenerator.generate)


def test_tc_generator_client_init():
    """验证实例化不会报错（不含网络调用）"""
    from testcase import TestCaseGenerator
    gen = TestCaseGenerator()
    assert gen.model is not None
    assert gen.client is not None
