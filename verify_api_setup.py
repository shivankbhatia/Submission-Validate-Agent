"""
Quick test script to verify API setup and endpoints

Run this to check if the API is configured correctly before starting.
"""

import sys
import os

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("Checking dependencies...")

    required_modules = [
        ('fastapi', 'FastAPI'),
        ('uvicorn', 'Uvicorn'),
        ('pandas', 'Pandas'),
        ('pydantic', 'Pydantic'),
    ]

    missing = []
    for module_name, display_name in required_modules:
        try:
            __import__(module_name)
            print(f"  ✓ {display_name}")
        except ImportError:
            print(f"  ✗ {display_name} - NOT INSTALLED")
            missing.append(module_name)

    if missing:
        print(f"\n❌ Missing dependencies: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False

    print("\n✅ All dependencies installed!\n")
    return True


def check_files():
    """Check if required files exist"""
    print("Checking required files...")

    required_files = [
        ('api/app.py', 'API Application'),
        ('submission2.csv', 'Submission Data'),
        ('data_management/data_manager.py', 'Data Manager'),
        ('core/evaluator.py', 'Evaluator'),
        ('frontend/.env', 'Frontend Environment Config'),
    ]

    missing = []
    for file_path, display_name in required_files:
        if os.path.exists(file_path):
            print(f"  ✓ {display_name}")
        else:
            print(f"  ✗ {display_name} - NOT FOUND at {file_path}")
            missing.append(file_path)

    if missing:
        print(f"\n⚠ Missing files: {', '.join(missing)}")
        return False

    print("\n✅ All required files present!\n")
    return True


def check_api_imports():
    """Check if API can be imported without errors"""
    print("Testing API imports...")

    try:
        sys.path.insert(0, os.getcwd())
        from api.app import app
        print("  ✓ API app imported successfully")

        # Check if endpoints are registered
        routes = [route.path for route in app.routes]
        print(f"  ✓ Found {len(routes)} routes")

        # Check for specific endpoints
        required_endpoints = [
            '/submit-evaluation',
            '/evaluate-stream/{roll_number}',
            '/submissions',
            '/submissions/stats'
        ]

        for endpoint in required_endpoints:
            if endpoint in routes:
                print(f"    ✓ {endpoint}")
            else:
                print(f"    ✗ {endpoint} - NOT FOUND")

        print("\n✅ API imports successful!\n")
        return True

    except Exception as e:
        print(f"\n❌ Error importing API: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("  API SETUP VERIFICATION")
    print("="*60 + "\n")

    checks = [
        ("Dependencies", check_dependencies),
        ("Required Files", check_files),
        ("API Imports", check_api_imports),
    ]

    results = []
    for name, check_func in checks:
        print(f"{'='*60}")
        result = check_func()
        results.append((name, result))
        print()

    # Summary
    print("="*60)
    print("  SUMMARY")
    print("="*60 + "\n")

    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
        if not result:
            all_passed = False

    print("\n" + "="*60)

    if all_passed:
        print("\n✅ All checks passed! You can start the API server.\n")
        print("Run: python start_api.bat  (Windows)")
        print("  or: ./start_api.sh       (Linux/Mac)")
        print("  or: uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload")
    else:
        print("\n❌ Some checks failed. Please fix the issues above before starting the API.\n")

    print("="*60 + "\n")


if __name__ == "__main__":
    main()
