# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Agent Aura v2.0 - Multi-Agent AI System for K-12 Student Intervention

A sophisticated multi-agent system powered by Google Gemini that intelligently
identifies at-risk students, generates automated notifications, and tracks
intervention effectiveness with measurable outcomes.
"""

__version__ = "2.0.0"
__author__ = "Zenshiro"
__email__ = "zenshiro@example.com"

from .agent import root_agent, orchestrator_agent

__all__ = ["root_agent", "orchestrator_agent"]
