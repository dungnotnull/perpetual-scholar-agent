"""Baseline benchmark fixture — default techniques the agent tries to beat."""
import pytest


def baseline_sort_large_list():
    """Naive sorted() as baseline."""
    import random
    data = [random.randint(0, 1_000_000) for _ in range(100_000)]
    return sorted(data)


def baseline_dict_lookup():
    """Direct dict key lookup as baseline."""
    d = {str(i): i for i in range(100_000)}
    return d.get("50000")


def baseline_file_read():
    """Read a small file as baseline."""
    import tempfile
    import os
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("x" * 10_000)
        name = f.name
    with open(name) as f:
        data = f.read()
    os.unlink(name)
    return data
