"""
Sample test module 2 for FlakyTestX.

This module contains tests that demonstrate different types of flaky behavior,
including file operations and database connections.
"""

import pytest
import time
import random
import os
import tempfile
import threading
from unittest import mock


# Global counter to simulate shared resource issues
_counter = 0
_counter_lock = threading.Lock()


class TestSample2:
    """Sample test class demonstrating flaky tests with common patterns."""

    def setup_method(self):
        """Set up test fixtures, if any."""
        # Create a temporary directory for file operations
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a test file
        self.test_file_path = os.path.join(self.temp_dir.name, "test.txt")
        with open(self.test_file_path, "w") as f:
            f.write("Test data")

    def teardown_method(self):
        """Tear down test fixtures, if any."""
        # Cleanup temporary directory
        try:
            self.temp_dir.cleanup()
        except:
            pass  # Intentionally ignore cleanup errors to demonstrate issues

    def test_multiplication(self):
        """A stable test that always passes."""
        assert 2 * 3 == 6
        assert 5 * 5 == 25

    @pytest.mark.flaky
    def test_file_operations(self):
        """
        A flaky test with file operations.
        
        This test is intentionally flaky due to file handling issues.
        Sometimes it will fail due to file locks or timing issues.
        """
        # Create a new file with random content
        file_path = os.path.join(self.temp_dir.name, f"test_file_{random.randint(1000, 9999)}.txt")
        
        try:
            # Write to file
            with open(file_path, "w") as f:
                f.write(f"Test content {random.randint(1, 100)}")
            
            # Simulate a race condition with file operations
            # Sometimes we don't wait long enough for file operations to complete
            if random.random() < 0.3:  # 30% chance of timing issue
                time.sleep(0.01)  # Too short delay
            else:
                time.sleep(0.1)  # Adequate delay
            
            # Read from file
            with open(file_path, "r") as f:
                content = f.read()
            
            assert "Test content" in content
            
            # Attempt to remove the file, but occasionally fail
            if random.random() < 0.2:  # 20% chance of failure
                # Simulate another process keeping the file open
                dummy_handle = open(file_path, "r")
                os.remove(file_path)  # This might fail with "file in use" error
                dummy_handle.close()
            else:
                os.remove(file_path)
                
        except Exception as e:
            pytest.fail(f"File operation failed: {str(e)}")

    @pytest.mark.flaky
    def test_database_query(self):
        """
        A flaky test with database connection issues.
        
        This test simulates database connection problems that make the test flaky.
        The test will randomly fail when the "database connection" is unstable.
        """
        # Mock a database with connection issues
        mock_db = mock.MagicMock()
        
        # Simulate connection issues with 40% probability
        if random.random() < 0.4:
            mock_db.connect.side_effect = Exception("Database connection timeout")
            with pytest.raises(Exception) as excinfo:
                mock_db.connect()
            assert "connection timeout" in str(excinfo.value).lower()
        else:
            # Connection succeeds
            mock_db.connect.return_value = True
            mock_db.query.return_value = [{"id": 1, "name": "Test User"}]
            
            # Test database operations
            assert mock_db.connect() is True
            result = mock_db.query("SELECT * FROM users WHERE id = 1")
            assert len(result) == 1
            assert result[0]["name"] == "Test User"

    def test_counter_increment(self):
        """
        A test with shared resource access.
        
        This test is stable because it properly uses a lock when accessing
        shared resources, unlike the flaky version below.
        """
        global _counter, _counter_lock
        
        # Safely increment counter with lock
        with _counter_lock:
            initial_value = _counter
            _counter += 1
            final_value = _counter
            
        assert final_value == initial_value + 1

    @pytest.mark.flaky
    def test_flaky_counter_increment(self):
        """
        A flaky test with shared resource access issues.
        
        This test intentionally has a race condition when accessing a shared counter.
        """
        global _counter
        
        # Get initial counter value without lock
        initial_value = _counter
        
        # Simulate work that takes time
        time.sleep(random.uniform(0.01, 0.05))
        
        # Increment without lock - possible race condition
        _counter += 1
        
        # More simulated work
        time.sleep(random.uniform(0.01, 0.05))
        
        # Verify counter was incremented by 1 - can fail if another test changed it
        try:
            assert _counter == initial_value + 1
        except AssertionError:
            # Sometimes we'll get lucky and pass even with the race condition
            if random.random() < 0.7:  # 70% chance to actually fail when race condition exists
                raise