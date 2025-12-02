"""Verification script for shared data models.

Validates all acceptance criteria for Story 2.1:
- AC1: UserContext Dataclass with all required fields
- AC2: EventProposal Dataclass with all required fields
- AC3: SharingRule Dataclass with all required fields
- AC4: Type hints for all fields
- AC5: Default factories prevent mutable default argument issues
- AC6: Models match architecture doc schema
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_ac1_usercontext():
    """AC1: UserContext Dataclass with all required fields."""
    print("\n📋 Checking AC1: UserContext Dataclass...")
    try:
        from shared.models import UserContext
        from dataclasses import fields
        
        # Check all required fields exist
        field_names = {f.name for f in fields(UserContext)}
        required_fields = {"user_id", "name", "preferences", "schedule", "trusted_contacts", "sharing_rules"}
        
        if not required_fields.issubset(field_names):
            missing = required_fields - field_names
            print(f"❌ AC1 FAILED: Missing fields: {missing}")
            return False
        
        # Check field types
        field_types = {f.name: f.type for f in fields(UserContext)}
        if field_types["user_id"] != str or field_types["name"] != str:
            print(f"❌ AC1 FAILED: Incorrect field types")
            return False
        
        # Test instantiation
        context = UserContext(user_id="test", name="Test")
        print("✅ AC1 PASSED: UserContext dataclass defined with all required fields")
        return True
    except Exception as e:
        print(f"❌ AC1 FAILED: {e}")
        return False


def check_ac2_eventproposal():
    """AC2: EventProposal Dataclass with all required fields."""
    print("\n📋 Checking AC2: EventProposal Dataclass...")
    try:
        from shared.models import EventProposal
        from dataclasses import fields
        
        # Check all required fields exist
        field_names = {f.name for f in fields(EventProposal)}
        required_fields = {"event_id", "proposer", "recipient", "status", "details", "timestamp"}
        
        if not required_fields.issubset(field_names):
            missing = required_fields - field_names
            print(f"❌ AC2 FAILED: Missing fields: {missing}")
            return False
        
        # Test instantiation
        proposal = EventProposal(
            event_id="test",
            proposer="alice",
            recipient="bob",
            status="pending",
            timestamp="2025-12-07T18:00:00"
        )
        print("✅ AC2 PASSED: EventProposal dataclass defined with all required fields")
        return True
    except Exception as e:
        print(f"❌ AC2 FAILED: {e}")
        return False


def check_ac3_sharingrule():
    """AC3: SharingRule Dataclass with all required fields."""
    print("\n📋 Checking AC3: SharingRule Dataclass...")
    try:
        from shared.models import SharingRule
        from dataclasses import fields
        
        # Check all required fields exist
        field_names = {f.name for f in fields(SharingRule)}
        required_fields = {"contact_id", "allowed_categories"}
        
        if not required_fields.issubset(field_names):
            missing = required_fields - field_names
            print(f"❌ AC3 FAILED: Missing fields: {missing}")
            return False
        
        # Test instantiation
        rule = SharingRule(contact_id="bob")
        print("✅ AC3 PASSED: SharingRule dataclass defined with all required fields")
        return True
    except Exception as e:
        print(f"❌ AC3 FAILED: {e}")
        return False


def check_ac4_type_hints():
    """AC4: Type hints for all fields."""
    print("\n📋 Checking AC4: Type hints...")
    try:
        from shared.models import UserContext, EventProposal, SharingRule
        from dataclasses import fields
        import typing
        
        all_models = [UserContext, EventProposal, SharingRule]
        for model in all_models:
            for field in fields(model):
                if field.type is None or field.type == type(None):
                    print(f"❌ AC4 FAILED: Field {model.__name__}.{field.name} missing type hint")
                    return False
        
        print("✅ AC4 PASSED: All fields have type hints")
        return True
    except Exception as e:
        print(f"❌ AC4 FAILED: {e}")
        return False


def check_ac5_default_factories():
    """AC5: Default factories prevent mutable default argument issues."""
    print("\n📋 Checking AC5: Default factories...")
    try:
        from shared.models import UserContext, EventProposal, SharingRule
        from dataclasses import fields
        
        # Check UserContext uses default_factory for mutable fields
        user_context_fields = {f.name: f for f in fields(UserContext)}
        if user_context_fields["preferences"].default_factory is None:
            print("❌ AC5 FAILED: UserContext.preferences missing default_factory")
            return False
        if user_context_fields["schedule"].default_factory is None:
            print("❌ AC5 FAILED: UserContext.schedule missing default_factory")
            return False
        if user_context_fields["trusted_contacts"].default_factory is None:
            print("❌ AC5 FAILED: UserContext.trusted_contacts missing default_factory")
            return False
        if user_context_fields["sharing_rules"].default_factory is None:
            print("❌ AC5 FAILED: UserContext.sharing_rules missing default_factory")
            return False
        
        # Check EventProposal uses default_factory for details
        event_proposal_fields = {f.name: f for f in fields(EventProposal)}
        if event_proposal_fields["details"].default_factory is None:
            print("❌ AC5 FAILED: EventProposal.details missing default_factory")
            return False
        
        # Check SharingRule uses default_factory for allowed_categories
        sharing_rule_fields = {f.name: f for f in fields(SharingRule)}
        if sharing_rule_fields["allowed_categories"].default_factory is None:
            print("❌ AC5 FAILED: SharingRule.allowed_categories missing default_factory")
            return False
        
        # Test that default_factory actually works (prevents shared mutable defaults)
        context1 = UserContext(user_id="alice", name="Alice")
        context2 = UserContext(user_id="bob", name="Bob")
        context1.preferences["test"] = "value"
        if "test" in context2.preferences:
            print("❌ AC5 FAILED: Default factories not working - mutable defaults are shared")
            return False
        
        print("✅ AC5 PASSED: Default factories prevent mutable default argument issues")
        return True
    except Exception as e:
        print(f"❌ AC5 FAILED: {e}")
        return False


def check_ac6_architecture_alignment():
    """AC6: Models match architecture doc schema."""
    print("\n📋 Checking AC6: Architecture alignment...")
    try:
        from shared.models import UserContext, EventProposal, SharingRule
        from dataclasses import fields
        
        # Check UserContext structure matches architecture doc
        user_context_fields = {f.name: f for f in fields(UserContext)}
        expected_user_context = {"user_id", "name", "preferences", "schedule", "trusted_contacts", "sharing_rules"}
        if set(user_context_fields.keys()) != expected_user_context:
            print(f"❌ AC6 FAILED: UserContext fields don't match architecture: {set(user_context_fields.keys())} vs {expected_user_context}")
            return False
        
        # Check EventProposal structure matches architecture doc
        event_proposal_fields = {f.name: f for f in fields(EventProposal)}
        expected_event_proposal = {"event_id", "proposer", "recipient", "status", "details", "timestamp"}
        if set(event_proposal_fields.keys()) != expected_event_proposal:
            print(f"❌ AC6 FAILED: EventProposal fields don't match architecture: {set(event_proposal_fields.keys())} vs {expected_event_proposal}")
            return False
        
        # Check SharingRule structure matches architecture doc
        sharing_rule_fields = {f.name: f for f in fields(SharingRule)}
        expected_sharing_rule = {"contact_id", "allowed_categories"}
        if set(sharing_rule_fields.keys()) != expected_sharing_rule:
            print(f"❌ AC6 FAILED: SharingRule fields don't match architecture: {set(sharing_rule_fields.keys())} vs {expected_sharing_rule}")
            return False
        
        print("✅ AC6 PASSED: Models match architecture doc schema")
        return True
    except Exception as e:
        print(f"❌ AC6 FAILED: {e}")
        return False


def main():
    """Run all acceptance criteria checks."""
    print("=" * 60)
    print("Verifying Story 2.1: Define User Context Data Models")
    print("=" * 60)
    
    checks = [
        ("AC1", check_ac1_usercontext),
        ("AC2", check_ac2_eventproposal),
        ("AC3", check_ac3_sharingrule),
        ("AC4", check_ac4_type_hints),
        ("AC5", check_ac5_default_factories),
        ("AC6", check_ac6_architecture_alignment),
    ]
    
    results = []
    for ac_id, check_func in checks:
        result = check_func()
        results.append((ac_id, result))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for ac_id, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{ac_id}: {status}")
    
    print(f"\nTotal: {passed}/{total} acceptance criteria passed")
    
    if passed == total:
        print("\n🎉 All acceptance criteria verified!")
        sys.exit(0)
    else:
        print(f"\n💥 {total - passed} acceptance criteria failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

