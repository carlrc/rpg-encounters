#!/usr/bin/env python3
"""Root-level test configuration"""
import os

from dotenv import load_dotenv

# Load environment variables for all tests
load_dotenv()
# Host-run tests must use localhost not docker DNS
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
