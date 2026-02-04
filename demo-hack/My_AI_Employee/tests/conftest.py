"""
Pytest configuration file for Silver Tier tests.

Configures pytest settings, fixtures, and test discovery.
"""

import sys
from pathlib import Path

# Add My_AI_Employee to Python path
# Path(__file__).parent.parent goes from tests/conftest.py -> tests/ -> My_AI_Employee/
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as an end-to-end test"
    )
