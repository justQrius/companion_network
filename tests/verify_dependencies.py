import sys
import importlib

def check_import(package_name, import_name=None):
    """
    Checks if a package can be imported.
    Args:
        package_name: The name of the package to check (for display).
        import_name: The actual module name to import (defaults to package_name).
    Returns:
        True if import succeeds, False otherwise.
    """
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name} imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import {package_name} ({import_name}): {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing {package_name} ({import_name}): {e}")
        return False

def main():
    print("Verifying Core Dependencies...")
    
    checks = [
        ("google-adk", "google.adk"),
        ("mcp", "mcp"),
        ("gradio", "gradio"),
        ("python-dotenv", "dotenv"),
    ]
    
    all_passed = True
    for package, module in checks:
        if not check_import(package, module):
            all_passed = False
            
    if all_passed:
        print("\n🎉 All core dependencies verified!")
        sys.exit(0)
    else:
        print("\n💥 Some dependencies failed to import.")
        sys.exit(1)

if __name__ == "__main__":
    main()
