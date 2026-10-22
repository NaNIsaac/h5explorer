import os
import subprocess
import sys

import h5py
import numpy as np
import pytest
from click.testing import CliRunner

from h5explorer.cli import cli


def _write(path, **datasets):
    path.parent.mkdir(parents=True, exist_ok=True)
    with h5py.File(path, "w") as f:
        for name, data in datasets.items():
            f.create_dataset(name, data=data)
    return path


def test_batch_creates_nested_output_dir(tmp_path):
    _write(tmp_path / "in" / "a.h5", x=np.zeros(3))
    out = tmp_path / "reports" / "deeper"

    result = CliRunner().invoke(cli, ["batch", str(tmp_path / "in"), "-o", str(out)])

    assert result.exit_code == 0, result.output
    assert (out / "a_detail.xlsx").exists()


def test_batch_keeps_reports_of_files_sharing_a_stem(tmp_path):
    _write(tmp_path / "in" / "d1" / "x.h5", only_first=np.zeros(3))
    _write(tmp_path / "in" / "d2" / "x.h5", only_second=np.zeros(3))
    out = tmp_path / "reports"

    result = CliRunner().invoke(cli, ["batch", str(tmp_path / "in"), "-o", str(out), "-r"])

    assert result.exit_code == 0, result.output
    assert sorted(p.name for p in out.glob("*_structure.json")) == ["x_2_structure.json", "x_structure.json"]
    text = "".join(p.read_text(encoding="utf-8") for p in out.glob("*_structure.json"))
    assert "only_first" in text and "only_second" in text


def test_datasets_table_shows_none_for_missing_compression(tmp_path):
    path = _write(tmp_path / "a.h5", x=np.zeros(3))

    result = CliRunner().invoke(cli, ["datasets", str(path)])

    assert result.exit_code == 0, result.output
    assert "nan" not in result.output.lower()
    assert "None" in result.output


@pytest.mark.parametrize("command", [["explore"], ["explore", "--summary"], ["datasets"]])
def test_output_encodes_in_cp949(tmp_path, command):
    # A Korean Windows console or a redirect uses cp949, which cannot encode emoji.
    path = _write(tmp_path / "a.h5", x=np.zeros(3))
    env = {**os.environ, "PYTHONIOENCODING": "cp949"}

    run = subprocess.run(
        [sys.executable, "-m", "h5explorer.cli", command[0], str(path), *command[1:]],
        capture_output=True,
        env=env,
    )

    assert run.returncode == 0, run.stderr.decode("cp949", "replace")
