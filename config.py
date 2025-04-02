"""
Configuration module for FlakyTestX.

This module loads configuration settings from environment variables
and provides default values when environment variables are not set.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# Test execution settings
TEST_ITERATIONS = int(os.getenv("TEST_ITERATIONS", 5))
PARALLEL_EXECUTIONS = int(os.getenv("PARALLEL_EXECUTIONS", 1))
FLAKY_THRESHOLD = float(os.getenv("FLAKY_THRESHOLD", 0.2))  # 20% flakiness threshold

# AI settings
AI_ENABLED = os.getenv("AI_ENABLED", "true").lower() == "true"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
MOCK_AI_RESPONSES = os.getenv("MOCK_AI_RESPONSES", "false").lower() == "true" or not OPENAI_API_KEY

# Reporting settings
GENERATE_HTML_REPORT = os.getenv("GENERATE_HTML_REPORT", "true").lower() == "true"
VERBOSE_OUTPUT = os.getenv("VERBOSE_OUTPUT", "true").lower() == "true"

# Dashboard settings
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8501))
DASHBOARD_HOST = os.getenv("DASHBOARD_HOST", "localhost")

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = BASE_DIR / "logs" / "flakytestx.log"
Path(LOG_FILE).parent.mkdir(exist_ok=True)

# System settings
TEMP_DIR = BASE_DIR / "temp"
TEMP_DIR.mkdir(exist_ok=True)