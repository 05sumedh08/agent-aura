# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Multi-Agent Orchestrator for Agent Aura.
Coordinates parallel execution of 4 specialized agents with Glass Box visibility.
"""

import asyncio
import json
from typing import AsyncGenerator, Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

from app.agent_core.tools import (
    get_student_data,
    analyze_student_risk,
    generate_intervention_plan,
    predict_intervention_success
)


@dataclass
class AgentStartEvent:
    """Event when an agent starts execution."""
    type: str = "agent_start"
    agent_name: str = ""
    description: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AgentCompleteEvent:
    """Event when an agent completes execution."""
    type: str = "agent_complete"
    agent_name: str = ""
    result: Optional[dict] = None
    success: bool = True
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class OrchestratorThought:
    """Orchestrator reasoning event."""
    type: str = "orchestrator_thought"
    content: str = ""
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FinalReport:
    """Final comprehensive report."""
    type: str = "final_report"
    content: str = ""
    student_data: Optional[dict] = None
    risk_analysis: Optional[dict] = None
    intervention_plan: Optional[dict] = None
    outcome_prediction: Optional[dict] = None
    timestamp: str = ""
    
    def to_dict(self) -> dict:
        return asdict(self)


class MultiAgentOrchestrator:
    """
    Orchestrates 4 specialized agents working in parallel.
    
    Agents:
    1. Data Collection Agent - Retrieves student information
    2. Risk Analysis Agent - Evaluates student risk level
    3. Intervention Planning Agent - Designs intervention strategies
    4. Outcome Prediction Agent - Forecasts intervention success
    """
    
    def __init__(self, enabled_agents: Optional[List[str]] = None):
        """
        Initialize orchestrator with optional agent filtering.
        
        Args:
            enabled_agents: List of agent names to enable. If None, all agents enabled.
        """
        self.all_agents = [
            "data_collection",
            "risk_analysis", 
            "intervention_planning",
            "outcome_prediction"
        ]
        self.enabled_agents = enabled_agents or self.all_agents
        
    async def run(
        self,
        student_id: str,
        session_history: Optional[List[dict]] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Execute multi-agent analysis with parallel processing.
        
        Args:
            student_id: Student ID to analyze
            session_history: Previous conversation history
            
        Yields:
            Stream events showing agent execution and results
        """
        # Orchestrator initial thought
        yield OrchestratorThought(
            content=f"Initiating multi-agent analysis for student {student_id}. Activating {len(self.enabled_agents)} specialized agents...",
            timestamp=datetime.utcnow().isoformat()
        ).to_dict()
        
        await asyncio.sleep(0.5)
        
        # Track results from each agent
        results = {}
        
        # Agent 1: Data Collection (must run first)
        if "data_collection" in self.enabled_agents:
            yield AgentStartEvent(
                agent_name="Data Collection Agent",
                description="Retrieving comprehensive student profile and academic data",
                timestamp=datetime.utcnow().isoformat()
            ).to_dict()
            
            await asyncio.sleep(0.3)
            
            # Use absolute path from project root
            import os
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            data_path = os.path.join(project_root, "data", "student_data.csv")
            
            student_data = await asyncio.to_thread(
                get_student_data,
                student_id=student_id,
                data_source=data_path
            )
            
            results["student_data"] = student_data
            
            yield AgentCompleteEvent(
                agent_name="Data Collection Agent",
                result=student_data,
                success="error" not in student_data,
                timestamp=datetime.utcnow().isoformat()
            ).to_dict()
            
            await asyncio.sleep(0.3)
        
        # Check if we have student data to continue
        if "error" in results.get("student_data", {}):
            yield FinalReport(
                content=f"Unable to proceed: {results['student_data']['error']}",
                student_data=results.get("student_data"),
                timestamp=datetime.utcnow().isoformat()
            ).to_dict()
            return
        
        # Orchestrator coordination thought
        yield OrchestratorThought(
            content="Student data retrieved successfully. Coordinating parallel analysis across Risk Analysis, Intervention Planning, and Outcome Prediction agents...",
            timestamp=datetime.utcnow().isoformat()
        ).to_dict()
        
        await asyncio.sleep(0.4)
        
        # Agents 2-4: Run in parallel
        parallel_tasks = []
        
        # Agent 2: Risk Analysis
        if "risk_analysis" in self.enabled_agents:
            yield AgentStartEvent(
                agent_name="Risk Analysis Agent",
                description="Evaluating student risk level and identifying warning indicators",
                timestamp=datetime.utcnow().isoformat()
            ).to_dict()
            
            async def risk_analysis_task():
                await asyncio.sleep(0.2)
                risk_result = await asyncio.to_thread(
                    analyze_student_risk,
                    student_id=student_id
                )
                return ("risk_analysis", risk_result)
            
            parallel_tasks.append(risk_analysis_task())
        
        # Agent 3: Intervention Planning
        if "intervention_planning" in self.enabled_agents:
            yield AgentStartEvent(
                agent_name="Intervention Planning Agent",
                description="Designing personalized intervention strategies",
                timestamp=datetime.utcnow().isoformat()
            ).to_dict()
            
            async def intervention_task():
                await asyncio.sleep(0.3)
                # Use student data to determine risk level
                risk_level = results["student_data"].get("risk_level", "MODERATE")
                intervention_result = await asyncio.to_thread(
                    generate_intervention_plan,
                    risk_level=risk_level
                )
                return ("intervention_planning", intervention_result)
            
            parallel_tasks.append(intervention_task())
        
        # Agent 4: Outcome Prediction
        if "outcome_prediction" in self.enabled_agents:
            yield AgentStartEvent(
                agent_name="Outcome Prediction Agent",
                description="Forecasting intervention success probability",
                timestamp=datetime.utcnow().isoformat()
            ).to_dict()
            
            async def prediction_task():
                await asyncio.sleep(0.25)
                risk_level = results["student_data"].get("risk_level", "MODERATE")
                prediction_result = await asyncio.to_thread(
                    predict_intervention_success,
                    risk_level=risk_level
                )
                return ("outcome_prediction", prediction_result)
            
            parallel_tasks.append(prediction_task())
        
        # Wait for all parallel agents to complete
        if parallel_tasks:
            completed_results = await asyncio.gather(*parallel_tasks)
            
            # Yield completion events
            for agent_key, agent_result in completed_results:
                results[agent_key] = agent_result
                
                agent_names = {
                    "risk_analysis": "Risk Analysis Agent",
                    "intervention_planning": "Intervention Planning Agent",
                    "outcome_prediction": "Outcome Prediction Agent"
                }
                
                yield AgentCompleteEvent(
                    agent_name=agent_names[agent_key],
                    result=agent_result,
                    success="error" not in agent_result,
                    timestamp=datetime.utcnow().isoformat()
                ).to_dict()
                
                await asyncio.sleep(0.2)
        
        # Generate final comprehensive report
        yield OrchestratorThought(
            content="All agents completed. Synthesizing comprehensive intervention report...",
            timestamp=datetime.utcnow().isoformat()
        ).to_dict()
        
        await asyncio.sleep(0.5)
        
        # Build final report
        report_sections = []
        
        report_sections.append("# AGENT AURA - COMPREHENSIVE STUDENT ANALYSIS REPORT")
        report_sections.append(f"Student ID: {student_id}")
        report_sections.append(f"Analysis Date: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
        report_sections.append("")
        
        if "student_data" in results:
            sd = results["student_data"]
            report_sections.append("## 📊 STUDENT PROFILE (Data Collection Agent)")
            report_sections.append(f"**Name:** {sd.get('name', 'N/A')}")
            report_sections.append(f"**Grade:** {sd.get('grade', 'N/A')}")
            report_sections.append(f"**GPA:** {sd.get('gpa', 'N/A')}")
            report_sections.append(f"**Attendance:** {sd.get('attendance', 'N/A')}%")
            report_sections.append("")
        
        if "risk_analysis" in results:
            ra = results["risk_analysis"]
            report_sections.append("## ⚠️ RISK ASSESSMENT (Risk Analysis Agent)")
            report_sections.append(f"**Risk Level:** {ra.get('risk_level', 'N/A')}")
            report_sections.append(f"**Risk Score:** {ra.get('risk_score', 'N/A')}/100")
            if "factors" in ra:
                report_sections.append(f"**Contributing Factors:** {', '.join(ra['factors'])}")
            report_sections.append("")
        
        if "intervention_planning" in results:
            ip = results["intervention_planning"]
            report_sections.append("## 🎯 INTERVENTION STRATEGY (Intervention Planning Agent)")
            if "primary_strategy" in ip:
                report_sections.append(f"**Primary Strategy:** {ip['primary_strategy']}")
            if "action_items" in ip:
                report_sections.append("**Action Items:**")
                for i, action in enumerate(ip["action_items"], 1):
                    report_sections.append(f"  {i}. {action}")
            if "timeline" in ip:
                report_sections.append(f"**Timeline:** {ip['timeline']}")
            report_sections.append("")
        
        if "outcome_prediction" in results:
            op = results["outcome_prediction"]
            report_sections.append("## 📈 OUTCOME FORECAST (Outcome Prediction Agent)")
            report_sections.append(f"**Success Probability:** {op.get('success_probability', 'N/A')}%")
            if "confidence_level" in op:
                report_sections.append(f"**Confidence Level:** {op['confidence_level']}")
            if "expected_improvement" in op:
                report_sections.append(f"**Expected Improvement:** {op['expected_improvement']}")
            report_sections.append("")
        
        report_sections.append("## 💡 ORCHESTRATOR RECOMMENDATION")
        report_sections.append(f"Based on the analysis from {len(results)} specialized agents working in parallel, ")
        report_sections.append("immediate action is recommended. The multi-agent system has identified specific ")
        report_sections.append("interventions tailored to this student's unique situation.")
        
        final_report_text = "\n".join(report_sections)
        
        yield FinalReport(
            content=final_report_text,
            student_data=results.get("student_data"),
            risk_analysis=results.get("risk_analysis"),
            intervention_plan=results.get("intervention_planning"),
            outcome_prediction=results.get("outcome_prediction"),
            timestamp=datetime.utcnow().isoformat()
        ).to_dict()
