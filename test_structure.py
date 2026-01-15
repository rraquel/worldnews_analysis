#!/usr/bin/env python3
"""
Test script to verify project structure without requiring dependencies
"""

import os
import sys
from pathlib import Path


def test_directory_structure():
    """Test that all required directories exist"""
    required_dirs = [
        'src',
        'src/agents',
        'src/models',
        'src/utils',
        'data',
        'data/raw',
        'data/processed',
        'data/analysis'
    ]

    print("Testing directory structure...")
    all_exist = True
    for dir_path in required_dirs:
        exists = os.path.isdir(dir_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {dir_path}")
        all_exist = all_exist and exists

    return all_exist


def test_required_files():
    """Test that all required files exist"""
    required_files = [
        'main.py',
        'requirements.txt',
        'README.md',
        'SETUP.md',
        'QUICKSTART.md',
        '.env.example',
        '.gitignore',
        'src/__init__.py',
        'src/models/__init__.py',
        'src/models/article.py',
        'src/utils/__init__.py',
        'src/utils/storage.py',
        'src/utils/nlp_utils.py',
        'src/agents/__init__.py',
        'src/agents/news_aggregator.py',
        'src/agents/event_clustering.py',
        'src/agents/rhetoric_analyzer.py',
        'src/agents/prediction_agent.py',
        'src/agents/coordinator.py'
    ]

    print("\nTesting required files...")
    all_exist = True
    for file_path in required_files:
        exists = os.path.isfile(file_path)
        status = "✅" if exists else "❌"
        print(f"  {status} {file_path}")
        all_exist = all_exist and exists

    return all_exist


def test_python_syntax():
    """Test that Python files have valid syntax"""
    import py_compile

    python_files = [
        'main.py',
        'src/__init__.py',
        'src/models/article.py',
        'src/utils/storage.py',
        'src/utils/nlp_utils.py',
        'src/agents/news_aggregator.py',
        'src/agents/event_clustering.py',
        'src/agents/rhetoric_analyzer.py',
        'src/agents/prediction_agent.py',
        'src/agents/coordinator.py'
    ]

    print("\nTesting Python syntax...")
    all_valid = True
    for file_path in python_files:
        try:
            py_compile.compile(file_path, doraise=True)
            print(f"  ✅ {file_path}")
        except py_compile.PyCompileError as e:
            print(f"  ❌ {file_path}: {e}")
            all_valid = False

    return all_valid


def main():
    print("="*60)
    print("World News Analysis System - Structure Test")
    print("="*60)
    print()

    results = []

    results.append(("Directory Structure", test_directory_structure()))
    results.append(("Required Files", test_required_files()))
    results.append(("Python Syntax", test_python_syntax()))

    print("\n" + "="*60)
    print("Test Results Summary")
    print("="*60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        all_passed = all_passed and passed

    print("\n" + "="*60)
    if all_passed:
        print("✅ All tests passed! Structure is correct.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Get API keys (see SETUP.md)")
        print("3. Create .env file with your keys")
        print("4. Run: python main.py --mode status")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
