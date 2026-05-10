import asyncio
import json
import time
from dataclasses import dataclass
from enum import Enum
from typing import Any, TypeVar

from openai import AsyncOpenAI
from pydantic import BaseModel

from meshmind.core.config import settings

T = TypeVar("T", bound=BaseModel)


class TaskType(str, Enum):
    CONVERSATION_EXTRACTION = "conversation_extraction"
    DOCUMENT_ANALYSIS = "document_analysis"
    AGENT_THINK = "agent_think"
    CONFLICT_JUDGMENT = "conflict_judgment"
    MAINTENANCE_JUDGMENT = "maintenance_judgment"
    FINAL_ANSWER = "final_answer"
    SIMILARITY_FILTER = "similarity_filter"
    SIMPLE_CLASSIFY = "simple_classify"
    RELATION_CONFIRM = "relation_confirm"


TASK_MODEL_MAP: dict[TaskType, str] = {
    TaskType.CONVERSATION_EXTRACTION: settings.llm_pro_model,
    TaskType.DOCUMENT_ANALYSIS: settings.llm_pro_model,
    TaskType.AGENT_THINK: settings.llm_pro_model,
    TaskType.CONFLICT_JUDGMENT: settings.llm_pro_model,
    TaskType.MAINTENANCE_JUDGMENT: settings.llm_pro_model,
    TaskType.FINAL_ANSWER: settings.llm_pro_model,
    TaskType.SIMILARITY_FILTER: settings.llm_flash_model,
    TaskType.SIMPLE_CLASSIFY: settings.llm_flash_model,
    TaskType.RELATION_CONFIRM: settings.llm_flash_model,
}


@dataclass
class Usage:
    prompt_tokens: int
    completion_tokens: int


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Usage
    latency_ms: int


class LLMError(Exception):
    pass


class LLMHarness:
    def __init__(self, base_url: str | None = None, api_key: str | None = None):
        self.client = AsyncOpenAI(
            base_url=base_url or settings.deepseek_base_url,
            api_key=api_key or settings.deepseek_api_key,
        )

    def _resolve_model(self, task: TaskType) -> str:
        return TASK_MODEL_MAP.get(task, settings.llm_pro_model)

    async def call(
        self,
        messages: list[dict],
        task: TaskType,
        *,
        max_tokens: int = 4096,
        temperature: float = 0.7,
        use_json: bool = False,
        retries: int = 3,
    ) -> LLMResponse:
        model = self._resolve_model(task)
        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        if use_json:
            kwargs["response_format"] = {"type": "json_object"}

        last_error = None
        for attempt in range(retries):
            try:
                start = time.monotonic()
                completion = await asyncio.wait_for(
                    self.client.chat.completions.create(**kwargs),
                    timeout=60,
                )
                latency = int((time.monotonic() - start) * 1000)

                choice = completion.choices[0]
                content = choice.message.content or ""

                return LLMResponse(
                    content=content,
                    model=model,
                    usage=Usage(
                        prompt_tokens=completion.usage.prompt_tokens if completion.usage else 0,
                        completion_tokens=completion.usage.completion_tokens if completion.usage else 0,
                    ),
                    latency_ms=latency,
                )
            except Exception as e:
                last_error = e
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)

        raise LLMError(f"LLM call failed after {retries} retries: {last_error}")

    async def call_structured(
        self,
        messages: list[dict],
        task: TaskType,
        output_model: type[T],
        *,
        max_tokens: int = 4096,
    ) -> T:
        response = await self.call(
            messages=messages,
            task=task,
            max_tokens=max_tokens,
            temperature=0.3,
            use_json=True,
        )
        try:
            data = json.loads(response.content)
            return output_model.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            raise LLMError(f"Failed to parse structured output: {e}\nContent: {response.content[:500]}")
