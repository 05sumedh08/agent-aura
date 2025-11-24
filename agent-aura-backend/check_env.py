import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Fix for Windows Unicode printing
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

try:
    import google.generativeai as genai
except ImportError:
    print("❌ Error: google-generativeai package not found.")
    print("   Please run: pip install -r requirements.txt")
    sys.exit(1)

def check_environment():
    """Validate environment configuration and API keys."""
    print("🔍 Checking Agent Aura Environment...")
    
    # Load .env
    backend_dir = Path(__file__).parent
    env_path = backend_dir / ".env"
    
    if not env_path.exists():
        print(f"❌ Error: .env file not found at {env_path}")
        print("   Please copy .env.template to .env and add your API key.")
        return False
        
    load_dotenv(dotenv_path=env_path)
    
    # Check API Key existence
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Error: GEMINI_API_KEY is missing in .env file.")
        return False
        
    if api_key == "your_api_key_here":
        print("❌ Error: GEMINI_API_KEY is still set to the default template value.")
        print("   Please edit .env and add your actual Google Gemini API key.")
        return False

    # Validate API Key by making a lightweight call
    print("🔑 Validating Gemini API Key...")
    try:
        genai.configure(api_key=api_key)
        # List models is a quick way to verify auth without generating content
        for m in genai.list_models():
            break
        print("✅ Success: Gemini API Key is valid.")
        return True
    except Exception as e:
        print(f"❌ Error: Failed to validate Gemini API Key.")
        print(f"   Details: {repr(e)}")
        return False

if __name__ == "__main__":
    if check_environment():
        print("\n✅ Environment check passed. Starting services...\n")
        sys.exit(0)
    else:
        print("\n❌ Environment check failed. Please fix the issues above.\n")
        sys.exit(1)
