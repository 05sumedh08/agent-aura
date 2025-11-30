# 🚀 Agent Aura Deployment Guide

This guide will walk you through deploying Agent Aura to the web so it's accessible to everyone.

## Overview

- **Backend**: Deployed on **Render** (Python/FastAPI)
- **Frontend**: Deployed on **Vercel** (Next.js)
- **Database**: Managed PostgreSQL on **Render**

---

## Phase 1: Deploy Backend (Render)

### 1. Create Web Service
1. Log in to [Render.com](https://render.com) with GitHub.
2. Click **New +** -> **Web Service**.
3. Select your repository: `agent-aura`.
4. Configure the service:
   - **Name**: `agent-aura-backend`
   - **Root Directory**: `agent-aura-backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
   - **Instance Type**: Free

### 2. Add Environment Variables
Scroll down to the **Environment Variables** section and add the following:

| Key | Value | Description |
|-----|-------|-------------|
| `ENV` | `production` | Sets app to production mode |
| `PYTHON_VERSION` | `3.11.9` | Ensures correct Python version |
| `SECRET_KEY` | *(Generate a random string)* | Security key for sessions |
| `GEMINI_API_KEY` | *(Your Google AI Key)* | Required for AI agents |
| `DATABASE_URL` | *(See Step 3)* | Connection string for DB |

### 3. Create Database (PostgreSQL)
1. In Render dashboard, click **New +** -> **PostgreSQL**.
2. Name it `agent-aura-db`.
3. Select **Free** plan.
4. Once created, copy the **Internal Database URL**.
5. Go back to your Web Service -> Environment -> Edit `DATABASE_URL` with this value.

### 4. Deploy
- Click **Create Web Service**.
- Wait for the build to finish.
- Once live, copy your backend URL (e.g., `https://agent-aura-backend.onrender.com`).

---

## Phase 2: Deploy Frontend (Vercel)

### 1. Import Project
1. Log in to [Vercel.com](https://vercel.com) with GitHub.
2. Click **Add New...** -> **Project**.
3. Import `agent-aura`.

### 2. Configure Project
- **Framework Preset**: Next.js (Auto-detected)
- **Root Directory**: Click Edit -> Select `agent-aura-frontend`.

### 3. Environment Variables
Expand the **Environment Variables** section:

| Key | Value |
|-----|-------|
| `NEXT_PUBLIC_API_URL` | `https://agent-aura-backend.onrender.com` |

> **Note**: Use the exact URL from Phase 1, Step 4. No trailing slash.

### 4. Deploy
- Click **Deploy**.
- Vercel will build your site.
- Once done, you'll get a live URL (e.g., `https://agent-aura.vercel.app`).

---

## Phase 3: Final Connection

1. Go back to **Render** -> Web Service -> Environment.
2. Add/Update `ALLOWED_ORIGINS` to include your new Vercel URL:
   ```
   ["https://agent-aura.vercel.app"]
   ```
   *(Replace with your actual Vercel URL)*.

---

## Phase 4: Verification

1. Open your Vercel URL.
2. Log in (default admin credentials if seeded, or register).
3. Check the browser console (F12) -> Network tab to ensure requests are going to your Render backend.
4. Test an AI agent query to verify the API key and backend connection.

🎉 **Success! Your Agent Aura is now live.**
