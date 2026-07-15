"""
AI 测试用例生成模块
- 接收需求描述，调用 LLM 生成结构化测试用例
- 支持指定测试用例数量
"""
from openai import AsyncOpenAI
from loguru import logger
from config import config

TC_SYSTEM_PROMPT = """你是一个专业的测试用例生成工程师。根据用户描述的需求，生成结构化测试用例。

请严格按以下格式输出：

## 测试用例

### TC-001: 测试标题
- **前置条件**: 前置条件描述
- **测试步骤**:
  1. 步骤1
  2. 步骤2
- **预期结果**: 预期结果描述
- **优先级**: P0/P1/P2/P3

### TC-002: 测试标题
...
"""


class TestCaseGenerator:
    """测试用例生成器"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
        self.model = config.OPENAI_MODEL

    async def generate(self, description: str, count: int = 5) -> str:
        """根据需求描述生成测试用例"""
        try:
            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": TC_SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": f"请为以下需求生成{count}个测试用例：\n{description}",
                    },
                ],
                temperature=0.3,
                max_tokens=2000,
            )
            return (
                resp.choices[0].message.content
                or "……生成失败了。需求太模糊了？"
            )
        except Exception as e:
            logger.error(f"测试用例生成失败: {e}")
            return f"呵呵——出问题了：{e}"


# 全局单例
tc_generator = TestCaseGenerator()
