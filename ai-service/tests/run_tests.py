import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

import pytest

if __name__ == "__main__":
    ret = pytest.main(["-v", "tests/"])
    sys.exit(ret)
