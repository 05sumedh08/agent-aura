"""
Test script to verify data path resolution
"""
from pathlib import Path
import os

# Simulate the path resolution from tools.py
print("Current working directory:", os.getcwd())
print("Script location (__file__):", __file__)

# Simulate being in agent-aura-backend/app/agent_core/tools.py
tools_path = Path("s:/Courses/Kaggle/Agent_Aura_GIT/agent-aura-backend/app/agent_core/tools.py")
print("\nSimulating tools.py at:", tools_path)

base_path = tools_path.parent.parent.parent.parent
print("Base path (4 levels up):", base_path)

data_source = str(base_path / "data" / "student_data.csv")
print("Resolved data_source:", data_source)
print("Does file exist?:", os.path.exists(data_source))

# Now test the actual resolution that would happen at runtime
print("\n--- Testing actual runtime resolution ---")
import sys
sys.path.insert(0, "s:/Courses/Kaggle/Agent_Aura_GIT/agent-aura-backend")

from app.agent_core.tools import get_student_data

# Try to get student data
result = get_student_data("S001")
print("\nResult:")
print(result)
