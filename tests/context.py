import os
import sys

# https://docs.python-guide.org/writing/structure/
# print(__file__)
# print(os.path.dirname(__file__))
# print(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import pystock