import os
import logging
import asyncio
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class ModelConfig:
    provider: str
    model_name: str
    api_key_env: str

class ModelManager:
    """
    Manages interactions with various LLM providers and handles fallback logic.
    """
    
    AVAILABLE_MODELS = {
        "gemini-3-pro-preview": ModelConfig("google", "gemini-3-pro-preview", "GEMINI_API_KEY"),
        "gemini-2.0-flash-exp": ModelConfig("google", "gemini-2.0-flash-exp", "GEMINI_API_KEY"),
        "gemini-1.5-pro": ModelConfig("google", "gemini-1.5-pro", "GEMINI_API_KEY"),
        "gpt-4o": ModelConfig("openai", "gpt-4o", "OPENAI_API_KEY"),
        "gpt-4o-mini": ModelConfig("openai", "gpt-4o-mini", "OPENAI_API_KEY"),
        "claude-3-5-sonnet-20241022": ModelConfig("anthropic", "claude-3-5-sonnet-20241022", "ANTHROPIC_API_KEY"),
        "llama-3.1-sonar-large-128k-online": ModelConfig("perplexity", "llama-3.1-sonar-large-128k-online", "PERPLEXITY_API_KEY"),
    }

    def __init__(self):
        self.default_model = os.getenv("ORCHESTRATOR_MODEL", "gemini-3-pro-preview")
        self._clients = {}

    def get_available_models(self) -> List[Dict[str, str]]:
        """Returns a list of available models and their providers."""
        return [
            {"id": key, "provider": config.provider, "name": config.model_name}
            for key, config in self.AVAILABLE_MODELS.items()
        ]

    async def generate_content(self, prompt: str, model_id: Optional[str] = None) -> str:
        """
        Generates content using the specified model or default.
        """
        target_model = model_id or self.default_model
        
        if target_model not in self.AVAILABLE_MODELS:
            logger.warning(f"Model {target_model} not found, falling back to default {self.default_model}")
            target_model = self.default_model

        config = self.AVAILABLE_MODELS[target_model]
        
        try:
            if config.provider == "google":
                return await self._call_gemini(config.model_name, prompt)
            elif config.provider == "openai":
                return await self._call_openai(config.model_name, prompt)
            elif config.provider == "anthropic":
                return await self._call_anthropic(config.model_name, prompt)
            elif config.provider == "perplexity":
                return await self._call_perplexity(config.model_name, prompt)
            else:
                raise ValueError(f"Unsupported provider: {config.provider}")
        except Exception as e:
            logger.error(f"Error calling {target_model}: {e}")
            raise e

    async def _call_gemini(self, model_name: str, prompt: str) -> str:
        import google.generativeai as genai
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set")
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text

    async def _call_openai(self, model_name: str, prompt: str) -> str:
        from openai import AsyncOpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set")
            
        client = AsyncOpenAI(api_key=api_key)
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

    async def _call_anthropic(self, model_name: str, prompt: str) -> str:
        from anthropic import AsyncAnthropic
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not set")
            
        client = AsyncAnthropic(api_key=api_key)
        response = await client.messages.create(
            model=model_name,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.content[0].text

    async def _call_perplexity(self, model_name: str, prompt: str) -> str:
        from openai import AsyncOpenAI
        api_key = os.getenv("PERPLEXITY_API_KEY")
        if not api_key:
            raise ValueError("PERPLEXITY_API_KEY not set")
            
        # Perplexity uses OpenAI-compatible API
        client = AsyncOpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        response = await client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content

# Global instance
model_manager = ModelManager()
