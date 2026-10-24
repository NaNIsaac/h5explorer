import h5py
import numpy as np
import pytest
from click.testing import CliRunner

from h5explorer.cli import cli


@pytest.fixture
def sample(tmp_path):
    path = tmp_path / "sample.h5"
    with h5py.File(path, "w") as f:
        # size and element count disagree: b_big has the most bytes (80 kB, 10,000 float64),
        # c_many the most elements (20,000 uint8, 20 kB)
        f.create_dataset("b_big", data=np.zeros((100, 100)))
        f.create_dataset("a_small", data=np.zeros(10))
        f.create_dataset("c_many", data=np.zeros(20000, dtype=np.uint8))
    return path


def listed(output, names=("a_small", "b_big", "c_many")):
    return sorted((n for n in names if n in output), key=output.index)


@pytest.mark.parametrize(
    ("sort_by", "order"),
    [
        ("size", ["b_big", "c_many", "a_small"]),
        ("name", ["a_small", "b_big", "c_many"]),
        ("elements", ["c_many", "b_big", "a_small"]),
    ],
)
def test_sort_by(sample, sort_by, order):
    result = CliRunner().invoke(cli, ["datasets", str(sample), "--sort-by", sort_by])
    assert result.exit_code == 0, result.output
    assert listed(result.output) == order


# the scan lists datasets alphabetically, so without the fix --sort-by name only shows its bug
# through --top, which was ignored
def test_top_applies_after_sorting(sample):
    result = CliRunner().invoke(
        cli, ["datasets", str(sample), "--sort-by", "name", "--top", "1"]
    )
    assert result.exit_code == 0, result.output
    assert listed(result.output) == ["a_small"]
