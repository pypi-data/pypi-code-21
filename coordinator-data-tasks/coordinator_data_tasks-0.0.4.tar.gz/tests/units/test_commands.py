#!/usr/bin/env python
"""Provide unit tests for modules/functions in the commands pkg."""
from hashlib import md5
from pathlib import Path
import shutil

import pytest

from coordinator_data_tasks import commands


@pytest.fixture()
def tmp_out_dir(tmpdir):
    """Create tempdir to store output files."""
    tmpdir = Path(str(tmpdir))
    yield tmpdir

    # Clean up after ourselves
    shutil.rmtree(str(tmpdir))


def test_left_join_overall(tmp_out_dir):
    """Ensure test files produce expected results file."""
    left_path = Path("tests/files/commands/left_join/left1.xls")
    right_path = Path("tests/files/commands/left_join/right1.xls")
    join_on = ["join1", "join2"]
    out = tmp_out_dir / "joined.xls"
    indicator = True

    joined_std = Path("tests/files/commands/left_join/joined.xls")
    joined_std_sum = md5(joined_std.open('rb').read()).hexdigest()

    commands.left_join.main(
        left_path=left_path,
        right_path=right_path,
        join_on=join_on,
        out=out,
        indicator=indicator)

    joined_test_sum = md5(out.open('rb').read()).hexdigest()

    assert joined_test_sum == joined_std_sum
