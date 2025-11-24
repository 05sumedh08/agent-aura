# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Configuration module for Agent Aura.
Manages model selection, API keys, and system parameters.
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentAuraConfig:
    """Configuration for Agent Aura multi-agent system."""
    
    # Primary Model Configuration - Gemini models with fallback support
    orchestrator_model: str = "gemini-3-pro-preview"  # Primary: Gemini 3 Pro Preview
    worker_model: str = "gemini-3-pro-preview"  # Primary: Gemini 3 Pro Preview
    
    # Fallback Models (used when primary model fails/overloaded)
    fallback_models: Optional[list] = None  # Will be set in __post_init__
    enable_fallback: bool = True  # Enable automatic fallback to other models
    
    # API Configuration - Multiple providers
    gemini_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None  # For GPT-4 fallback
    anthropic_api_key: Optional[str] = None  # For Claude fallback
    
    # Risk Thresholds
    critical_risk_threshold: float = 0.90
    high_risk_threshold: float = 0.80
    moderate_risk_threshold: float = 0.60
    low_risk_threshold: float = 0.30
    
    # Intervention Parameters
    max_iterations: int = 3
    confidence_level: int = 85
    
    # Data Configuration
    data_directory: str = "./data"
    output_directory: str = "./output"
    
    # Logging Configuration
    log_level: str = "INFO"
    log_file: str = "agent_aura.log"
    
    # Rate Limiting Configuration
    max_requests_per_minute: int = 10  # Conservative rate limit
    retry_delay_seconds: int = 2  # Delay between retries
    max_retries: int = 3  # Maximum retry attempts
    
    def __post_init__(self):
        """Load configuration from environment variables."""
        # Try to get API keys from environment
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Allow override from environment for models
        self.orchestrator_model = os.getenv("ORCHESTRATOR_MODEL", self.orchestrator_model)
        self.worker_model = os.getenv("WORKER_MODEL", self.worker_model)
        
        # Set up fallback model chain (try in order when primary fails)
        if self.fallback_models is None:
            self.fallback_models = [
                "gemini-3-pro-preview",  # Gemini 3 Pro Preview
                "gemini-2.0-flash-exp",  # Gemini 2.0 Flash
                "gemini-1.5-pro",  # Gemini Pro (more stable)
                "gemini-1.5-flash-8b",  # Gemini Flash 8B (lightweight)
                "gpt-4o-mini",  # OpenAI GPT-4o mini (requires OPENAI_API_KEY)
                "claude-3-5-sonnet-20241022",  # Anthropic Claude (requires ANTHROPIC_API_KEY)
            ]
        
        # Create directories if they don't exist
        os.makedirs(self.data_directory, exist_ok=True)
        os.makedirs(self.output_directory, exist_ok=True)


# Global configuration instance
config = AgentAuraConfig()
