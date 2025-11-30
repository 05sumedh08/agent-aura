# Required Dependencies for Model Fallback

## Backend Dependencies (Python)

Add to `agent-aura-backend/requirements.txt`:

```
openai>=1.0.0
anthropic>=0.21.0
```

Note: `google-generativeai` should already be installed.

## Installation Command

```bash
cd agent-aura-backend
pip install openai anthropic
```

## API Keys Required

Add to `.env` file:

```
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
PERPLEXITY_API_KEY=your_perplexity_key_here
```

If you don't have these keys, the system will fall back to Gemini models.
