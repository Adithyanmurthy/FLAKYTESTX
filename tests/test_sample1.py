"""
Sample test module 1 for FlakyTestX.

This module contains tests that demonstrate different behaviors,
including a flaky test with a race condition in an asynchronous call.
"""

import pytest
import time
import random
import asyncio
from unittest import mock


class TestSample1:
    """Sample test class demonstrating stable and flaky tests."""

    def test_addition(self):
        """A stable test that always passes."""
        assert 1 + 1 == 2
        assert 2 + 2 == 4

    def test_subtraction(self):
        """Another stable test that always passes."""
        assert 5 - 3 == 2
        assert 10 - 5 == 5

    @pytest.mark.parametrize("input_val,expected", [(1, 1), (2, 4), (3, 9), (4, 16)])
    def test_square_function(self, input_val, expected):
        """A parametrized test that always passes."""
        def square(x):
            return x * x
        
        assert square(input_val) == expected

    @pytest.mark.flaky
    def test_async_api_call(self):
        """
        A flaky test with a race condition in an asynchronous call.
        
        This test is intentionally flaky and will randomly fail about 60% of the time
        due to a simulated race condition in the async API call.
        """
        # Simulate an asynchronous API call with race condition
        async def mock_api_call():
            # Simulate variable network latency
            await asyncio.sleep(random.uniform(0.01, 0.1))
            
            # Simulate race condition - random failures
            if random.random() < 0.6:  # 60% chance of failure
                raise Exception("API timeout: The operation took too long to complete")
            
            return {"status": "success", "data": [1, 2, 3]}

        # Run the async function and check result
        async def run_test():
            try:
                # No proper timeout handling - will cause flaky behavior
                result = await mock_api_call()
                assert result["status"] == "success"
                assert len(result["data"]) > 0
            except Exception as e:
                pytest.fail(f"API call failed: {str(e)}")

        # Execute async test
        asyncio.run(run_test())

    def test_mock_database(self):
        """A stable test with mocking."""
        # Mock a database connection
        mock_db = mock.MagicMock()
        mock_db.query.return_value = [{"id": 1, "name": "Test Item"}]
        
        # Test code that would use the database
        def get_item_by_id(db, item_id):
            result = db.query(f"SELECT * FROM items WHERE id = {item_id}")
            return result[0] if result else None
        
        # Run test with mock
        item = get_item_by_id(mock_db, 1)
        assert item["id"] == 1
        assert item["name"] == "Test Item"