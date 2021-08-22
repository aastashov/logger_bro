#!/usr/bin/env python3
import os
import sys

from tracker.management import execute_from_command_line

if __name__ == '__main__':
    current_path = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(os.path.join(current_path, "tracker"))

    execute_from_command_line()
