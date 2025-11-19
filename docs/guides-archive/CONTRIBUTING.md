# Contributing to Agent Aura

Thank you for your interest in contributing to Agent Aura! This document provides guidelines and instructions for contributing to the project.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [How to Contribute](#how-to-contribute)
- [Development Setup](#development-setup)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Community](#community)

---

## 🤝 Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, gender, gender identity and expression, sexual orientation, disability, personal appearance, body size, race, ethnicity, age, religion, or nationality.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

### Unacceptable Behavior

- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without explicit permission
- Other conduct which could reasonably be considered inappropriate

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- Google Gemini API key
- Node.js 18+ (for frontend development)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
```bash
git clone https://github.com/YOUR_USERNAME/agent-aura.git
cd agent-aura
```

3. Add the upstream repository:
```bash
git remote add upstream https://github.com/05sumedh08/agent-aura.git
```

---

## 💡 How to Contribute

### Types of Contributions

We welcome many types of contributions:

- 🐛 **Bug fixes** - Fix issues in the codebase
- ✨ **New features** - Add new functionality
- 📝 **Documentation** - Improve or add documentation
- 🧪 **Tests** - Add or improve test coverage
- 🎨 **UI/UX improvements** - Enhance the frontend
- 🔧 **Refactoring** - Improve code quality
- 🌐 **Translations** - Add language support

### Finding Issues

- Check the [Issues](https://github.com/05sumedh08/agent-aura/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Feel free to create a new issue if you find a bug

---

## 🛠️ Development Setup

### 1. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Backend dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Frontend dependencies
cd agent-aura-frontend
npm install
```

### 3. Configure Environment

```bash
# Copy environment template
cp .env.template .env

# Edit .env and add your API keys
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agent_aura --cov-report=html

# Run specific test file
pytest tests/test_tools.py
```

### 5. Start Development Server

```bash
# Backend
adk web

# Frontend (separate terminal)
cd agent-aura-frontend
npm run dev
```

---

## 📏 Coding Standards

### Python Code Style

We follow PEP 8 with these exceptions:
- Maximum line length: 127 characters
- Use double quotes for strings

#### Formatting Tools

```bash
# Format code with Black
black agent_aura/

# Check with flake8
flake8 agent_aura/ --max-line-length=127

# Type checking with mypy
mypy agent_aura/
```

#### Python Best Practices

- Use type hints for function arguments and returns
- Write docstrings for all public functions and classes
- Follow Google docstring format
- Use descriptive variable names
- Keep functions small and focused

**Example:**

```python
def analyze_student_risk(student_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate risk score for a student based on their data.
    
    Args:
        student_data: Dictionary containing student information including
                     GPA, attendance, and behavioral metrics.
    
    Returns:
        Dictionary containing risk_score, risk_level, and risk_factors.
    
    Raises:
        ValueError: If student_data is missing required fields.
    """
    # Implementation here
    pass
```

### TypeScript/React Code Style

- Use TypeScript for all frontend code
- Follow Airbnb React style guide
- Use functional components with hooks
- Use Tailwind CSS for styling

```bash
# Lint frontend code
npm run lint

# Format with Prettier
npm run format
```

### Commit Message Guidelines

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**

```bash
feat(tools): add new progress tracking tool

fix(agent): resolve error in risk calculation

docs(readme): update installation instructions

test(tools): add unit tests for get_student_data
```

---

## 🧪 Testing Guidelines

### Writing Tests

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Follow AAA pattern: Arrange, Act, Assert

**Example:**

```python
def test_analyze_student_risk_high_risk():
    """Test that high-risk students are correctly identified."""
    # Arrange
    student_data = {
        "student_id": "S001",
        "gpa": 1.5,
        "attendance_rate": 0.65,
        "behavioral_incidents": 8
    }
    
    # Act
    result = analyze_student_risk(student_data)
    
    # Assert
    assert result["risk_level"] == "HIGH"
    assert result["risk_score"] >= 0.80
    assert "Low GPA" in result["risk_factors"]
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_tools.py

# Specific test function
pytest tests/test_tools.py::test_analyze_student_risk_high_risk

# With coverage
pytest --cov=agent_aura --cov-report=html

# Watch mode
pytest-watch
```

---

## 🔄 Pull Request Process

### Before Submitting

1. **Update your fork**
```bash
git fetch upstream
git checkout main
git merge upstream/main
```

2. **Create a feature branch**
```bash
git checkout -b feature/your-feature-name
```

3. **Make your changes**
- Write clean, well-documented code
- Add tests for new functionality
- Update documentation as needed

4. **Run tests and linting**
```bash
pytest
black agent_aura/
flake8 agent_aura/
```

5. **Commit your changes**
```bash
git add .
git commit -m "feat: add your feature description"
```

6. **Push to your fork**
```bash
git push origin feature/your-feature-name
```

### Submitting a Pull Request

1. Go to the [Agent Aura repository](https://github.com/05sumedh08/agent-aura)
2. Click "New Pull Request"
3. Select your fork and branch
4. Fill out the PR template:
   - Clear title and description
   - Link related issues
   - List changes made
   - Add screenshots if applicable

### PR Review Process

1. **Automated checks** - CI/CD pipeline runs tests
2. **Code review** - Maintainers review your code
3. **Feedback** - Address any requested changes
4. **Approval** - PR is approved by maintainers
5. **Merge** - Your contribution is merged!

### PR Guidelines

✅ **DO:**
- Keep PRs focused and small
- Write clear descriptions
- Update documentation
- Add tests
- Respond to feedback promptly

❌ **DON'T:**
- Submit large PRs with multiple features
- Break existing functionality
- Ignore test failures
- Add unrelated changes

---

## 🏗️ Project Structure

```
agent-aura/
├── agent_aura/              # Main Python package
│   ├── agent.py            # Orchestrator agent
│   ├── tools.py            # Tool implementations
│   ├── config.py           # Configuration
│   ├── sub_agents/         # Specialized agents
│   └── utils.py            # Utility functions
├── agent-aura-backend/      # FastAPI backend
├── agent-aura-frontend/     # Next.js frontend
├── tests/                   # Test suite
├── docs/                    # Documentation
└── .github/                 # GitHub workflows
```

---

## 📚 Additional Resources

### Documentation

- [README.md](README.md) - Project overview
- [QUICKSTART.md](QUICKSTART.md) - Quick start guide
- [API Documentation](docs/api_reference.md) - API reference
- [Architecture](docs/architecture.md) - System architecture

### Community

- **GitHub Issues**: [Report bugs or request features](https://github.com/05sumedh08/agent-aura/issues)
- **Discussions**: [Ask questions and share ideas](https://github.com/05sumedh08/agent-aura/discussions)
- **Email**: 05sumedh08@example.com

### Learning Resources

- [Google ADK Documentation](https://github.com/google/adk-python)
- [Gemini API Guide](https://ai.google.dev/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

---

## 🎯 Development Roadmap

Check our [project roadmap](https://github.com/05sumedh08/agent-aura/projects) to see what we're working on and where you can help!

---

## 🙏 Recognition

Contributors are recognized in several ways:

- Listed in [CONTRIBUTORS.md](CONTRIBUTORS.md)
- Mentioned in release notes
- Acknowledged in documentation
- Invited to join core team (for significant contributions)

---

## ❓ Questions?

If you have questions about contributing, feel free to:
- Open a [Discussion](https://github.com/05sumedh08/agent-aura/discussions)
- Create an [Issue](https://github.com/05sumedh08/agent-aura/issues)
- Reach out via email

---

Thank you for contributing to Agent Aura! Together, we're helping transform K-12 education through intelligent student support. 🎓✨
