from langchain_core.callbacks import CallbackManagerForLLMRun, AsyncCallbackManagerForLLMRun
from langchain_core.language_models import BaseLLM,LLM
from langchain_core.outputs import LLMResult, Generation
from typing import Any, List, Optional, Mapping
import requests


class CustomAPI_LLM(LLM):
    api_url: str
    api_key: str  # Your API key

    def _call(self, prompt: str, stop: list[str] | None = None, run_manager: CallbackManagerForLLMRun | None = None,
              **kwargs: Any) -> str:
        pass

    async def _acall(self, prompt: str, stop: list[str] | None = None,
                     run_manager: AsyncCallbackManagerForLLMRun | None = None, **kwargs: Any) -> str:
        return await super()._acall(prompt, stop, run_manager, **kwargs)



