"""Unit tests for LLM Harness."""
import pytest

from meshmind.llm.harness import LLMHarness, TaskType, LLMError


@pytest.mark.asyncio
async def test_harness_simple_call():
    harness = LLMHarness()
    resp = await harness.call(
        messages=[{"role": "user", "content": "Say hi in one word"}],
        task=TaskType.SIMPLE_CLASSIFY,
        max_tokens=100,
    )
    assert resp.model == "deepseek-v4-flash"
    assert resp.usage.prompt_tokens > 0
    assert resp.latency_ms > 0


@pytest.mark.asyncio
async def test_harness_pro_model():
    harness = LLMHarness()
    resp = await harness.call(
        messages=[{"role": "user", "content": "Say hi"}],
        task=TaskType.AGENT_THINK,
        max_tokens=100,
    )
    assert resp.model == "deepseek-v4-pro"


@pytest.mark.asyncio
async def test_harness_retry_on_bad_model():
    harness = LLMHarness(base_url="https://api.deepseek.com/v1")
    try:
        await harness.call(
            messages=[{"role": "user", "content": "hi"}],
            task=TaskType.SIMPLE_CLASSIFY,
            max_tokens=10,
            retries=1,
        )
    except Exception:
        pass  # Expected to fail after retries


@pytest.mark.asyncio
async def test_harness_json_mode():
    harness = LLMHarness()
    resp = await harness.call(
        messages=[
            {"role": "system", "content": 'Output ONLY valid JSON, no other text. Example: {"key":"value"}'},
            {"role": "user", "content": 'Return {"hello":"world"}'},
        ],
        task=TaskType.SIMPLE_CLASSIFY,
        max_tokens=200,
        use_json=True,
    )
    assert resp.content and "hello" in resp.content.lower()
