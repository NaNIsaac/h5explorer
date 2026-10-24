import os
import subprocess
import sys

from click.testing import CliRunner

from h5explorer.cli import cli

# metadata_loader's main.py prints these lines for the same file, without the first two (it
# never visits the root group, so the file's own attributes are missing there).
EXPECTED = [
    "/",
    "    @facility = test",
    "entry/",
    "entry/data/",
    "    @NX_class = NXdata",
    "entry/data/bslz4  (64, 64) uint16",
    "entry/data/gzip  (64, 64) uint16",
    "entry/instrument/",
    "entry/instrument/energy  () float64",
    "    @units = keV",
]


def test_dump_lists_everything_with_root_attributes(compressed_file):
    result = CliRunner().invoke(cli, ["dump", str(compressed_file)])

    assert result.exit_code == 0, result.output
    assert result.output.splitlines() == EXPECTED


def test_dump_encodes_in_cp949(compressed_file):
    env = {**os.environ, "PYTHONIOENCODING": "cp949"}

    run = subprocess.run(
        [sys.executable, "-m", "h5explorer.cli", "dump", str(compressed_file)],
        capture_output=True,
        env=env,
        check=False,
    )

    assert run.returncode == 0, run.stderr.decode("cp949", "replace")
    assert run.stdout.decode("cp949").splitlines() == EXPECTED


def test_dump_reports_a_missing_file(tmp_path):
    result = CliRunner().invoke(cli, ["dump", str(tmp_path / "none.h5")])

    assert result.exit_code != 0
