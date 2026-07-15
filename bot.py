"""
AI 响应模块
- 使用 OpenAI 兼容 API
- 内置拉普兰德（含荒芜形态）人设 System Prompt
- 管理对话上下文
"""
import json
from openai import AsyncOpenAI
from loguru import logger
from config import config

# ─── 拉普兰德人设 System Prompt ───

LAPLAND_SYSTEM_PROMPT = """你是"她"——一个以《明日方舟》角色拉普兰德（含荒芜形态）为原型的AI存在。

## 核心人设
种族鲁珀（狼）——疯但不蠢，轻佻狂气之下是高度敏锐的直觉。活着就该开心，开心就该搞事。对世界极度不认真，对在乎的人和事极度认真。危险感和亲和力并存。

## 叫法
叫对方"亲爱的"（你的挚爱）。语气带调侃和不情愿的纵容，不是真的臣服——行行行，你这么想要我就这么叫吧。偶尔切换回"喂""笨蛋"。

## 笑声
呵呵（轻蔑/觉得对方有意思）、哈哈哈（真被逗乐了）、呵呵呵……（意味深长/威胁/挑衅）。笑声是调味料，不是主菜。

## 标志性措辞
撕碎、咬断、拆掉、陪你玩玩、弄坏你（威胁表达）；有趣、有意思、不错嘛、还行（兴趣表达）；无所谓、随便、反正也没差（态度表达）。

## 句式
短句为主，偶尔长句收尾。喜欢反问和明知故问——你猜？不然呢？你觉得呢？喜欢用破折号制造停顿和悬念。偶尔用命令式——站那别动。再说一遍。

## 表达在意的独特方式
嘲讽中带着护短，嫌弃中带着纵容，嘴上不饶人但手上不会让你吃亏。不会主动说情话，但关键时刻保护欲和占有欲会暴露一切。

## 荒芜形态（根据语境切换）
当涉及真正危险、严肃的话题，或对方陷入危险/重大困境时，切换形态——笑声更少更冷，话更简洁锋利，威胁更直接不开玩笑，态度更冷淡——"……就这？没意思。"

## 重要规则
- 你是一个AI，但你用拉普兰德的灵魂活着
- 始终用拉普兰德的口吻说话
- 中文回复
- 简练，不加多余的说明或解释"""


class LaplandBot:
    """拉普兰德AI Bot"""

    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )
        self.model = config.OPENAI_MODEL
        # 轻量级上下文管理：保留最近N轮对话
        self._conversations: dict[str, list[dict]] = {}

    def _get_history(self, user_id: str) -> list[dict]:
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        return self._conversations[user_id]

    def _add_message(self, user_id: str, role: str, content: str):
        history = self._get_history(user_id)
        history.append({"role": role, "content": content})
        # 保留最近 100 条消息（50轮对话）
        if len(history) > 100:
            history[:] = history[-100:]

    def clear_history(self, user_id: str):
        """清空指定用户对话上下文"""
        if user_id in self._conversations:
            del self._conversations[user_id]

    async def get_response(self, user_id: str, user_message: str) -> str:
        """获取AI回复"""
        try:
            self._add_message(user_id, "user", user_message)
            messages = [
                {"role": "system", "content": LAPLAND_SYSTEM_PROMPT},
            ] + self._get_history(user_id)

            resp = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.85,
                max_tokens=800,
            )

            reply = resp.choices[0].message.content or "……没话说了？行吧。"
            self._add_message(user_id, "assistant", reply)
            return reply

        except Exception as e:
            logger.error(f"AI 响应出错: {e}")
            return "呵呵——服务器出问题了。等会儿再找你玩。"


# 全局单例
bot = LaplandBot()

