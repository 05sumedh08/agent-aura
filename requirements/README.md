# Requirements Files

This folder contains all Python dependency files for the Agent Aura project.

## Files Overview

### `requirements.txt` (Backend - Full)
**Use for:** Production backend deployment  
**Contains:** All dependencies for running the FastAPI backend with full features
```bash
cd agent-aura-backend
pip install -r ../requirements/requirements.txt
```

### `requirements-production.txt`
**Use for:** Production servers with optimized dependencies  
**Contains:** Production-ready packages with pinned versions for stability

### `requirements-minimal.txt`
**Use for:** Lightweight installations or testing  
**Contains:** Only essential dependencies for basic functionality

### `requirements-local.txt`
**Use for:** Local development environment  
**Contains:** Development tools, testing frameworks, and debugging utilities

### `requirements-root.txt`
**Use for:** Root-level CLI and core agent functionality  
**Contains:** Dependencies for the `agent_aura` package and CLI tools
```bash
pip install -r requirements/requirements-root.txt
```

## Installation Guide

### Quick Start (Development)
```bash
# Install backend dependencies
pip install -r requirements/requirements.txt

# Install root/CLI dependencies
pip install -r requirements/requirements-root.txt
```

### Production Deployment
```bash
# Use production requirements for stability
pip install -r requirements/requirements-production.txt
```

### Minimal Installation
```bash
# For testing or resource-constrained environments
pip install -r requirements/requirements-minimal.txt
```

## Updating Dependencies

To update dependencies:
```bash
# Update specific package
pip install --upgrade package-name

# Freeze current environment
pip freeze > requirements/requirements-local.txt
```

## Dependency Management

- Keep production requirements stable with pinned versions
- Test new packages in local environment first
- Document any new dependencies in this README
- Run security audits regularly: `pip audit`

---

**Last Updated:** November 2024  
**Maintained by:** Sumedh Gurchal
