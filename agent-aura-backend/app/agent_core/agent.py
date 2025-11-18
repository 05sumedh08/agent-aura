# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Core Agentic Reasoning Engine for Agent Aura.
Implements the Think-Act-Observe loop with Glass Box trajectory streaming.
"""

import json
import asyncio
from typing import AsyncGenerator, Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

from app.agent_core.tools import (
    get_student_data,
    analyze_student_risk,
    generate_intervention_plan,
    predict_intervention_success,
    generate_alert_email,
    track_student_progress,
    get_student_progress_timeline,
    export_progress_visualization_data
)


# ============================================================================
# Stream Event Types (Glass Box Trajectory)
# ============================================================================

@dataclass
class StreamThought:
    """Represents an agent's reasoning step."""
    type: str = "thought"
    content: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StreamAction:
    """Represents a tool call action."""
    type: str = "action"
    tool_name: str = ""
    arguments: dict | None = None
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StreamObservation:
    """Represents the result of an action."""
    type: str = "observation"
    content: str = ""
    success: bool = True
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StreamFinalResponse:
    """Represents the final response to the user."""
    type: str = "response"
    content: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# Tool Registry
# ============================================================================

TOOL_REGISTRY = {
    "get_student_data": {
        "function": get_student_data,
        "description": "Retrieve comprehensive student profile data",
        "parameters": ["student_id", "data_source"]
    },
    "analyze_student_risk": {
        "function": analyze_student_risk,
        "description": "Calculate risk score and categorize risk level",
        "parameters": ["student_id"]
    },
    "generate_intervention_plan": {
        "function": generate_intervention_plan,
        "description": "Create personalized intervention strategy",
        "parameters": ["risk_level"]
    },
    "predict_intervention_success": {
        "function": predict_intervention_success,
        "description": "Forecast intervention success probability",
        "parameters": ["risk_level"]
    },
    "generate_alert_email": {
        "function": generate_alert_email,
        "description": "Generate automated notification for stakeholders",
        "parameters": ["student_id"]
    },
    "track_student_progress": {
        "function": track_student_progress,
        "description": "Record student progress over time",
        "parameters": ["student_id", "risk_level", "risk_score", "student_name", "notes"]
    },
    "get_student_progress_timeline": {
        "function": get_student_progress_timeline,
        "description": "Retrieve historical progress timeline",
        "parameters": ["student_id"]
    },
    "export_progress_visualization_data": {
        "function": export_progress_visualization_data,
        "description": "Export progress data for visualization",
        "parameters": ["student_id", "format"]
    }
}


# ============================================================================
# Agent Core
# ============================================================================

class Agent:
    """
    Core Agent class implementing Think-Act-Observe loop.
    
    This is the heart of Agent Aura - a custom implementation of
    the agentic problem-solving process with full transparency.
    """
    
    def __init__(self, tools: Optional[List[str]] = None):
        """
        Initialize the Agent.
        
        Args:
            tools: List of tool names to enable (default: all tools)
        """
        self.tools = tools or list(TOOL_REGISTRY.keys())
        self.max_iterations = 10
        self.session_history = []
    
    def _prepare_context(self, goal: str, session_history: List[dict]) -> str:
        """
        Context Engineering: Prepare the system prompt with tools and history.
        
        Args:
            goal: User's goal/query
            session_history: Previous conversation history
            
        Returns:
            Formatted context string
        """
        # System prompt
        system_prompt = """You are Agent Aura, an AI agent specialized in K-12 student intervention analysis.

Your mission is to help identify at-risk students, generate interventions, and track outcomes.

You think step-by-step and use tools to accomplish your goals. For each step:
1. THINK about what you need to do next
2. ACT by calling a tool if needed
3. OBSERVE the result and continue

Available Tools:
"""
        
        # Add tool definitions
        for tool_name in self.tools:
            tool_info = TOOL_REGISTRY[tool_name]
            system_prompt += f"\n- {tool_name}: {tool_info['description']}"
            system_prompt += f"\n  Parameters: {', '.join(tool_info['parameters'])}"
        
        system_prompt += "\n\nWhen you need to use a tool, respond in this format:"
        system_prompt += '\n{\n  "thought": "Your reasoning here",\n  "action": "tool_name",\n  "arguments": {...}\n}'
        
        system_prompt += "\n\nWhen you have the final answer, respond in this format:"
        system_prompt += '\n{\n  "thought": "Summary of findings",\n  "final_response": "Your detailed response"\n}'
        
        # Add conversation history
        context = f"{system_prompt}\n\n=== Conversation History ===\n"
        for item in session_history[-5:]:  # Last 5 turns
            context += f"\nUser: {item.get('user', '')}"
            context += f"\nAgent: {item.get('agent', '')}"
        
        # Add current goal
        context += f"\n\n=== Current Request ===\nUser: {goal}\n"
        
        return context
    
    def _parse_llm_response(self, response: str) -> dict:
        """
        Parse LLM response to extract thought, action, or final response.
        
        Args:
            response: Raw LLM response
            
        Returns:
            Parsed dictionary with type indicator
        """
        try:
            # Try to parse as JSON
            parsed = json.loads(response.strip())
            return parsed
        except json.JSONDecodeError:
            # If not JSON, treat as a thought
            return {
                "thought": response,
                "final_response": response
            }
    
    def _execute_tool(self, tool_name: str, arguments: dict) -> Any:
        """
        Execute a tool with given arguments.
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments to pass to the tool
            
        Returns:
            Tool execution result
        """
        if tool_name not in TOOL_REGISTRY:
            return {"error": f"Tool '{tool_name}' not found"}
        
        tool_func = TOOL_REGISTRY[tool_name]["function"]
        
        try:
            # Call the tool
            result = tool_func(**arguments)
            return result
        except Exception as e:
            return {"error": str(e)}
    
    async def run(
        self,
        goal: str,
        session_history: Optional[List[dict]] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Execute the Think-Act-Observe loop with streaming.
        
        This is an async generator that yields each step of the agent's
        reasoning process, creating the "Glass Box" trajectory.
        
        Args:
            goal: User's goal/query
            session_history: Previous conversation history
            
        Yields:
            Stream events (thought, action, observation, response)
        """
        if session_history is None:
            session_history = []
        
        # Prepare context
        context = self._prepare_context(goal, session_history)
        
        iteration = 0
        conversation_context = context
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # THINK: Get agent's reasoning (simulated for now)
            thought_content = await self._simulate_llm_call(conversation_context)
            
            yield StreamThought(
                content=thought_content.get("thought", "Processing..."),
                timestamp=datetime.utcnow().isoformat()
            ).to_dict()
            
            await asyncio.sleep(0.1)  # Small delay for streaming effect
            
            # Check if this is the final response
            if "final_response" in thought_content:
                yield StreamFinalResponse(
                    content=thought_content["final_response"],
                    timestamp=datetime.utcnow().isoformat()
                ).to_dict()
                break
            
            # ACT: Execute tool if requested
            if "action" in thought_content and "arguments" in thought_content:
                tool_name = thought_content["action"]
                arguments = thought_content["arguments"]
                
                yield StreamAction(
                    tool_name=tool_name,
                    arguments=arguments,
                    timestamp=datetime.utcnow().isoformat()
                ).to_dict()
                
                await asyncio.sleep(0.1)
                
                # Execute the tool
                observation = self._execute_tool(tool_name, arguments)
                observation_str = json.dumps(observation, indent=2)
                
                # OBSERVE: Return tool result
                yield StreamObservation(
                    content=observation_str,
                    success="error" not in observation,
                    timestamp=datetime.utcnow().isoformat()
                ).to_dict()
                
                # Update context with observation
                conversation_context += f"\n\nTool Result: {observation_str}\n"
                
                await asyncio.sleep(0.1)
            else:
                # No action requested, treat as final response
                yield StreamFinalResponse(
                    content=thought_content.get("thought", "Process completed"),
                    timestamp=datetime.utcnow().isoformat()
                ).to_dict()
                break
    
    async def _simulate_llm_call(self, context: str) -> dict:
        """
        Simulate LLM reasoning (placeholder for actual Gemini API call).
        
        In production, this would call the Gemini API with the context.
        For now, we'll create a simple rule-based response.
        
        Args:
            context: Prepared context string
            
        Returns:
            Parsed LLM response
        """
        # Simple keyword-based routing for demonstration
        if "analyze" in context.lower() and "student" in context.lower():
            # Extract student ID from context
            import re
            match = re.search(r'S\d{3}', context)
            if match:
                student_id = match.group(0)
                return {
                    "thought": f"I need to analyze the risk level for student {student_id}. First, I'll get their data.",
                    "action": "get_student_data",
                    "arguments": {"student_id": student_id, "data_source": "./data/student_data.csv"}
                }
        
        # Default response
        return {
            "thought": "I understand you want help with student intervention analysis.",
            "final_response": "Agent Aura is ready. Please provide a specific student ID (e.g., S001) to analyze risk levels and generate interventions."
        }
