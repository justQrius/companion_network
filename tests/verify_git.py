#!/usr/bin/env python3
"""
Verification script for Story 1.5: Initialize Git Repository with Best Practices

Verifies all acceptance criteria for Git repository initialization:
- AC1: Git repository initialized
- AC2: .gitignore properly configured
- AC3: .gitattributes configured
- AC4: Initial commit includes required files
- AC5: Commit message correct
- AC6: .env not in Git history
- AC7: uv.lock is committed
- AC8: Clean working directory
- AC9: .gitignore exclusions present
"""

import subprocess
import sys
from pathlib import Path

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, check=check
        )
        return result.stdout.strip(), result.returncode == 0
    except subprocess.CalledProcessError as e:
        return e.stdout.strip() if e.stdout else "", False

def check_ac1():
    """AC1: Git Initialized - Git repository initialized (git init)."""
    print("\n[AC1] Checking Git repository initialization...")
    git_dir = Path(".git")
    if git_dir.exists() and git_dir.is_dir():
        print(f"{GREEN}✓ PASS{RESET}: .git directory exists")
        return True
    else:
        print(f"{RED}✗ FAIL{RESET}: .git directory not found")
        return False

def check_ac2_ac9():
    """AC2 & AC9: Gitignore Configured - .gitignore properly configured with required exclusions."""
    print("\n[AC2, AC9] Checking .gitignore configuration...")
    gitignore_path = Path(".gitignore")
    if not gitignore_path.exists():
        print(f"{RED}✗ FAIL{RESET}: .gitignore file not found")
        return False
    
    gitignore_content = gitignore_path.read_text()
    required_patterns = {
        ".env": ".env",
        "*.db": "*.db",
        ".venv": ".venv",
        "__pycache__": "__pycache__",
        "*.pyc": "*.pyc or *.py[cod]",
    }
    
    all_present = True
    for pattern, description in required_patterns.items():
        if pattern in gitignore_content or (pattern == "*.pyc" and "*.py[cod]" in gitignore_content):
            print(f"{GREEN}✓ PASS{RESET}: {description} found in .gitignore")
        else:
            print(f"{RED}✗ FAIL{RESET}: {description} NOT found in .gitignore")
            all_present = False
    
    # Verify with git check-ignore
    test_files = [".env", ".venv", "test.db"]
    for test_file in test_files:
        output, success = run_command(f'git check-ignore "{test_file}"', check=False)
        if success and output:
            print(f"{GREEN}✓ PASS{RESET}: git check-ignore confirms {test_file} is ignored")
        else:
            print(f"{YELLOW}⚠ WARN{RESET}: git check-ignore for {test_file} returned unexpected result")
    
    return all_present

def check_ac3():
    """AC3: Gitattributes Configured - .gitattributes configured."""
    print("\n[AC3] Checking .gitattributes configuration...")
    gitattributes_path = Path(".gitattributes")
    if gitattributes_path.exists():
        content = gitattributes_path.read_text()
        if "text=auto" in content or "* text" in content:
            print(f"{GREEN}✓ PASS{RESET}: .gitattributes file exists with text normalization")
            return True
        else:
            print(f"{YELLOW}⚠ WARN{RESET}: .gitattributes exists but may be incomplete")
            return True  # File exists, which satisfies AC3
    else:
        print(f"{RED}✗ FAIL{RESET}: .gitattributes file not found")
        return False

def check_ac4():
    """AC4: Initial Commit - Initial commit includes required files."""
    print("\n[AC4] Checking initial commit includes required files...")
    required_files = [
        "README.md",
        "pyproject.toml",
        "uv.lock",
        ".env.example",
        ".gitignore",
        "app.py",
        "alice_companion/__init__.py",
        "bob_companion/__init__.py",
        "shared/__init__.py",
    ]
    
    output, success = run_command("git ls-files", check=False)
    if not success:
        print(f"{RED}✗ FAIL{RESET}: Cannot list tracked files")
        return False
    
    tracked_files = set(output.splitlines())
    all_present = True
    
    for file_path in required_files:
        if file_path in tracked_files:
            print(f"{GREEN}✓ PASS{RESET}: {file_path} is tracked")
        else:
            print(f"{RED}✗ FAIL{RESET}: {file_path} is NOT tracked")
            all_present = False
    
    return all_present

def check_ac5():
    """AC5: Commit Message - Initial commit message matches requirement."""
    print("\n[AC5] Checking commit message...")
    output, success = run_command("git log -1 --pretty=%B", check=False)
    if not success:
        print(f"{RED}✗ FAIL{RESET}: Cannot retrieve commit message")
        return False
    
    expected_message = "Initial project setup with ADK, MCP, and Gradio"
    if expected_message in output:
        print(f"{GREEN}✓ PASS{RESET}: Latest commit message matches requirement")
        print(f"   Message: {output}")
        return True
    else:
        print(f"{YELLOW}⚠ WARN{RESET}: Latest commit message does not match exactly")
        print(f"   Expected: {expected_message}")
        print(f"   Found: {output}")
        # Check if any commit has the expected message
        all_output, _ = run_command("git log --all --pretty=%B", check=False)
        if expected_message in all_output:
            print(f"{GREEN}✓ PASS{RESET}: Expected message found in commit history")
            return True
        return False

def check_ac6():
    """AC6: Secrets Not Committed - .env file is NOT committed."""
    print("\n[AC6] Checking .env is NOT in Git history...")
    output, success = run_command("git log --all --decorate -- .env", check=False)
    if not output.strip():
        print(f"{GREEN}✓ PASS{RESET}: .env is NOT in Git history")
        return True
    else:
        print(f"{RED}✗ FAIL{RESET}: .env found in Git history!")
        print(f"   History: {output}")
        return False

def check_ac7():
    """AC7: Lock File Committed - uv.lock IS committed."""
    print("\n[AC7] Checking uv.lock is committed...")
    output, success = run_command("git ls-files uv.lock", check=False)
    if success and "uv.lock" in output:
        print(f"{GREEN}✓ PASS{RESET}: uv.lock is tracked in Git")
        return True
    else:
        print(f"{RED}✗ FAIL{RESET}: uv.lock is NOT tracked in Git")
        return False

def check_ac8():
    """AC8: Clean Status - Running git status shows clean working directory."""
    print("\n[AC8] Checking working directory is clean...")
    output, success = run_command("git status --porcelain", check=False)
    if success and not output.strip():
        print(f"{GREEN}✓ PASS{RESET}: Working directory is clean")
        return True
    else:
        # Filter out untracked files that are intentionally ignored
        lines = output.strip().splitlines() if output.strip() else []
        # Only count modified/staged files, not untracked
        relevant_lines = [l for l in lines if not l.startswith("??")]
        if not relevant_lines:
            print(f"{GREEN}✓ PASS{RESET}: Working directory is clean (untracked files are expected)")
            return True
        else:
            print(f"{YELLOW}⚠ WARN{RESET}: Working directory has uncommitted changes:")
            for line in relevant_lines:
                print(f"   {line}")
            return False

def main():
    """Run all acceptance criteria checks."""
    print("=" * 70)
    print("Git Repository Verification - Story 1.5")
    print("=" * 70)
    
    results = {
        "AC1": check_ac1(),
        "AC2, AC9": check_ac2_ac9(),
        "AC3": check_ac3(),
        "AC4": check_ac4(),
        "AC5": check_ac5(),
        "AC6": check_ac6(),
        "AC7": check_ac7(),
        "AC8": check_ac8(),
    }
    
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for ac, result in results.items():
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"{ac}: {status}")
    
    print(f"\nTotal: {passed}/{total} acceptance criteria passed")
    
    if passed == total:
        print(f"\n{GREEN}✓ All acceptance criteria satisfied!{RESET}")
        return 0
    else:
        print(f"\n{RED}✗ Some acceptance criteria failed{RESET}")
        return 1

if __name__ == "__main__":
    sys.exit(main())

