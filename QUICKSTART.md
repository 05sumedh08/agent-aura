# 🚀 Agent Aura Quick Start Guide

Get started with Agent Aura in 5 minutes!

## Prerequisites

- Python 3.11+
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

## Installation

```powershell
# Clone repository
git clone https://github.com/yourusername/agent-aura.git
cd agent-aura

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env and add your GEMINI_API_KEY
```

## Quick Test

```powershell
# Test CLI
python -m agent_aura.cli analyze --student-id S001

# Run integration tests
python tests/test_integration.py

# Batch process students
python -m agent_aura.cli batch --student-ids "S001,S002,S003,S004,S005"

# Export reports
python -m agent_aura.cli export --format all --output output
```

## Using ADK Web Interface

```powershell
# Start ADK Web
adk web

# Open browser to http://localhost:8000
# Interact with Agent Aura through the UI
```

## Python API Usage

```python
from agent_aura import root_agent
from google.adk.sessions import InMemorySessionService

# Initialize
session_service = InMemorySessionService()
session_id = session_service.create_session(root_agent)

# Send message
response = session_service.send_message(
    session_id=session_id,
    message="Analyze student S001 and provide intervention recommendations"
)

print(response.text)
```

## Docker Deployment

```powershell
# Build and run with Docker Compose
docker-compose up -d

# Or build and run manually
docker build -t agent-aura:latest .
docker run -p 8000:8000 --env-file .env agent-aura:latest
```

## Common Commands

```powershell
# Analyze single student
python -m agent_aura.cli analyze --student-id S001 --verbose

# Batch process with custom data
python -m agent_aura.cli batch --student-ids "S001,S002,S003" --data-file custom_data.csv

# Export specific format
python -m agent_aura.cli export --format notifications --output reports

# Run all tests
pytest

# Run specific test suite
pytest tests/test_tools.py
```

## Expected Output

### Single Student Analysis
```
================================================================================
AGENT AURA - STUDENT ANALYSIS
================================================================================

[1/6] Collecting data for student S001...
✓ Student: Alex Johnson (Grade 9)

[2/6] Analyzing risk factors...
✓ Risk Level: 🟠 HIGH (Score: 0.800)

[3/6] Generating intervention plan...
✓ Plan Type: Targeted Intervention
  Duration: 6 weeks
  Frequency: 3x per week

[4/6] Predicting intervention success...
✓ Expected Success Rate: 82%
  Confidence: 85%
  Timeline: 6 weeks

[5/6] Checking notification requirements...
✓ 📧 Notification generated: HIGH priority

[6/6] Tracking progress...
✓ Progress tracked: → NEW ENTRY

================================================================================
✅ ANALYSIS COMPLETE
================================================================================
```

### Batch Analysis
```
================================================================================
AGENT AURA - BATCH ANALYSIS
================================================================================

Analyzing 5 students...

[ 1/5] 🟠 Alex Johnson         | HIGH       | 0.800 📧
[ 2/5] 🟢 Maria Garcia         | LOW        | 0.200  
[ 3/5] 🟢 James Smith          | LOW        | 0.500  
[ 4/5] 🟢 Emily Davis          | LOW        | 0.000  
[ 5/5] 🟠 Michael Brown        | HIGH       | 0.800 📧

================================================================================
SUMMARY
================================================================================
Total Analyzed: 5
Notifications Sent: 2

Risk Distribution:
  🔴 CRITICAL  :  0 (  0.0%)
  🟠 HIGH      :  2 ( 40.0%)
  🟡 MODERATE  :  0 (  0.0%)
  🟢 LOW       :  3 ( 60.0%)
================================================================================
```

## Troubleshooting

### Issue: "Import could not be resolved"
**Solution:** Install dependencies: `pip install -r requirements.txt`

### Issue: "GEMINI_API_KEY not found"
**Solution:** Create `.env` file and add your API key

### Issue: "No module named 'agent_aura'"
**Solution:** Run commands from project root directory

### Issue: "Student data not found"
**Solution:** Ensure `data/student_data.csv` exists

## Next Steps

1. ✅ Verify installation with tests
2. ✅ Analyze sample students
3. ✅ Review generated reports in `output/` directory
4. 📊 Explore ADK Web interface
5. 🚀 Deploy to Cloud Run (see README.md)
6. 📈 Monitor results and iterate

## Support

- **Documentation:** [README.md](README.md)
- **Issues:** [GitHub Issues](https://github.com/yourusername/agent-aura/issues)
- **Kaggle:** [Competition Page](https://www.kaggle.com/competitions/agents-intensive-course-capstone-2025)

---

**Happy Student Supporting! 🎓**
