# 🚀 Agent Aura - Complete Production System

**Full-Stack AI Agent Platform for K-12 Student Intervention**

A production-ready system with:
- 🎨 **Next.js Frontend** - Glass Box UI with real-time streaming
- ⚡ **FastAPI Backend** - RESTful API with Think-Act-Observe loop
- 🗄️ **PostgreSQL Database** - Session persistence and user management
- 🤖 **AI Agents** - Multi-agent system powered by Google Gemini
- 🔐 **Role-Based Access Control** - Admin, Teacher, Student roles
- 🐳 **Docker Deployment** - One-command deployment

---

## 📋 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      AGENT AURA SYSTEM                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Frontend   │ ───> │   Backend    │ ───> │   Database   │ │
│  │   Next.js    │ <─── │   FastAPI    │ <─── │  PostgreSQL  │ │
│  │   Port 3000  │      │   Port 8000  │      │   Port 5432  │ │
│  └──────────────┘      └──────────────┘      └──────────────┘ │
│        │                      │                                │
│        │                      │                                │
│        │              ┌───────┴────────┐                      │
│        │              │                │                      │
│        │         ┌────▼─────┐   ┌─────▼────┐                 │
│        │         │  Agent   │   │   Auth   │                 │
│        └────────>│  Engine  │   │  Service │                 │
│   (Glass Box)    │          │   │          │                 │
│                  └──────────┘   └──────────┘                 │
│                       │                                        │
│              ┌────────┼────────┐                             │
│              │        │        │                             │
│         ┌────▼───┐ ┌──▼───┐ ┌─▼────┐                        │
│         │ Risk   │ │ Inter│ │Predic│                        │
│         │Analysis│ │vention│ │tion  │                        │
│         └────────┘ └──────┘ └──────┘                         │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## 🎯 User Roles & Permissions

### 👨‍💼 Admin
- Full system access
- View all students across all classes
- Create/manage users (admin, teachers, students)
- System-wide analytics and reports
- Configure system settings

### 👨‍🏫 Teacher
- View students in their assigned classes/batches
- Run risk assessments for their students
- Generate intervention plans
- Track student progress over time
- Communicate with parents

### 👨‍🎓 Student
- View personal academic information
- See own risk assessments (if any)
- View intervention plans assigned to them
- Track own progress timeline
- Limited read-only access

---

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key ([Get one here](https://makersuite.google.com/app/apikey))

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/agent-aura.git
cd agent-aura

# Set up environment variables
cp .env.template .env
# Edit .env and add your GEMINI_API_KEY

# Start all services with Docker Compose
docker-compose -f docker-compose.full.yml up -d

# Wait for services to be healthy (30-60 seconds)
docker-compose -f docker-compose.full.yml ps

# Initialize database with sample data (optional)
docker-compose -f docker-compose.full.yml exec backend python scripts/seed_database.py
```

### Access the System

```
🌐 Frontend (Glass Box UI):  http://localhost:3000
📡 Backend API Docs:         http://localhost:8000/docs
🗄️ Database:                 localhost:5432
```

### Default Login Credentials

```
Admin:
  Username: admin
  Password: admin123

Teacher:
  Username: teacher1
  Password: teacher123

Student:
  Username: student_S001
  Password: student123
```

---

## 🎨 Frontend Features

### Glass Box UI
Real-time visualization of agent's reasoning process:

```
Session View              │  Trajectory View
──────────────────────────┼──────────────────────────────
                          │
User: Analyze S001        │  💭 Thought:
                          │  "I need to get student data
Agent: Risk Level: HIGH   │  first..."
       GPA: 2.1           │
       Intervention: 6wks │  🔧 Action: get_student_data
                          │  { "student_id": "S001" }
                          │
                          │  👁️ Observation:
                          │  { "name": "Alex", "gpa": 2.1 }
                          │
                          │  💭 Thought:
                          │  "GPA is below 2.5, analyzing
                          │  risk factors..."
                          │
                          │  🔧 Action: analyze_student_risk
                          │
                          │  👁️ Observation:
                          │  { "risk_level": "HIGH" }
                          │
                          │  ✅ Response:
                          │  Student S001 is at HIGH risk...
```

### Role-Specific Dashboards

**Admin Dashboard:**
- System overview with all students
- User management interface
- Analytics and reports
- System configuration

**Teacher Dashboard:**
- Class roster view
- Batch risk analysis
- Intervention planning tools
- Progress tracking charts

**Student Dashboard:**
- Personal academic profile
- Current risk status
- Active interventions
- Progress timeline

---

## ⚡ Backend API

### Authentication Endpoints

```http
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me
```

### Student Management

```http
GET  /api/v1/students
GET  /api/v1/students/{student_id}
POST /api/v1/students/{student_id}/assess
```

### Agent Interaction (Core Feature)

```http
POST /api/v1/agent/invoke
```

**Request:**
```json
{
  "goal": "Analyze student S001 risk level",
  "session_id": "optional-session-id"
}
```

**Response:** Streaming NDJSON
```json
{"type": "thought", "content": "I need to get student data...", "timestamp": "..."}
{"type": "action", "tool_name": "get_student_data", "arguments": {...}, "timestamp": "..."}
{"type": "observation", "content": "{...}", "success": true, "timestamp": "..."}
{"type": "response", "content": "Final answer here", "timestamp": "..."}
```

### Session Management

```http
GET /api/v1/sessions
GET /api/v1/sessions/{session_id}/events
```

---

## 🗄️ Database Schema

### Core Tables

**users** - Authentication and base user data
- `id, username, email, hashed_password, role, is_active`

**admins** - Admin profiles
- `id, user_id, full_name, department`

**teachers** - Teacher profiles with class assignments
- `id, user_id, teacher_id, full_name, subject, grade_level`

**students** - Student academic data
- `id, user_id, student_id, full_name, grade, gpa, attendance`

**agent_sessions** - Agent interaction sessions
- `id, session_id, user_id, goal, status, created_at`

**session_events** - Glass Box trajectory events
- `id, session_id, event_type, content, tool_name, sequence_number`

**risk_assessments** - Student risk analysis results
- `id, student_id, risk_score, risk_level, assessed_at`

**interventions** - Intervention plans and tracking
- `id, student_id, intervention_type, duration_weeks, status`

**progress_records** - Historical progress tracking
- `id, student_id, risk_score, recorded_at`

---

## 🔧 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=postgresql://agent_aura:password@localhost:5432/agent_aura_db

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Authentication
SECRET_KEY=your-secret-jwt-key-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Development

### Backend Development

```bash
cd agent-aura-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd agent-aura-frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Database Development

```bash
# Connect to PostgreSQL
docker-compose -f docker-compose.full.yml exec database psql -U agent_aura -d agent_aura_db

# Run migrations
docker-compose -f docker-compose.full.yml exec backend alembic upgrade head

# Create migration
docker-compose -f docker-compose.full.yml exec backend alembic revision --autogenerate -m "description"
```

---

## 📊 API Documentation

Full interactive API documentation available at:
```
http://localhost:8000/docs     (Swagger UI)
http://localhost:8000/redoc    (ReDoc)
```

---

## 🐳 Docker Commands

```bash
# Start all services
docker-compose -f docker-compose.full.yml up -d

# Stop all services
docker-compose -f docker-compose.full.yml down

# View logs
docker-compose -f docker-compose.full.yml logs -f

# Restart a service
docker-compose -f docker-compose.full.yml restart backend

# Rebuild and restart
docker-compose -f docker-compose.full.yml up -d --build

# Clean everything (including volumes)
docker-compose -f docker-compose.full.yml down -v
```

---

## 🧪 Testing

```bash
# Run backend tests
cd agent-aura-backend
pytest tests/

# Run frontend tests
cd agent-aura-frontend
npm test

# Integration tests
python tests/test_integration.py
```

---

## 📈 Production Deployment

### Google Cloud Run

```bash
# Build and push backend
gcloud builds submit --tag gcr.io/PROJECT_ID/agent-aura-backend ./agent-aura-backend

# Deploy backend
gcloud run deploy agent-aura-backend \
  --image gcr.io/PROJECT_ID/agent-aura-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=$DATABASE_URL,GEMINI_API_KEY=$GEMINI_API_KEY

# Build and push frontend
gcloud builds submit --tag gcr.io/PROJECT_ID/agent-aura-frontend ./agent-aura-frontend

# Deploy frontend
gcloud run deploy agent-aura-frontend \
  --image gcr.io/PROJECT_ID/agent-aura-frontend \
  --platform managed \
  --region us-central1 \
  --set-env-vars NEXT_PUBLIC_API_URL=$BACKEND_URL
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

---

## 📄 License

Apache 2.0 - See LICENSE file

---

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- FastAPI for the excellent web framework
- Next.js for the modern frontend
- PostgreSQL for reliable data persistence

---

**Built with ❤️ for the Kaggle Agents Intensive Competition**
