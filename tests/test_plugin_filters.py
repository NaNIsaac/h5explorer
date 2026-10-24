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
    run = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True, check=False
    )

    assert run.returncode == 0, run.stderr
    assert run.stdout.strip() == "False"


def test_cli_reads_plugin_compressed_data(compressed_file):
    for command in (["explore"], ["datasets"], ["explore", "--summary"]):
        result = CliRunner().invoke(cli, [*command, str(compressed_file)])
        assert result.exit_code == 0, result.output


def test_filter_table_matches_hdf5plugin():
    import hdf5plugin

    from h5explorer.core import PLUGIN_FILTERS

    assert PLUGIN_FILTERS == {code: name for name, code in hdf5plugin.FILTERS.items()}


def test_compression_column_names_plugin_filters(compressed_file):
    import pandas as pd

    from h5explorer.core import H5Explorer

    df = (
        H5Explorer(compressed_file).get_datasets_info().set_index("path")["compression"]
    )

    assert df["entry/data/gzip"] == "gzip"
    assert df["entry/data/bslz4"] == "bshuf"
    assert pd.isna(df["entry/instrument/energy"])  # stored as missing, as before


def test_unknown_filter_id_is_shown_by_number(tmp_path):
    import h5py
    import numpy as np
    from h5py import h5d, h5p, h5s, h5t, h5z

    from h5explorer.core import H5Explorer

    path = tmp_path / "odd_filter.h5"
    with h5py.File(path, "w") as f:
        dcpl = h5p.create(h5p.DATASET_CREATE)
        dcpl.set_chunk((4,))
        dcpl.set_filter(
            40000, h5z.FLAG_OPTIONAL, (1,)
        )  # optional, so HDF5 writes without it
        dset = h5py.Dataset(
            h5d.create(
                f.id, b"odd", h5t.NATIVE_INT32, h5s.create_simple((8,)), dcpl=dcpl
            )
        )
        dset[...] = np.arange(8)

    assert H5Explorer(path).get_datasets_info()["compression"].tolist() == [
        "filter 40000"
    ]


def test_datasets_table_shows_plugin_filter_name(compressed_file):
    result = CliRunner().invoke(cli, ["datasets", str(compressed_file)])

    assert result.exit_code == 0, result.output
    assert "bshuf" in result.output
    assert "unknown" not in result.output
