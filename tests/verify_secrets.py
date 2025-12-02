"""Verify that environment variables are properly configured."""
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    
    # Load environment variables from .env file
    load_dotenv()
    
    # Check for GOOGLE_API_KEY
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if api_key and len(api_key) > 0:
        print("✓ GOOGLE_API_KEY loaded successfully")
        print("✓ Key length:", len(api_key), "characters")
        print("✓ Key format:", "Valid" if api_key.startswith("AIza") else "Unknown format")
        print("\n✅ Secrets verification: OK")
        sys.exit(0)
    else:
        print("✗ GOOGLE_API_KEY not found or empty")
        print("✗ Check that .env file exists and contains GOOGLE_API_KEY=<your-key>")
        print("\n❌ Secrets verification: MISSING")
        sys.exit(1)
        
except ImportError as e:
    print("✗ python-dotenv not installed:", e)
    print("✗ Run: uv pip install python-dotenv")
    print("\n❌ Secrets verification: FAILED")
    sys.exit(1)
except Exception as e:
    print("✗ Unexpected error:", e)
    print("\n❌ Secrets verification: FAILED")
    sys.exit(1)
