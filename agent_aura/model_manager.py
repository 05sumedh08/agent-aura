# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Model Manager for Agent Aura.
Handles multi-model fallback when primary models fail or are overloaded.
"""

import logging
from typing import Optional
from google.adk.agents.llm_agent import LlmAgent
__all__ = []
from agent_aura.config import config

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Manages model selection with automatic fallback support.
    
    When the primary model (Gemini) fails due to overload or availability issues,
    automatically tries fallback models in order of preference.
    """
    
    def __init__(self, primary_model: Optional[str] = None):
        """
        Initialize ModelManager.
        
        Args:
            primary_model: Primary model name (default from config)
        """
        self.primary_model = primary_model or config.orchestrator_model
        self.fallback_models = config.fallback_models if config.enable_fallback else []
        self.current_model = self.primary_model
        self.failed_models = set()
        
    def get_model_for_agent(self, agent_name: str = "agent") -> str:
        """
        Get the best available model for an agent.
        
        Args:
            agent_name: Name of the agent requesting the model
            
        Returns:
            Model name to use
        """
        # Try primary model first if not failed
        if self.primary_model not in self.failed_models:
            logger.info(f"[{agent_name}] Using primary model: {self.primary_model}")
            return self.primary_model
        
        # Try fallback models
        for fallback_model in self.fallback_models:
            if fallback_model not in self.failed_models:
                logger.warning(
                    f"[{agent_name}] Primary model unavailable. "
                    f"Falling back to: {fallback_model}"
                )
                self.current_model = fallback_model
                return fallback_model
        
        # If all models failed, reset and try primary again
        logger.error(
            f"[{agent_name}] All models failed. Resetting and retrying primary model."
        )
        self.failed_models.clear()
        return self.primary_model
    
    def mark_model_failed(self, model_name: str, error: Exception):
        """
        Mark a model as failed (temporarily unavailable).
        
        Args:
            model_name: Name of the failed model
            error: Exception that caused the failure
        """
        self.failed_models.add(model_name)
        logger.error(f"Model {model_name} marked as failed: {str(error)}")
        
        # Log which models are still available
        available = [m for m in self.fallback_models if m not in self.failed_models]
        if available:
            logger.info(f"Available fallback models: {', '.join(available)}")
        else:
            logger.warning("No fallback models available!")
    
    def reset_failures(self):
        """Reset all model failure states."""
        self.failed_models.clear()
        self.current_model = self.primary_model
        logger.info("Model failure states reset")
    
    def get_model_config(self, model_name: str) -> dict:
        """
        Get configuration for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Configuration dict with API key and provider info
        """
        # Determine provider and API key
        if model_name.startswith("gemini"):
            return {
                "provider": "google",
                "api_key": config.gemini_api_key,
                "model": model_name
            }
        elif model_name.startswith("gpt"):
            return {
                "provider": "openai",
                "api_key": config.openai_api_key,
                "model": model_name
            }
        elif model_name.startswith("claude"):
            return {
                "provider": "anthropic",
                "api_key": config.anthropic_api_key,
                "model": model_name
            }
        else:
            # Default to Gemini
            return {
                "provider": "google",
                "api_key": config.gemini_api_key,
                "model": model_name
            }


# Global model manager instance
model_manager = ModelManager()


def create_agent_with_fallback(
    name: str,
    instruction: str,
    tools: Optional[list] = None,
    model_override: Optional[str] = None
 ) -> LlmAgent:
    """
    Create an LLMAgent with automatic model fallback support.
    
    Args:
        name: Agent name
        instruction: Agent instruction/prompt
        tools: List of tools for the agent
        model_override: Optional model override
        
    Returns:
        Configured LLMAgent
    """
    # Get the best available model
    model_name = model_override or model_manager.get_model_for_agent(name)
    model_config = model_manager.get_model_config(model_name)
    
    # Log model selection
    logger.info(
        f"Creating agent '{name}' with model: {model_name} "
        f"(provider: {model_config['provider']})"
    )
    
    # For now, only Gemini is supported by ADK
    # Future: Add OpenAI/Anthropic support when ADK adds it
    if model_config["provider"] != "google":
        logger.warning(
            f"Provider '{model_config['provider']}' not yet supported by ADK. "
            f"Falling back to Gemini."
        )
        model_name = "gemini-1.5-pro"
    
    return LlmAgent(
        name=name,
        model=model_name,
        instruction=instruction,
        tools=tools or []
    )
