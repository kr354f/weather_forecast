"""
Load testing script for the Weather Forecast Microservice.

This script performs load testing to validate the service's performance
under various load conditions.
"""

import asyncio
import httpx
import time
import statistics
from typing import List, Dict
from dataclasses import dataclass
import argparse


@dataclass
class LoadTestResult:
    """Results from a load test run."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    min_response_time: float
    max_response_time: float
    requests_per_second: float
    error_rate: float


class WeatherServiceLoadTester:
    """Load tester for the weather service."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.results: List[float] = []
        self.errors: List[str] = []
    
    async def single_request(self, endpoint: str, params: Dict = None) -> Dict:
        """Make a single request and return timing and status info."""
        start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}{endpoint}",
                    params=params or {},
                    timeout=30.0
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    'success': response.status_code == 200,
                    'status_code': response.status_code,
                    'response_time': response_time,
                    'error': None
                }
                
            except Exception as e:
                end_time = time.time()
                response_time = end_time - start_time
                
                return {
                    'success': False,
                    'status_code': None,
                    'response_time': response_time,
                    'error': str(e)
                }
    
    async def run_concurrent_requests(self, 
                                    endpoint: str, 
                                    params: Dict, 
                                    num_requests: int, 
                                    concurrent_users: int) -> LoadTestResult:
        """Run concurrent requests and collect performance metrics."""
        
        print(f"Starting load test: {num_requests} requests with {concurrent_users} concurrent users")
        print(f"Endpoint: {endpoint}")
        print(f"Parameters: {params}")
        
        start_time = time.time()
        
        # Create semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(concurrent_users)
        
        async def bounded_request():
            async with semaphore:
                return await self.single_request(endpoint, params)
        
        # Execute all requests
        tasks = [bounded_request() for _ in range(num_requests)]
        results = await asyncio.gather(*tasks)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Analyze results
        successful_requests = sum(1 for r in results if r['success'])
        failed_requests = num_requests - successful_requests
        response_times = [r['response_time'] for r in results]
        
        # Calculate metrics
        avg_response_time = statistics.mean(response_times) if response_times else 0
        min_response_time = min(response_times) if response_times else 0
        max_response_time = max(response_times) if response_times else 0
        requests_per_second = num_requests / total_duration if total_duration > 0 else 0
        error_rate = (failed_requests / num_requests) * 100 if num_requests > 0 else 0
        
        # Collect error details
        errors = [r['error'] for r in results if r['error']]
        status_codes = [r['status_code'] for r in results if r['status_code']]
        
        print(f"\nLoad Test Results:")
        print(f"Total Duration: {total_duration:.2f} seconds")
        print(f"Successful Requests: {successful_requests}")
        print(f"Failed Requests: {failed_requests}")
        print(f"Error Rate: {error_rate:.2f}%")
        print(f"Requests/Second: {requests_per_second:.2f}")
        print(f"Avg Response Time: {avg_response_time:.3f} seconds")
        print(f"Min Response Time: {min_response_time:.3f} seconds")
        print(f"Max Response Time: {max_response_time:.3f} seconds")
        
        if errors:
            print(f"\nError Summary:")
            error_counts = {}
            for error in errors:
                error_counts[error] = error_counts.get(error, 0) + 1
            for error, count in error_counts.items():
                print(f"  {error}: {count} times")
        
        if status_codes:
            status_counts = {}
            for code in status_codes:
                status_counts[code] = status_counts.get(code, 0) + 1
            print(f"\nStatus Code Summary:")
            for code, count in sorted(status_counts.items()):
                print(f"  {code}: {count} times")
        
        return LoadTestResult(
            total_requests=num_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            min_response_time=min_response_time,
            max_response_time=max_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate
        )
    
    async def run_health_check_test(self):
        """Test the health endpoint under load."""
        print("=" * 60)
        print("HEALTH CHECK LOAD TEST")
        print("=" * 60)
        
        return await self.run_concurrent_requests(
            endpoint="/health",
            params={},
            num_requests=100,
            concurrent_users=10
        )
    
    async def run_current_weather_test(self):
        """Test the current weather endpoint under load."""
        print("\n" + "=" * 60)
        print("CURRENT WEATHER LOAD TEST")
        print("=" * 60)
        
        cities = ["London", "Paris", "Tokyo", "New York", "Sydney"]
        
        results = []
        for city in cities:
            print(f"\nTesting with city: {city}")
            result = await self.run_concurrent_requests(
                endpoint="/api/v1/weather/current",
                params={"city": city},
                num_requests=20,
                concurrent_users=5
            )
            results.append(result)
        
        return results
    
    async def run_forecast_test(self):
        """Test the forecast endpoint under load."""
        print("\n" + "=" * 60)
        print("WEATHER FORECAST LOAD TEST")
        print("=" * 60)
        
        return await self.run_concurrent_requests(
            endpoint="/api/v1/weather/forecast",
            params={"city": "London", "days": 3},
            num_requests=50,
            concurrent_users=8
        )
    
    async def run_stress_test(self):
        """Run a stress test with high concurrent load."""
        print("\n" + "=" * 60)
        print("STRESS TEST - HIGH CONCURRENT LOAD")
        print("=" * 60)
        
        return await self.run_concurrent_requests(
            endpoint="/health",
            params={},
            num_requests=500,
            concurrent_users=50
        )
    
    async def run_endurance_test(self, duration_minutes: int = 5):
        """Run an endurance test for a specified duration."""
        print(f"\n" + "=" * 60)
        print(f"ENDURANCE TEST - {duration_minutes} MINUTES")
        print("=" * 60)
        
        end_time = time.time() + (duration_minutes * 60)
        request_count = 0
        successful_requests = 0
        
        while time.time() < end_time:
            result = await self.single_request("/health", {})
            request_count += 1
            if result['success']:
                successful_requests += 1
            
            # Wait between requests to simulate realistic usage
            await asyncio.sleep(0.5)
            
            # Progress indicator
            if request_count % 20 == 0:
                elapsed = time.time() - (end_time - duration_minutes * 60)
                print(f"Progress: {elapsed/60:.1f}/{duration_minutes} minutes, "
                      f"Requests: {request_count}, Success rate: {successful_requests/request_count*100:.1f}%")
        
        success_rate = (successful_requests / request_count * 100) if request_count > 0 else 0
        
        print(f"\nEndurance Test Results:")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Total Requests: {request_count}")
        print(f"Successful Requests: {successful_requests}")
        print(f"Success Rate: {success_rate:.2f}%")
        
        return {
            'duration_minutes': duration_minutes,
            'total_requests': request_count,
            'successful_requests': successful_requests,
            'success_rate': success_rate
        }


async def main():
    """Main function to run load tests."""
    parser = argparse.ArgumentParser(description='Weather Service Load Tester')
    parser.add_argument('--url', default='http://localhost:8080', 
                       help='Base URL of the weather service')
    parser.add_argument('--test', choices=['all', 'health', 'current', 'forecast', 'stress', 'endurance'],
                       default='all', help='Type of test to run')
    parser.add_argument('--endurance-duration', type=int, default=2,
                       help='Duration for endurance test in minutes')
    
    args = parser.parse_args()
    
    tester = WeatherServiceLoadTester(args.url)
    
    try:
        if args.test in ['all', 'health']:
            await tester.run_health_check_test()
        
        if args.test in ['all', 'current']:
            await tester.run_current_weather_test()
        
        if args.test in ['all', 'forecast']:
            await tester.run_forecast_test()
        
        if args.test in ['all', 'stress']:
            await tester.run_stress_test()
        
        if args.test in ['all', 'endurance']:
            await tester.run_endurance_test(args.endurance_duration)
        
        print("\n" + "=" * 60)
        print("LOAD TESTING COMPLETED")
        print("=" * 60)
        
    except KeyboardInterrupt:
        print("\nLoad testing interrupted by user")
    except Exception as e:
        print(f"\nLoad testing failed with error: {e}")


if __name__ == "__main__":
    asyncio.run(main())