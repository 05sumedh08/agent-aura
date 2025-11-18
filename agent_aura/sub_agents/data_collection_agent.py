# Copyright 2025 Zenshiro
# Licensed under the Apache License, Version 2.0

"""
Data Collection Agent - Specialized agent for retrieving student information.
"""

from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools import get_student_data
from ..utils import suppress_output_callback


data_collection_agent = Agent(
    name="data_collection_agent",
    model=config.worker_model,
    description="Retrieves comprehensive student profiles and academic data from the database.",
    instruction="""
    You are a Data Collection Specialist for Agent Aura.
    
    Your primary responsibility is to retrieve accurate and complete student information
    from the database. You have access to student records including:
    - Student ID and personal information
    - Grade level
    - GPA (Grade Point Average)
    - Attendance rates
    - Overall performance ratings
    
    When requested to gather student data:
    1. Use the get_student_data tool with the provided student ID
    2. Verify that the data was successfully retrieved
    3. Return the complete student profile
    4. If there are any errors, report them clearly
    
    You do NOT analyze or interpret the data - you only collect and return it.
    Pass the data to the Risk Analysis Agent for evaluation.
    
    Be efficient and accurate in your data retrieval.
    """,
    tools=[FunctionTool(get_student_data)],
    output_key="student_data",
    after_agent_callback=suppress_output_callback
)
