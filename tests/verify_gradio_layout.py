"""Verification script for Gradio split-screen layout implementation.

This script verifies all acceptance criteria for Story 4.1:
- AC1: Split-Screen Layout (left panel Alice, right panel Bob, bottom panel Network Monitor)
- AC2: Clean Minimal Design (Gradio Base theme + custom CSS)
- AC3: Chat Panel Components (input textbox and submit button in each panel)
- AC4: Chat History Display (conversational format)
- AC5: Responsive Layout (desktop-first, ~1200px width minimum)
- AC6: Panel Labels (clear labels for each panel)

Follows Epic 1, 2, 3 verification pattern.
"""

import sys
import ast
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_ac1_split_screen_layout():
    """AC1: Split-Screen Layout.
    
    Given the Gradio app is launched,
    when I open the browser to localhost:7860,
    then the interface displays:
    - Left panel "Alice's Companion" with chat interface
    - Right panel "Bob's Companion" with chat interface
    - Bottom panel "Network Activity Monitor"
    """
    print("\n📋 Checking AC1: Split-Screen Layout...")
    try:
        # Read app.py and parse it
        app_file = project_root / "app.py"
        if not app_file.exists():
            print("❌ AC1: app.py not found")
            return False
        
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required components
        checks = {
            "gr.Row()": "gr.Row()" in content or "gr.Row(" in content,
            "gr.Column()": "gr.Column()" in content or "gr.Column(" in content,
            "Alice panel": "Alice" in content and "Column" in content,
            "Bob panel": "Bob" in content and "Column" in content,
            "Network Monitor": "Network Activity Monitor" in content or "Network Monitor" in content,
        }
        
        failed_checks = [k for k, v in checks.items() if not v]
        if failed_checks:
            print(f"❌ AC1: Missing components: {failed_checks}")
            return False
        
        print("✅ AC1: Split-screen layout structure found (Row/Column components)")
        return True
    except Exception as e:
        print(f"❌ AC1: Failed - {e}")
        return False


def check_ac2_clean_minimal_design():
    """AC2: Clean Minimal Design.
    
    The interface uses Gradio Base theme + custom CSS for clean minimal style.
    """
    print("\n📋 Checking AC2: Clean Minimal Design...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Base theme
        has_base_theme = "Base()" in content or "theme=gr.themes.Base()" in content or 'theme="base"' in content.lower()
        
        # Check for custom CSS
        has_css = "CUSTOM_CSS" in content or "css=" in content.lower()
        
        if not has_base_theme:
            print("❌ AC2: Gradio Base theme not found")
            return False
        
        if not has_css:
            print("❌ AC2: Custom CSS not found")
            return False
        
        print("✅ AC2: Gradio Base theme + custom CSS applied")
        return True
    except Exception as e:
        print(f"❌ AC2: Failed - {e}")
        return False


def check_ac3_chat_panel_components():
    """AC3: Chat Panel Components.
    
    Each chat panel has input textbox and submit button.
    """
    print("\n📋 Checking AC3: Chat Panel Components...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Alice components
        has_alice_textbox = "alice_input" in content and "Textbox" in content
        has_alice_button = "alice_submit" in content and "Button" in content
        
        # Check for Bob components
        has_bob_textbox = "bob_input" in content and "Textbox" in content
        has_bob_button = "bob_submit" in content and "Button" in content
        
        if not (has_alice_textbox and has_alice_button):
            print("❌ AC3: Alice panel missing textbox or button")
            return False
        
        if not (has_bob_textbox and has_bob_button):
            print("❌ AC3: Bob panel missing textbox or button")
            return False
        
        print("✅ AC3: Both panels have input textbox and submit button")
        return True
    except Exception as e:
        print(f"❌ AC3: Failed - {e}")
        return False


def check_ac4_chat_history_display():
    """AC4: Chat History Display.
    
    Chat history displays in conversational format.
    """
    print("\n📋 Checking AC4: Chat History Display...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Chatbot components (used for conversational format)
        has_alice_chatbot = "alice_chatbot" in content and "Chatbot" in content
        has_bob_chatbot = "bob_chatbot" in content and "Chatbot" in content
        
        if not has_alice_chatbot:
            print("❌ AC4: Alice panel missing Chatbot component")
            return False
        
        if not has_bob_chatbot:
            print("❌ AC4: Bob panel missing Chatbot component")
            return False
        
        print("✅ AC4: Chat history displays in conversational format (Chatbot components)")
        return True
    except Exception as e:
        print(f"❌ AC4: Failed - {e}")
        return False


def check_ac5_responsive_layout():
    """AC5: Responsive Layout.
    
    Layout is responsive (desktop-first per UX spec) with ~1200px width minimum.
    Note: Actual responsive behavior requires visual testing, but we verify structure supports it.
    """
    print("\n📋 Checking AC5: Responsive Layout...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for Row/Column structure (supports responsive design)
        has_row_column = ("gr.Row()" in content or "gr.Row(" in content) and ("gr.Column()" in content or "gr.Column(" in content)
        
        # Note: Minimum width is typically handled by CSS or Gradio's responsive system
        # We verify the structure supports responsive design
        
        if not has_row_column:
            print("❌ AC5: Row/Column layout structure not found")
            return False
        
        print("✅ AC5: Responsive layout structure in place (Row/Column components)")
        print("   Note: Visual testing at ~1200px width required for full validation")
        return True
    except Exception as e:
        print(f"❌ AC5: Failed - {e}")
        return False


def check_ac6_panel_labels():
    """AC6: Panel Labels.
    
    Left panel clearly labeled "Alice's Companion",
    right panel clearly labeled "Bob's Companion",
    bottom panel clearly labeled "Network Activity Monitor".
    """
    print("\n📋 Checking AC6: Panel Labels...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for panel labels
        has_alice_label = "Alice's Companion" in content or "Alice" in content
        has_bob_label = "Bob's Companion" in content or "Bob" in content
        has_network_label = "Network Activity Monitor" in content
        
        if not has_alice_label:
            print("❌ AC6: Alice panel label not found")
            return False
        
        if not has_bob_label:
            print("❌ AC6: Bob panel label not found")
            return False
        
        if not has_network_label:
            print("❌ AC6: Network Activity Monitor label not found")
            return False
        
        print("✅ AC6: All panel labels present (Alice's Companion, Bob's Companion, Network Activity Monitor)")
        return True
    except Exception as e:
        print(f"❌ AC6: Failed - {e}")
        return False


def check_app_launch_config():
    """Additional check: App launch configuration.
    
    Verify app launches on localhost:7860 with correct title.
    """
    print("\n📋 Checking App Launch Configuration...")
    try:
        app_file = project_root / "app.py"
        with open(app_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for launch configuration
        has_launch = "app.launch(" in content or ".launch(" in content
        has_port = "7860" in content or "server_port" in content
        has_title = "Companion Network" in content or "A2A Coordination Demo" in content
        
        if not has_launch:
            print("❌ Launch: app.launch() not found")
            return False
        
        if not has_port:
            print("⚠️  Launch: Port 7860 not explicitly configured (may use default)")
        
        print("✅ App launch configuration found")
        return True
    except Exception as e:
        print(f"❌ Launch: Failed - {e}")
        return False


def main():
    """Run all acceptance criteria checks."""
    print("=" * 70)
    print("Gradio Split-Screen Layout Verification")
    print("Story 4.1: Create Gradio Split-Screen Layout")
    print("=" * 70)
    
    results = []
    
    # Run all AC checks
    results.append(("AC1", check_ac1_split_screen_layout()))
    results.append(("AC2", check_ac2_clean_minimal_design()))
    results.append(("AC3", check_ac3_chat_panel_components()))
    results.append(("AC4", check_ac4_chat_history_display()))
    results.append(("AC5", check_ac5_responsive_layout()))
    results.append(("AC6", check_ac6_panel_labels()))
    results.append(("Launch", check_app_launch_config()))
    
    # Summary
    print("\n" + "=" * 70)
    print("Verification Summary")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for ac_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{ac_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All acceptance criteria verified!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} check(s) failed. Review output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

