import subprocess
import sys

from click.testing import CliRunner

from h5explorer.cli import cli


def test_metadata_of_plugin_compressed_data_needs_no_hdf5plugin(compressed_file):
    # A fresh interpreter, so the hdf5plugin import of the fixture does not count.
    code = (
        "import sys\n"
        "from h5explorer.core import H5Explorer\n"
        f"x = H5Explorer({str(compressed_file)!r})\n"
        "x.scan_structure(); x.get_datasets_info(); x.get_attributes_info(); x.get_file_summary()\n"
        "print('hdf5plugin' in sys.modules)\n"
    )
    run = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)

    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == "False"


def test_cli_reads_plugin_compressed_data(compressed_file):
    for command in (["explore"], ["datasets"], ["explore", "--summary"]):
        result = CliRunner().invoke(cli, [*command, str(compressed_file)])
        assert result.exit_code == 0, result.output
