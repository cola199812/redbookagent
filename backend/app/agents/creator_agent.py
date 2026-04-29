"""文案生成 Agent - M2 核心模块"""
import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from app.knowledge_base.knowledge_base_manager import KnowledgeBaseManager
from app.prompts import XHS_CREATOR_PROMPT, XHS_SYSTEM_PROMPT
from app.config import (
    LLM_PROVIDER, MINIMAX_API_KEY, MINIMAX_MODEL, MINIMAX_BASE_URL,
    DASHSCOPE_API_KEY, LLM_MODEL, LLM_TEMPERATURE
)
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class XHSContentGenerator:
    """小红书文案生成器"""

    def __init__(
        self,
        knowledge_base: Optional[KnowledgeBaseManager] = None,
        temperature: float = LLM_TEMPERATURE
    ):
        self.kb = knowledge_base or KnowledgeBaseManager()
        self.temperature = temperature

        # 根据 provider 选择配置
        if LLM_PROVIDER == "minimax" and MINIMAX_API_KEY:
            self.llm = ChatOpenAI(
                model=MINIMAX_MODEL,
                api_key=MINIMAX_API_KEY,
                base_url=MINIMAX_BASE_URL,
                temperature=temperature
            )
            logger.info(f"使用 MiniMax 模型: {MINIMAX_MODEL}")
        elif DASHSCOPE_API_KEY:
            self.llm = ChatOpenAI(
                model=LLM_MODEL,
                api_key=DASHSCOPE_API_KEY,
                base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                temperature=temperature
            )
            logger.info(f"使用通义千问模型: {LLM_MODEL}")
        else:
            logger.warning("未设置 API_KEY，文案生成功能将不可用")
            self.llm = None

    def generate(
        self,
        topic: str,
        style: str = "经验分享",
        keywords: Optional[List[str]] = None,
        extra: str = "",
        use_kb: bool = True
    ) -> Dict[str, Any]:
        """
        生成小红书文案

        返回: {
            "title": str,
            "content": str,
            "hashtags": List[str],
            "full_post": str
        }
        """
        if not self.llm:
            raise RuntimeError("LLM 未初始化，请检查 API_KEY")

        logger.info(f"开始生成文案: topic={topic}, style={style}")

        context = ""
        if use_kb:
            search_results = self.kb.search(
                query=f"{topic} {style}",
                k=5
            )
            if search_results:
                context = "\n\n".join([
                    f"- {r['content']}"
                    for r in search_results
                ])
                logger.info(f"从知识库检索到 {len(search_results)} 条相关知识")

        keywords_str = ", ".join(keywords) if keywords else "无"
        prompt = XHS_CREATOR_PROMPT.format(
            context=context or "无相关知识",
            topic=topic,
            style=style,
            keywords=keywords_str,
            extra=extra or "无"
        )

        messages = [
            SystemMessage(content=XHS_SYSTEM_PROMPT),
            HumanMessage(content=prompt)
        ]

        logger.info("正在调用 LLM 生成文案...")
        response = self.llm.invoke(messages)
        content = response.content

        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            elif "{" in content and "}" in content:
                start = content.find("{")
                end = content.rfind("}") + 1
                content = content[start:end]

            result = json.loads(content.strip())

            full_post = self._format_full_post(
                result.get("title", ""),
                result.get("content", ""),
                result.get("hashtags", [])
            )
            result["full_post"] = full_post

            logger.info(f"文案生成完成: {result.get('title', 'NO_TITLE')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始输出: {content}")
            return {
                "title": f"关于{topic}的分享",
                "content": content,
                "hashtags": [f"#{topic}", "#分享"],
                "full_post": content,
                "error": f"JSON解析失败: {str(e)}"
            }

    def _format_full_post(
        self,
        title: str,
        content: str,
        hashtags: List[str]
    ) -> str:
        """组合完整文案"""
        parts = [f"**{title}**\n" if title else ""]
        parts.append(content)
        if hashtags:
            parts.append("\n" + " ".join(hashtags))
        return "\n\n".join(parts)


class CreatorAgent:
    """文案创作Agent"""

    def __init__(self):
        self.generator = XHSContentGenerator()
        self.name = "小红书创作Agent"
        self.description = "根据主题和风格生成小红书文案"

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Agent入口"""
        try:
            topic = input_data.get("topic")
            if not topic:
                return {
                    "success": False,
                    "error": "缺少必需参数: topic"
                }

            result = self.generator.generate(
                topic=topic,
                style=input_data.get("style", "经验分享"),
                keywords=input_data.get("keywords"),
                extra=input_data.get("extra", "")
            )

            return {
                "success": True,
                "result": result
            }

        except Exception as e:
            logger.error(f"Agent执行失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_info(self) -> Dict[str, str]:
        """获取Agent信息"""
        return {
            "name": self.name,
            "description": self.description
        }
