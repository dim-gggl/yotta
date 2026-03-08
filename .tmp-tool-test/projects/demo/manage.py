#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

from yotta.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("YOTTA_SETTINGS_MODULE", "settings")
    execute_from_command_line(sys.argv)
