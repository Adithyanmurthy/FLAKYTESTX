# FlakyTestX

## AI-Powered Flaky Test Detection and Resolution

![FlakyTestX Logo](https://via.placeholder.com/150x150?text=FlakyTestX)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A submission for the Kyiv QA Automation Summit 2025

## 🔍 Problem

Flaky tests are a persistent headache in test automation, wasting developer time and eroding confidence in test suites. These tests unpredictably pass and fail without actual code changes, making them difficult to identify and fix.

## 💡 Solution

FlakyTestX automatically detects flaky tests by running test suites multiple times and using AI to analyze patterns in failed test executions. It provides:

- **Detection**: Identifies which tests are flaky and assigns a flakiness score
- **Analysis**: Uses AI to understand why tests are flaky
- **Recommendations**: Generates targeted suggestions to fix each flaky test
- **Visualization**: Presents results in an intuitive dashboard

## 🚀 Features

- 🔄 Automated test runner that executes tests multiple times
- 📊 Statistical analysis of test reliability
- 🤖 AI-powered root cause analysis
- 🛠️ Concrete fix suggestions for each flaky test
- 📈 Interactive dashboard to visualize flakiness patterns
- 📝 Comprehensive reporting capabilities

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/flakytestx.git
cd flakytestx

# Create and activate a virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file in the project root with the following variables:

```
OPENAI_API_KEY=your_openai_api_key_here  # Optional, will use mock responses if not provided
TEST_ITERATIONS=5                         # Number of times to run each test
AI_ENABLED=true                           # Set to false to disable AI features
```

## 📋 Usage

### Command Line Interface

```bash
# Run the entire pipeline (detection + analysis + suggestions)
python run_all.py --path path/to/tests

# Run just the flaky test detection
python flaky_detector.py --path path/to/tests --iterations 5

# Generate AI insights for previously detected flaky tests
python ai_insight_generator.py --results path/to/results.json
```

### Dashboard

```bash
# Launch the Streamlit dashboard
python -m streamlit run dashboard.py
```

## 📊 Sample Output

```
================================
FlakyTestX Analysis Results
================================

📋 Test Suite Summary:
- Total tests: 12
- Flaky tests detected: 3
- Overall suite stability: 75%

🔍 Flaky Test Details:
1. test_async_api_call (test_sample1.py) - Flakiness: 60%
   └─ AI Insight: Race condition in asynchronous API call
   └─ Suggestion: Add proper awaiting with timeout and implement retry mechanism

2. test_database_query (test_sample2.py) - Flakiness: 40%
   └─ AI Insight: Database connection not properly closed between test runs
   └─ Suggestion: Use connection pooling and ensure proper teardown in fixture

3. test_file_operations (test_sample2.py) - Flakiness: 30%
   └─ AI Insight: File locks causing intermittent failures
   └─ Suggestion: Implement retry pattern with exponential backoff
```

## 🔧 Architecture

FlakyTestX consists of several modular components:

1. **Flaky Detector**: Executes test suites multiple times to identify flaky tests
2. **AI Insight Generator**: Analyzes test failures using AI to determine root causes
3. **Dashboard**: Visualizes results and provides an interface for exploring solutions
4. **Utilities**: Shared logging and helper functions

## 📚 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🧑‍💻 Authors

- Your Name - [Your GitHub Profile](https://github.com/yourusername)

---

Developed with ❤️ for the Kyiv QA Automation Summit 2025
