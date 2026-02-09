#!/usr/bin/env python3
"""
Scene Engine API Test Runner

TaskMaster Task 47.7: Test Execution Script
Comprehensive test runner for Scene Engine API with different test categories,
reporting options, and performance measurement.
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))


class APITestRunner:
    """Test runner for Scene Engine API tests"""
    
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.project_root = self.test_dir.parent.parent.parent
        self.reports_dir = self.test_dir / "reports"
        self.reports_dir.mkdir(exist_ok=True)
    
    def run_command(self, command: list, capture_output: bool = True) -> tuple:
        """Run a command and return (success, output)"""
        try:
            if capture_output:
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root
                )
                return result.returncode == 0, result.stdout + result.stderr
            else:
                result = subprocess.run(command, cwd=self.project_root)
                return result.returncode == 0, ""
        except Exception as e:
            return False, str(e)
    
    def install_test_dependencies(self):
        """Install test dependencies"""
        print("Installing test dependencies...")
        requirements_file = self.test_dir / "requirements-test.txt"
        
        success, output = self.run_command([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        
        if not success:
            print(f"Failed to install dependencies: {output}")
            return False
        
        print("Test dependencies installed successfully.")
        return True
    
    def run_integration_tests(self, verbose: bool = False, coverage: bool = False):
        """Run integration tests"""
        print("\n" + "="*60)
        print("RUNNING INTEGRATION TESTS")
        print("="*60)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_scene_engine_integration.py"),
            "-v" if verbose else "-q",
            "--tb=short"
        ]
        
        if coverage:
            command.extend([
                "--cov=src.api",
                "--cov=src.scene_engine",
                f"--cov-report=html:{self.reports_dir}/coverage_integration",
                f"--cov-report=xml:{self.reports_dir}/coverage_integration.xml"
            ])
        
        # Add HTML report
        command.extend([
            f"--html={self.reports_dir}/integration_report.html",
            "--self-contained-html"
        ])
        
        start_time = time.time()
        success, output = self.run_command(command, capture_output=False)
        execution_time = time.time() - start_time
        
        print(f"\nIntegration tests completed in {execution_time:.2f} seconds")
        print(f"Report generated: {self.reports_dir}/integration_report.html")
        
        return success
    
    def run_performance_tests(self, verbose: bool = False, include_stress: bool = False):
        """Run performance tests"""
        print("\n" + "="*60)
        print("RUNNING PERFORMANCE TESTS")
        print("="*60)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_scene_engine_performance.py"),
            "-v" if verbose else "-q",
            "--tb=short",
            "--benchmark-only",
            "--benchmark-sort=mean"
        ]
        
        if include_stress:
            command.extend(["-m", "stress"])
        else:
            command.extend(["-m", "not stress"])
        
        # Add performance reporting
        command.extend([
            f"--html={self.reports_dir}/performance_report.html",
            "--self-contained-html",
            f"--benchmark-json={self.reports_dir}/benchmark_results.json"
        ])
        
        start_time = time.time()
        success, output = self.run_command(command, capture_output=False)
        execution_time = time.time() - start_time
        
        print(f"\nPerformance tests completed in {execution_time:.2f} seconds")
        print(f"Report generated: {self.reports_dir}/performance_report.html")
        print(f"Benchmark data: {self.reports_dir}/benchmark_results.json")
        
        return success
    
    def run_all_tests(self, verbose: bool = False, coverage: bool = True):
        """Run all API tests"""
        print("\n" + "="*60)
        print("RUNNING ALL SCENE ENGINE API TESTS")
        print("="*60)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir),
            "-v" if verbose else "",
            "--tb=short",
            "-m", "not stress"  # Exclude stress tests by default
        ]
        
        command = [cmd for cmd in command if cmd]  # Remove empty strings
        
        if coverage:
            command.extend([
                "--cov=src.api",
                "--cov=src.scene_engine", 
                f"--cov-report=html:{self.reports_dir}/coverage_full",
                f"--cov-report=xml:{self.reports_dir}/coverage_full.xml",
                "--cov-report=term-missing"
            ])
        
        # Add comprehensive reporting
        command.extend([
            f"--html={self.reports_dir}/full_test_report.html",
            "--self-contained-html",
            f"--json-report={self.reports_dir}/test_results.json"
        ])
        
        start_time = time.time()
        success, output = self.run_command(command, capture_output=False)
        execution_time = time.time() - start_time
        
        print(f"\nAll tests completed in {execution_time:.2f} seconds")
        print(f"Full report generated: {self.reports_dir}/full_test_report.html")
        
        if coverage:
            print(f"Coverage report: {self.reports_dir}/coverage_full/index.html")
        
        return success
    
    def run_quick_smoke_test(self):
        """Run a quick smoke test to verify basic functionality"""
        print("\n" + "="*60)
        print("RUNNING QUICK SMOKE TEST")
        print("="*60)
        
        command = [
            sys.executable, "-m", "pytest",
            str(self.test_dir / "test_scene_engine_integration.py"),
            "-k", "test_plan_proactive_scene_success or test_get_scene_success",
            "-v",
            "--tb=short"
        ]
        
        start_time = time.time()
        success, output = self.run_command(command, capture_output=False)
        execution_time = time.time() - start_time
        
        print(f"\nSmoke test completed in {execution_time:.2f} seconds")
        return success
    
    def generate_test_summary(self):
        """Generate a test summary report"""
        summary_file = self.reports_dir / "test_summary.txt"
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("Scene Engine API Test Summary\n")
            f.write("=" * 40 + "\n\n")
            
            f.write(f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Test directory: {self.test_dir}\n")
            f.write(f"Reports directory: {self.reports_dir}\n\n")
            
            f.write("Available Test Categories:\n")
            f.write("- Integration Tests: Full API endpoint testing\n")
            f.write("- Performance Tests: Response time and load testing\n") 
            f.write("- Stress Tests: Extended load testing\n\n")
            
            f.write("Key Test Files:\n")
            f.write(f"- {self.test_dir}/test_scene_engine_integration.py\n")
            f.write(f"- {self.test_dir}/test_scene_engine_performance.py\n")
            f.write(f"- {self.test_dir}/conftest.py\n\n")
            
            f.write("Report Files:\n")
            for report_file in self.reports_dir.glob("*.html"):
                f.write(f"- {report_file.name}\n")
        
        print(f"Test summary generated: {summary_file}")


def main():
    """Main test runner entry point"""
    parser = argparse.ArgumentParser(
        description="Scene Engine API Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py --quick                    # Quick smoke test
  python run_tests.py --integration --verbose    # Run integration tests with verbose output
  python run_tests.py --performance              # Run performance tests
  python run_tests.py --all --coverage          # Run all tests with coverage
  python run_tests.py --install-deps            # Install test dependencies
        """
    )
    
    # Test type arguments
    parser.add_argument("--quick", action="store_true", help="Run quick smoke test")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--performance", action="store_true", help="Run performance tests")
    parser.add_argument("--stress", action="store_true", help="Include stress tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Options
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--coverage", action="store_true", help="Generate coverage reports")
    parser.add_argument("--install-deps", action="store_true", help="Install test dependencies")
    parser.add_argument("--summary", action="store_true", help="Generate test summary")
    
    args = parser.parse_args()
    
    runner = APITestRunner()
    
    # Handle install dependencies
    if args.install_deps:
        if not runner.install_test_dependencies():
            sys.exit(1)
        return
    
    # Handle summary generation
    if args.summary:
        runner.generate_test_summary()
        return
    
    # Determine which tests to run
    tests_run = False
    overall_success = True
    
    if args.quick:
        success = runner.run_quick_smoke_test()
        overall_success = overall_success and success
        tests_run = True
    
    if args.integration:
        success = runner.run_integration_tests(
            verbose=args.verbose,
            coverage=args.coverage
        )
        overall_success = overall_success and success
        tests_run = True
    
    if args.performance:
        success = runner.run_performance_tests(
            verbose=args.verbose,
            include_stress=args.stress
        )
        overall_success = overall_success and success
        tests_run = True
    
    if args.all:
        success = runner.run_all_tests(
            verbose=args.verbose,
            coverage=args.coverage
        )
        overall_success = overall_success and success
        tests_run = True
    
    # If no specific test type was specified, run quick test
    if not tests_run:
        print("No test type specified. Running quick smoke test...")
        success = runner.run_quick_smoke_test()
        overall_success = overall_success and success
    
    # Generate summary
    runner.generate_test_summary()
    
    # Exit with appropriate code
    if overall_success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()