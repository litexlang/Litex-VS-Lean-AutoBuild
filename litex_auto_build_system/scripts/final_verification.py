#!/usr/bin/env python3
"""
Final validation script: Confirm experiment can run and reproduce with one click
"""

import sys
import os
from pathlib import Path

# Set environment variables (using relative path)
script_dir = Path(__file__).resolve().parent
litex_bin = script_dir.parent.parent / "LitexGeo" / "golitex" / "target" / "release" / "litex"
os.environ["LITEX_BIN"] = str(litex_bin)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

def check_environment():
    """Check runtime environment"""
    print("\n" + "="*60)
    print("1. Environment check")
    print("="*60)

    # Python version
    print(f"Python version: {sys.version.split()[0]}")

    # OpenAI library
    try:
        import openai
        print("✅ openai library installed")
    except ImportError:
        print("❌ openai library not installed")
        return False

    # Litex compiler
    litex_bin = os.environ.get("LITEX_BIN")
    if litex_bin and Path(litex_bin).exists():
        print(f"✅ Litex compiler: {Path(litex_bin).name}")
    else:
        print("❌ Litex compiler not found")
        return False

    return True

def check_seed_files():
    """Check seed library files"""
    print("\n" + "="*60)
    print("2. Seed library check")
    print("="*60)

    base_dir = Path(__file__).resolve().parent.parent
    seeds = {
        "Definition": base_dir / "database/definition_library_seed.lit",
        "Theorem": base_dir / "database/theorem_library_seed.lit"
    }

    all_exist = True
    for name, path in seeds.items():
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {name:12s}: {path} ({size} bytes)")
        else:
            print(f"❌ {name:12s}: {path} (does not exist)")
            all_exist = False

    return all_exist

def check_scripts():
    """Check script files"""
    print("\n" + "="*60)
    print("3. Script check")
    print("="*60)

    base_dir = Path(__file__).resolve().parent
    scripts = {
        "Definition script": base_dir / "run_litex_definitions.py",
        "Theorem script": base_dir / "run_litex_theorems.py",
        "One-click run script": base_dir / "run_all_experiments.sh",
        "Validator": base_dir / "litex_session.py"
    }

    all_exist = True
    for name, path in scripts.items():
        if path.exists():
            print(f"✅ {name:20s}: {path.name}")
        else:
            print(f"❌ {name:20s}: {path} (does not exist)")
            all_exist = False

    return all_exist

def test_import():
    """Test script imports"""
    print("\n" + "="*60)
    print("4. Import Test")
    print("="*60)

    # Add scripts directory to Python path
    scripts_dir = Path(__file__).resolve().parent
    sys.path.insert(0, str(scripts_dir))

    try:
        from run_litex_definitions import LitexExperimentWithValidation, LITEX_TASKS as def_tasks
        print(f"✅ Definition script import success ({len(def_tasks)} tasks)")
    except Exception as e:
        print(f"❌ Definition script import failed: {e}")
        return False

    try:
        from run_litex_theorems import LitexExperimentWithValidation as TheoremExp, LITEX_TASKS as thm_tasks
        print(f"✅ Theorem script import success ({len(thm_tasks)} tasks)")
    except Exception as e:
        print(f"❌ Theorem script import failed: {e}")
        return False

    return True

def test_validator():
    """Test validator"""
    print("\n" + "="*60)
    print("5. Validator test")
    print("="*60)

    try:
        from litex_session import SessionBackedValidator, find_litex_bin

        litex_bin = find_litex_bin()
        if not litex_bin:
            print("❌ Litex compiler not found")
            return False

        print(f"✅ Litex compiler: {Path(litex_bin).name}")

        # Test Definition validator
        seed_file = Path("database/definition_library_seed.lit")
        seed = seed_file.read_text(encoding='utf-8')
        validator = SessionBackedValidator(seed, frame_timeout=30.0)

        if validator.session and validator.session.alive:
            print("✅ Session mode initialization success")
            validator.close()
        else:
            print("❌ Session mode initialization failed")
            return False

    except Exception as e:
        print(f"❌ Validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    return True

def main():
    print("\n" + "="*60)
    print("LitexGeo experiment final validation")
    print("="*60)

    checks = [
        ("Environment", check_environment),
        ("Seed library", check_seed_files),
        ("Scripts", check_scripts),
        ("Import", test_import),
        ("Validator", test_validator)
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))

    # Summary
    print("\n" + "="*60)
    print("Validation summary")
    print("="*60)

    all_passed = True
    for name, result in results:
        status = "✅ Passed" if result else "❌ Failed"
        print(f"{name:15s}: {status}")
        if not result:
            all_passed = False

    print("\n" + "="*60)
    if all_passed:
        print("🎉 All checks passed! Experiment can run with one click.")
        print("="*60)
        print("\nHow to run:")
        print("\nMethod 1: Test mode (recommended to run first)")
        print("  ./run_all_experiments.sh --test")
        print("  Estimated time: 20-30 minutes (3 tasks per experiment)")
        print("\nMethod 2: Full run")
        print("  ./run_all_experiments.sh")
        print("  Estimated time: 6-10 hours (Definition 39 + Theorem 165 tasks)")
        print("\nMethod 3: Run separately")
        print("  ./run_all_experiments.sh --def-only  # Run Definition only")
        print("  ./run_all_experiments.sh --thm-only  # Run Theorem only")
        print("\nSee USAGE_GUIDE.md for detailed instructions")
    else:
        print("❌ Some checks failed, please resolve the above issues first.")
        print("="*60)

    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
