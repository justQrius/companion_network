import os
import sys
from pathlib import Path

def check_path(path, description):
    if os.path.exists(path):
        print(f"✅ {description} exists: {path}")
        return True
    else:
        print(f"❌ {description} MISSING: {path}")
        return False

def main():
    # Use script location to reliably find project root, regardless of CWD
    project_root = Path(__file__).parent.parent
    print(f"Verifying project structure in: {project_root}")

    checks = [
        ("alice_companion", "Alice Companion Directory"),
        (os.path.join("alice_companion", "__init__.py"), "Alice Companion Package Marker"),
        ("bob_companion", "Bob Companion Directory"),
        (os.path.join("bob_companion", "__init__.py"), "Bob Companion Package Marker"),
        ("shared", "Shared Directory"),
        (os.path.join("shared", "__init__.py"), "Shared Package Marker"),
        ("app.py", "Application Entry Point"),
    ]

    all_passed = True
    for path, desc in checks:
        if not check_path(project_root / path, desc):
            all_passed = False

    if all_passed:
        print("\n🎉 All structure checks passed!")
        sys.exit(0)
    else:
        print("\n💥 Some structure checks failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
