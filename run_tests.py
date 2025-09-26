#!/usr/bin/env python3
"""
Comprehensive test runner for the Weather Forecast Microservice.

This script runs all test suites including unit tests, integration tests,
accuracy tests, and performance tests.
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*60)
    
    try:
        result = subprocess.run(command, shell=True, check=True, 
                              capture_output=False, text=True)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED")
        print(f"Exit code: {e.returncode}")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False


def check_requirements():
    """Check if test requirements are installed."""
    try:
        import pytest
        import httpx
        print("✅ Test dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing test dependencies: {e}")
        print("Install with: pip install -r requirements.txt")
        return False


def run_unit_tests():
    """Run unit tests."""
    commands = [
        ("python -m pytest tests/test_weather_service.py -v", "Unit Tests - Weather Service"),
        ("python -m pytest tests/test_api.py -v", "Unit Tests - API Endpoints")
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    return all(results)


def run_accuracy_tests():
    """Run accuracy and reliability tests."""
    command = "python -m pytest tests/test_accuracy_reliability.py -v"
    return run_command(command, "Accuracy and Reliability Tests")


def run_integration_tests():
    """Run integration tests (requires running service)."""
    print("\n" + "="*60)
    print("INTEGRATION TESTS")
    print("Note: These tests require the service to be running on localhost:8080")
    print("="*60)
    
    # Check if service is running
    try:
        import httpx
        import asyncio
        
        async def check_service():
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get("http://localhost:8080/health", timeout=5.0)
                    return response.status_code == 200
            except:
                return False
        
        service_running = asyncio.run(check_service())
        
        if not service_running:
            print("⚠️  Service is not running. Starting integration tests anyway...")
            print("   Some tests may fail if the service is not available.")
        else:
            print("✅ Service is running on localhost:8080")
        
    except Exception as e:
        print(f"⚠️  Could not check service status: {e}")
    
    # Run integration tests with markers
    command = "python -m pytest tests/ -v -m 'not unit' --tb=short"
    return run_command(command, "Integration Tests")


def run_load_tests():
    """Run load tests."""
    print("\n" + "="*60)
    print("LOAD TESTS")
    print("Note: These tests require the service to be running on localhost:8080")
    print("="*60)
    
    command = "python tests/load_test.py --test health"
    return run_command(command, "Load Tests - Health Endpoint")


def run_coverage_analysis():
    """Run tests with coverage analysis."""
    commands = [
        ("coverage erase", "Clear previous coverage data"),
        ("coverage run -m pytest tests/test_weather_service.py tests/test_api.py", "Run tests with coverage"),
        ("coverage report", "Generate coverage report"),
        ("coverage html", "Generate HTML coverage report")
    ]
    
    results = []
    for command, description in commands:
        results.append(run_command(command, description))
    
    if all(results):
        print("\n📊 Coverage report generated in htmlcov/index.html")
    
    return all(results)


def run_all_tests(include_load=False, include_coverage=False):
    """Run all test suites."""
    print("🧪 Starting comprehensive test suite...")
    
    results = {
        "requirements_check": check_requirements(),
        "unit_tests": False,
        "accuracy_tests": False,
        "integration_tests": False,
        "load_tests": False,
        "coverage_analysis": False
    }
    
    if not results["requirements_check"]:
        print("❌ Cannot continue without required dependencies")
        return results
    
    # Run unit tests
    results["unit_tests"] = run_unit_tests()
    
    # Run accuracy tests
    results["accuracy_tests"] = run_accuracy_tests()
    
    # Run integration tests
    results["integration_tests"] = run_integration_tests()
    
    # Run load tests if requested
    if include_load:
        results["load_tests"] = run_load_tests()
    
    # Run coverage analysis if requested
    if include_coverage:
        results["coverage_analysis"] = run_coverage_analysis()
    
    return results


def print_summary(results):
    """Print test results summary."""
    print("\n" + "="*80)
    print("TEST RESULTS SUMMARY")
    print("="*80)
    
    total_tests = len([k for k in results.keys() if not k.endswith('_check')])
    passed_tests = len([k for k, v in results.items() if v and not k.endswith('_check')])
    
    for test_name, result in results.items():
        if test_name.endswith('_check'):
            continue
        
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name.replace('_', ' ').title(): <25} {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed successfully!")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed_tests == total_tests


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Comprehensive test runner for Weather Forecast Microservice')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--accuracy', action='store_true', help='Run only accuracy tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--load', action='store_true', help='Include load tests')
    parser.add_argument('--coverage', action='store_true', help='Include coverage analysis')
    parser.add_argument('--all', action='store_true', help='Run all tests (default)')
    
    args = parser.parse_args()
    
    # If no specific test is requested, run all
    if not any([args.unit, args.accuracy, args.integration, args.load, args.coverage]):
        args.all = True
    
    # Check if we're in the right directory
    if not os.path.exists('app/main.py'):
        print("❌ Error: Please run this script from the project root directory")
        print("   Expected to find app/main.py in current directory")
        sys.exit(1)
    
    try:
        if args.all:
            results = run_all_tests(include_load=args.load, include_coverage=args.coverage)
            success = print_summary(results)
        else:
            results = {}
            
            if not check_requirements():
                sys.exit(1)
            
            if args.unit:
                results["unit_tests"] = run_unit_tests()
            
            if args.accuracy:
                results["accuracy_tests"] = run_accuracy_tests()
            
            if args.integration:
                results["integration_tests"] = run_integration_tests()
            
            if args.load:
                results["load_tests"] = run_load_tests()
            
            if args.coverage:
                results["coverage_analysis"] = run_coverage_analysis()
            
            success = print_summary(results)
        
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Test execution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()