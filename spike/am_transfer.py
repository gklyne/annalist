"""
Transfer module for running annalist-manager

This appears to be needed becausde the annalist-manager directory is not installed 
on the python path.
"""

import sys
import os

annroot = os.path.dirname(os.path.abspath(__file__))    # annalist_root
sys.path.insert(0, annroot)

import annalist_manager

annalist_manager.am_main.runMain()
