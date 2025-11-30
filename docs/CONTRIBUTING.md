# Contributing to Agent Aura

Thank you for your interest in contributing to Agent Aura! We welcome contributions from the community to help improve this project.

## How to Contribute

1.  **Fork the Repository**: Click the "Fork" button on the top right of the repository page.
2.  **Clone your Fork**:
    ```bash
    git clone https://github.com/YOUR_USERNAME/agent-aura.git
    cd agent-aura
    ```
3.  **Create a Branch**:
    ```bash
    git checkout -b feature/your-feature-name
    ```
4.  **Make Changes**: Implement your feature or fix.
5.  **Commit Changes**:
    ```bash
    git commit -m "Description of your changes"
    ```
6.  **Push to your Fork**:
    ```bash
    git push origin feature/your-feature-name
    ```
7.  **Open a Pull Request**: Go to the original repository and open a Pull Request from your fork.

## Development Setup

### Backend
1.  Navigate to `agent-aura-backend`.
2.  Create a virtual environment: `python -m venv .venv`.
3.  Activate it: `.venv\Scripts\Activate` (Windows) or `source .venv/bin/activate` (Mac/Linux).
4.  Install dependencies: `pip install -r requirements.txt`.
5.  Set up `.env` (see `.env.example`).
6.  Run server: `uvicorn app.main:app --reload`.

### Frontend
1.  Navigate to `agent-aura-frontend`.
2.  Install dependencies: `npm install`.
3.  Run dev server: `npm run dev`.

## Code Style
- **Python**: Follow PEP 8.
- **JavaScript/TypeScript**: Follow standard ESLint configuration.

## Reporting Bugs
Please open an issue on GitHub with a detailed description of the bug, steps to reproduce, and expected behavior.
