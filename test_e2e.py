#!/usr/bin/env python3
"""Comprehensive E2E tests for Speedify Dashboard API."""
import requests
import time
import sys

BASE_URL = "http://localhost:5000"
PASS = "\033[92mPASSED\033[0m"
FAIL = "\033[91mFAILED\033[0m"

results = []


def test(name, condition, details=""):
    """Record test result."""
    status = PASS if condition else FAIL
    results.append((name, condition, details))
    print(f"  [{status}] {name}")
    if details and not condition:
        print(f"           {details}")
    return condition


def test_main_page():
    """Test GET / returns the dashboard HTML."""
    print("\n=== Main Page Tests ===")
    try:
        r = requests.get(f"{BASE_URL}/", timeout=10)
        test("GET / returns 200", r.status_code == 200)
        test("GET / returns HTML", "text/html" in r.headers.get("Content-Type", ""))
        test("Response contains dashboard title", "Speedify Dashboard" in r.text)
        test("Response contains status-hero element", "status-hero" in r.text)
        test("Response contains JavaScript", "<script>" in r.text)
    except Exception as e:
        test("GET / request succeeded", False, str(e))


def test_status_api():
    """Test GET /api/status returns valid status data."""
    print("\n=== Status API Tests ===")
    try:
        r = requests.get(f"{BASE_URL}/api/status", timeout=10)
        test("GET /api/status returns 200", r.status_code == 200)
        test("Response is JSON", "application/json" in r.headers.get("Content-Type", ""))

        data = r.json()

        # Test overall section
        test("Response has 'overall' section", "overall" in data)
        if "overall" in data:
            overall = data["overall"]
            test("overall.state exists", "state" in overall)
            test("overall.status is valid", overall.get("status") in ["good", "warn", "bad"])
            test("overall.healthScore is number", isinstance(overall.get("healthScore"), (int, float)))
            test("overall.healthScore in range 0-100",
                 0 <= overall.get("healthScore", -1) <= 100,
                 f"Got: {overall.get('healthScore')}")
            test("overall.bondingMode exists", "bondingMode" in overall)
            test("overall.badIndicators is dict", isinstance(overall.get("badIndicators"), dict))

        # Test performance section
        test("Response has 'performance' section", "performance" in data)
        if "performance" in data:
            perf = data["performance"]
            test("performance.latency is number", isinstance(perf.get("latency"), (int, float)))
            test("performance.jitter is number", isinstance(perf.get("jitter"), (int, float)))
            test("performance.mos is number", isinstance(perf.get("mos"), (int, float)))
            test("performance.lossSend is number", isinstance(perf.get("lossSend"), (int, float)))
            test("performance.lossReceive is number", isinstance(perf.get("lossReceive"), (int, float)))
            test("performance.activeConnections is int", isinstance(perf.get("activeConnections"), int))

        # Test session section
        test("Response has 'session' section", "session" in data)
        if "session" in data:
            session = data["session"]
            test("session.uptime exists", "uptime" in session)
            test("session.bytesReceived exists", "bytesReceived" in session)
            test("session.bytesSent exists", "bytesSent" in session)
            test("session.failovers is int", isinstance(session.get("failovers"), int))

        # Test adapters section
        test("Response has 'adapters' section", "adapters" in data)
        test("adapters is list", isinstance(data.get("adapters"), list))

        # Test connections section
        test("Response has 'connections' section", "connections" in data)
        test("connections is list", isinstance(data.get("connections"), list))

    except Exception as e:
        test("GET /api/status request succeeded", False, str(e))


def test_server_api():
    """Test GET /api/server returns valid server data."""
    print("\n=== Server API Tests ===")
    try:
        r = requests.get(f"{BASE_URL}/api/server", timeout=10)
        test("GET /api/server returns 200", r.status_code == 200)
        test("Response is JSON", "application/json" in r.headers.get("Content-Type", ""))

        data = r.json()
        test("Response has 'location'", "location" in data)
        test("Response has 'publicIP'", "publicIP" in data)
        test("location is string", isinstance(data.get("location"), str))
        test("publicIP is string", isinstance(data.get("publicIP"), str))

    except Exception as e:
        test("GET /api/server request succeeded", False, str(e))


def test_change_mode_api():
    """Test POST /api/change-mode validation and functionality."""
    print("\n=== Change Mode API Tests ===")

    # Test missing body
    try:
        r = requests.post(f"{BASE_URL}/api/change-mode", timeout=10)
        test("POST without body returns 400", r.status_code == 400)
    except Exception as e:
        test("POST without body handled", False, str(e))

    # Test invalid JSON
    try:
        r = requests.post(f"{BASE_URL}/api/change-mode",
                         data="not json",
                         headers={"Content-Type": "application/json"},
                         timeout=10)
        test("POST with invalid JSON returns 400", r.status_code == 400)
    except Exception as e:
        test("POST with invalid JSON handled", False, str(e))

    # Test missing mode
    try:
        r = requests.post(f"{BASE_URL}/api/change-mode",
                         json={},
                         timeout=10)
        test("POST without mode returns 400", r.status_code == 400)
    except Exception as e:
        test("POST without mode handled", False, str(e))

    # Test invalid mode
    try:
        r = requests.post(f"{BASE_URL}/api/change-mode",
                         json={"mode": "invalid"},
                         timeout=10)
        test("POST with invalid mode returns 400", r.status_code == 400)
        data = r.json()
        test("Error message mentions valid modes", "speed" in data.get("error", "").lower())
    except Exception as e:
        test("POST with invalid mode handled", False, str(e))

    # Test valid mode change (redundant - safest option)
    try:
        r = requests.post(f"{BASE_URL}/api/change-mode",
                         json={"mode": "redundant"},
                         timeout=10)
        test("POST with valid mode returns 200", r.status_code == 200)
        data = r.json()
        test("Response has success=True", data.get("success") is True)
        test("Response has mode field", "mode" in data)
    except Exception as e:
        test("POST with valid mode handled", False, str(e))


def test_caching():
    """Test that response caching is working."""
    print("\n=== Response Caching Tests ===")

    # Test status API caching - make rapid requests and check timing
    try:
        # First request (cache miss)
        start = time.time()
        r1 = requests.get(f"{BASE_URL}/api/status", timeout=10)
        first_time = time.time() - start

        # Second request immediately after (should be cache hit)
        start = time.time()
        r2 = requests.get(f"{BASE_URL}/api/status", timeout=10)
        second_time = time.time() - start

        test("First status request succeeded", r1.status_code == 200)
        test("Second status request succeeded", r2.status_code == 200)

        # Cache hit should be significantly faster (at least 2x faster typically)
        # We're lenient here since network timing can vary
        test("Second request faster (cache hit)",
             second_time < first_time or second_time < 0.1,
             f"First: {first_time:.3f}s, Second: {second_time:.3f}s")

    except Exception as e:
        test("Status caching test completed", False, str(e))

    # Test server API caching
    try:
        start = time.time()
        r1 = requests.get(f"{BASE_URL}/api/server", timeout=10)
        first_time = time.time() - start

        start = time.time()
        r2 = requests.get(f"{BASE_URL}/api/server", timeout=10)
        second_time = time.time() - start

        test("First server request succeeded", r1.status_code == 200)
        test("Second server request succeeded", r2.status_code == 200)
        test("Server caching working",
             second_time < first_time or second_time < 0.1,
             f"First: {first_time:.3f}s, Second: {second_time:.3f}s")

    except Exception as e:
        test("Server caching test completed", False, str(e))

    # Test cache expiration (wait for cache to expire)
    print("  Waiting 2.5s for cache to expire...")
    time.sleep(2.5)

    try:
        start = time.time()
        r = requests.get(f"{BASE_URL}/api/status", timeout=10)
        elapsed = time.time() - start

        test("Request after cache expiry succeeded", r.status_code == 200)
        # After expiry, should take longer (CLI call needed)
        test("Cache expired (fresh data fetched)", elapsed > 0.05,
             f"Elapsed: {elapsed:.3f}s (expected >0.05s for CLI call)")

    except Exception as e:
        test("Cache expiry test completed", False, str(e))


def test_health_score_calculation():
    """Test health score is calculated correctly based on metrics."""
    print("\n=== Health Score Validation ===")
    try:
        r = requests.get(f"{BASE_URL}/api/status", timeout=10)
        data = r.json()

        overall = data.get("overall", {})
        perf = data.get("performance", {})

        health_score = overall.get("healthScore", 0)
        latency = perf.get("latency", 0)
        mos = perf.get("mos", 0)

        # Health score should correlate with metrics
        test("Health score is reasonable",
             0 <= health_score <= 100,
             f"Score: {health_score}")

        # If MOS is good (>4.0) and latency is low (<50ms), health should be high
        if mos >= 4.0 and latency < 50:
            test("High MOS + low latency = high health",
                 health_score >= 70,
                 f"MOS: {mos}, Latency: {latency}ms, Score: {health_score}")
        elif mos > 0:
            test("MOS data present, health score calculated", health_score > 0)

    except Exception as e:
        test("Health score validation completed", False, str(e))


def test_adapter_data():
    """Test adapter data structure and content."""
    print("\n=== Adapter Data Tests ===")
    try:
        r = requests.get(f"{BASE_URL}/api/status", timeout=10)
        data = r.json()
        adapters = data.get("adapters", [])

        test("At least one adapter present", len(adapters) >= 1, f"Found: {len(adapters)}")

        if adapters:
            adapter = adapters[0]
            test("Adapter has adapterID", "adapterID" in adapter)
            test("Adapter has name", "name" in adapter)
            test("Adapter has type", "type" in adapter)
            test("Adapter has state", "state" in adapter)
            test("Adapter has dataUsage", "dataUsage" in adapter)

            if "dataUsage" in adapter:
                usage = adapter["dataUsage"]
                test("dataUsage has daily", "daily" in usage)
                test("dataUsage has monthly", "monthly" in usage)

    except Exception as e:
        test("Adapter data tests completed", False, str(e))


def test_connection_details():
    """Test connection detail data structure."""
    print("\n=== Connection Details Tests ===")
    try:
        r = requests.get(f"{BASE_URL}/api/status", timeout=10)
        data = r.json()
        connections = data.get("connections", [])

        if connections:
            test("Connections array has data", len(connections) >= 1)
            conn = connections[0]
            test("Connection has adapterID", "adapterID" in conn)
            test("Connection has protocol", "protocol" in conn)
            test("Connection has latency", "latency" in conn)
            test("Connection has status", "status" in conn)
            test("Connection status is valid",
                 conn.get("status") in ["good", "warn", "bad"])
        else:
            test("No active connections (may be expected)", True)

    except Exception as e:
        test("Connection details tests completed", False, str(e))


def test_concurrent_requests():
    """Test handling of concurrent requests."""
    print("\n=== Concurrent Request Tests ===")
    import concurrent.futures

    try:
        def make_request(url):
            return requests.get(url, timeout=10)

        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            # Make 5 concurrent requests to each endpoint
            futures = []
            for _ in range(5):
                futures.append(executor.submit(make_request, f"{BASE_URL}/api/status"))
                futures.append(executor.submit(make_request, f"{BASE_URL}/api/server"))

            responses = [f.result() for f in futures]

        status_ok = all(r.status_code == 200 for r in responses)
        test("All concurrent requests succeeded", status_ok,
             f"Status codes: {[r.status_code for r in responses]}")

    except Exception as e:
        test("Concurrent request test completed", False, str(e))


def print_summary():
    """Print test summary."""
    passed = sum(1 for _, condition, _ in results if condition)
    total = len(results)
    failed = total - passed

    print("\n" + "=" * 50)
    print(f"TEST SUMMARY: {passed}/{total} passed")
    if failed > 0:
        print(f"\n{FAIL} Failed tests:")
        for name, condition, details in results:
            if not condition:
                print(f"  - {name}")
                if details:
                    print(f"    {details}")
    print("=" * 50)

    return failed == 0


def main():
    """Run all E2E tests."""
    print("=" * 50)
    print("Speedify Dashboard E2E Tests")
    print("=" * 50)
    print(f"Target: {BASE_URL}")

    # Check if server is running
    try:
        requests.get(f"{BASE_URL}/", timeout=5)
    except requests.exceptions.ConnectionError:
        print(f"\n{FAIL} Cannot connect to server at {BASE_URL}")
        print("Make sure the Flask app is running: python3 app.py")
        sys.exit(1)

    # Run all tests
    test_main_page()
    test_status_api()
    test_server_api()
    test_change_mode_api()
    test_caching()
    test_health_score_calculation()
    test_adapter_data()
    test_connection_details()
    test_concurrent_requests()

    # Print summary
    success = print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
