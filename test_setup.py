#!/usr/bin/env python3
"""
Test script to verify City Desk project setup.
Checks dependencies, file structure, and basic functionality.
"""

import os
import sys
import json
from pathlib import Path

def test_file_structure():
    """Test that all required files and directories exist."""
    print("🔍 Testing file structure...")
    
    required_files = [
        'template.yaml',
        'requirements.txt',
        'deploy.sh',
        'README.md',
        'src/lambda_function.py',
        'src/authorizer.py',
        'scripts/ingest_data.py',
        'events/test-event.json'
    ]
    
    required_dirs = [
        'src',
        'scripts',
        'events',
        'sample-documents'
    ]
    
    all_good = True
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - MISSING")
            all_good = False
    
    for dir_path in required_dirs:
        if os.path.isdir(dir_path):
            print(f"  ✅ {dir_path}/")
        else:
            print(f"  ❌ {dir_path}/ - MISSING")
            all_good = False
    
    return all_good

def test_python_dependencies():
    """Test that Python dependencies can be imported."""
    print("\n🐍 Testing Python dependencies...")
    
    try:
        import boto3
        print("  ✅ boto3")
    except ImportError:
        print("  ❌ boto3 - Install with: pip install boto3")
        return False
    
    try:
        import botocore
        print("  ✅ botocore")
    except ImportError:
        print("  ❌ botocore - Install with: pip install botocore")
        return False
    
    return True

def test_sam_template():
    """Test that the SAM template is valid YAML."""
    print("\n📋 Testing SAM template...")
    
    try:
        import yaml
        print("  ✅ PyYAML available")
    except ImportError:
        print("  ⚠️  PyYAML not available - template validation skipped")
        return True
    
    try:
        with open('template.yaml', 'r') as f:
            yaml.safe_load(f)
        print("  ✅ template.yaml is valid YAML")
        return True
    except Exception as e:
        print(f"  ❌ template.yaml validation failed: {e}")
        return False

def test_lambda_functions():
    """Test that Lambda functions have valid Python syntax."""
    print("\n🔧 Testing Lambda functions...")
    
    lambda_files = [
        'src/lambda_function.py',
        'src/authorizer.py'
    ]
    
    all_good = True
    
    for file_path in lambda_files:
        try:
            with open(file_path, 'r') as f:
                compile(f.read(), file_path, 'exec')
            print(f"  ✅ {file_path} - Valid Python syntax")
        except SyntaxError as e:
            print(f"  ❌ {file_path} - Syntax error: {e}")
            all_good = False
        except Exception as e:
            print(f"  ❌ {file_path} - Error: {e}")
            all_good = False
    
    return all_good

def test_sample_documents():
    """Test that sample documents exist and are readable."""
    print("\n📚 Testing sample documents...")
    
    sample_dir = Path('sample-documents')
    if not sample_dir.exists():
        print("  ❌ sample-documents/ directory not found")
        return False
    
    doc_count = 0
    for file_path in sample_dir.rglob('*'):
        if file_path.is_file():
            doc_count += 1
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"  ✅ {file_path.relative_to(sample_dir)} ({len(content)} chars)")
            except Exception as e:
                print(f"  ❌ {file_path.relative_to(sample_dir)} - Error reading: {e}")
    
    if doc_count == 0:
        print("  ⚠️  No sample documents found")
    else:
        print(f"  📊 Found {doc_count} sample documents")
    
    return True

def test_deployment_script():
    """Test that the deployment script is executable."""
    print("\n🚀 Testing deployment script...")
    
    script_path = 'deploy.sh'
    if not os.path.exists(script_path):
        print(f"  ❌ {script_path} not found")
        return False
    
    if os.access(script_path, os.X_OK):
        print(f"  ✅ {script_path} is executable")
        return True
    else:
        print(f"  ⚠️  {script_path} is not executable - run: chmod +x {script_path}")
        return False

def main():
    """Run all tests."""
    print("🧪 City Desk Project Setup Test")
    print("=" * 40)
    
    tests = [
        test_file_structure,
        test_python_dependencies,
        test_sam_template,
        test_lambda_functions,
        test_sample_documents,
        test_deployment_script
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 40)
    print("📊 Test Results Summary")
    print("=" * 40)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 All {total} tests passed! Project is ready for deployment.")
        print("\n🚀 Next steps:")
        print("1. Configure AWS credentials: aws configure")
        print("2. Install AWS SAM CLI")
        print("3. Deploy: ./deploy.sh dev us-east-1")
    else:
        print(f"⚠️  {passed}/{total} tests passed. Please fix the issues above.")
        print("\n🔧 Common fixes:")
        print("- Install dependencies: pip install -r requirements.txt")
        print("- Make script executable: chmod +x deploy.sh")
        print("- Check file paths and permissions")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
