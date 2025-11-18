# Agent Aura Frontend

Modern Next.js 14 frontend with Glass Box UI for real-time AI agent visualization.

## 🎨 Features

- **Glass Morphism UI**: Beautiful frosted glass design with backdrop blur
- **Glass Box Visualization**: Real-time Think-Act-Observe agent trajectory
- **Role-Based Dashboards**: Admin, Teacher, and Student views
- **Streaming NDJSON**: Live agent responses with event-by-event rendering
- **State Management**: Zustand for global state
- **TypeScript**: Full type safety across the application

## 📦 Tech Stack

- **Framework**: Next.js 14.0.4 (App Router)
- **Language**: TypeScript 5.3.3
- **Styling**: Tailwind CSS 3.3.6
- **State**: Zustand 4.4.7
- **HTTP**: Axios 1.6.2
- **Charts**: Recharts 2.10.3
- **Icons**: Lucide React 0.294.0
- **Dates**: date-fns 3.0.0

## 🚀 Quick Start

### Prerequisites

- Node.js 18+ and npm
- Backend running on http://localhost:8000

### Installation

```bash
cd agent-aura-frontend
npm install
```

### Development

```bash
npm run dev
```

Open http://localhost:3000

### Build for Production

```bash
npm run build
npm start
```

## 📁 Project Structure

```
agent-aura-frontend/
├── app/                      # Next.js 14 App Router
│   ├── layout.tsx           # Root layout
│   ├── page.tsx             # Home page (auth redirect)
│   ├── globals.css          # Global styles + Tailwind
│   ├── login/
│   │   └── page.tsx         # Login page
│   └── admin/
│       ├── page.tsx         # Admin dashboard
│       └── agent/
│           └── page.tsx     # Agent Glass Box UI
├── components/              # Reusable React components
│   ├── TrajectoryView.tsx   # Think-Act-Observe timeline
│   ├── SessionView.tsx      # Conversation history
│   ├── EventCard.tsx        # Individual event rendering
│   ├── Header.tsx           # Top navigation bar
│   ├── Sidebar.tsx          # Side navigation menu
│   ├── StudentCard.tsx      # Student info card
│   ├── RiskBadge.tsx        # Risk level indicator
│   └── LoadingSpinner.tsx   # Loading indicator
├── lib/                     # Core utilities
│   ├── api.ts               # API client with streaming
│   ├── store.ts             # Zustand state management
│   └── types.ts             # TypeScript definitions
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## 🎯 Key Components

### Glass Box UI (TrajectoryView)

Real-time visualization of agent's reasoning process:

```typescript
<TrajectoryView 
  events={streamEvents}     // Array of StreamEvent
  isStreaming={isStreaming} // Boolean loading state
/>
```

**Event Types:**
- `thought`: Agent's reasoning step (purple)
- `action`: Tool execution (blue)
- `observation`: Tool result (green)
- `response`: Final answer (indigo)

### API Client (Streaming)

NDJSON streaming for real-time updates:

```typescript
const stream = apiClient.invokeAgent({ goal: 'Analyze student STU001' });

for await (const event of stream) {
  console.log(event.type, event.content);
}
```

### State Management (Zustand)

Three specialized stores:

```typescript
// Authentication
const { user, isAuthenticated, setUser, logout } = useAuth();

// Students
const { students, selectedStudent, setStudents } = useStudents();

// Agent Sessions
const { streamEvents, isStreaming, addStreamEvent } = useSession();
```

## 🎨 Styling System

### Glass Morphism Classes

```css
.glass              /* White translucent with blur */
.glass-dark         /* Dark translucent with blur */
```

### Custom Colors

```javascript
colors: {
  aura: {
    primary: '#6366f1',   // Indigo
    secondary: '#8b5cf6', // Purple  
    accent: '#ec4899',    // Pink
  }
}
```

### Custom Animations

```javascript
animation: {
  'fade-in': 'fadeIn 0.5s ease-out',
  'slide-up': 'slideUp 0.5s ease-out',
  'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
}
```

## 🔐 Authentication Flow

1. User visits `/` → checks token → redirects to `/login` or role-based dashboard
2. Login → POST `/api/v1/auth/login` → stores JWT token
3. API requests include `Authorization: Bearer <token>` header
4. Token stored in localStorage (automatically loaded on page refresh)

## 🎭 User Roles

### Admin
- Full system access
- View all students and teachers
- System-wide analytics
- User management

### Teacher
- View assigned students only
- Class-level analytics
- Create interventions for their students

### Student
- View personal data only
- Own progress tracking
- Risk assessment history

## 📡 API Integration

### Backend URL Configuration

Set in `next.config.js`:

```javascript
env: {
  NEXT_PUBLIC_API_URL: process.env.API_URL || 'http://localhost:8000',
}
```

### Key Endpoints Used

```
POST   /api/v1/auth/login           # Login
GET    /api/v1/auth/me              # Get current user
GET    /api/v1/students              # List students (role-filtered)
POST   /api/v1/agent/invoke         # Stream agent (NDJSON)
GET    /api/v1/sessions              # Session history
GET    /api/v1/sessions/{id}/events # Replay session
```

## 🧪 Testing

```bash
# Lint check
npm run lint

# Type check
npx tsc --noEmit

# Build check
npm run build
```

## 🐛 Common Issues

### "Cannot find module" errors
Run: `npm install`

### Tailwind classes not working
Restart dev server: `Ctrl+C` then `npm run dev`

### API connection failed
Ensure backend is running on http://localhost:8000
Check CORS settings in backend

### TypeScript errors on @types/node
Already included in devDependencies - run `npm install`

## 📝 Demo Credentials

```
Admin:    admin / admin123
Teacher:  teacher1 / teacher123
Student:  STU001 / student123
```

## 🎯 Next Steps

1. Start backend: `docker-compose -f docker-compose.full.yml up -d`
2. Start frontend: `npm run dev`
3. Open http://localhost:3000
4. Login with demo credentials
5. Navigate to "Ask AI Agent" to see Glass Box UI

## 📚 Key Features Demo

### Glass Box Trajectory
1. Login as admin
2. Go to "Ask AI Agent"
3. Type: "What is the risk level for student STU001?"
4. Watch real-time Think → Act → Observe → Response flow

### Student Management
1. View dashboard
2. See at-risk students highlighted
3. Click student card for details

### Session History
1. Left sidebar shows all past conversations
2. Click session to replay trajectory
3. See complete reasoning chain

## 🛠️ Development Tips

- Use `'use client'` for interactive components
- Keep server components for static content
- Leverage Zustand for cross-component state
- Use TypeScript types from `lib/types.ts`
- Follow glass morphism design system

## 📄 License

MIT License - See backend project for details

---

**Built with ❤️ for Kaggle Agent Aura Competition**
