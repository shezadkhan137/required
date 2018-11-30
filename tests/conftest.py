import sys
import pytest

py3 = sys.version_info[0] >= 3


class DummyCollector(pytest.collect.File):
    def collect(self):
        return []


def pytest_pycollect_makemodule(path, parent):
    base_name = path.basename
    if "py3" in base_name and not py3 or ("py2" in base_name and py3):
        return DummyCollector(path, parent=parent)
