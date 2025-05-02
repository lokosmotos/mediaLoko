#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "cat_hr.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

import sys
from pathlib import Path

# Add this line BEFORE django imports
sys.path.append(str(Path(__file__).resolve().parent))  # ← Forces Python to recognize root
