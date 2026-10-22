import h5py
import hdf5plugin
import numpy as np
import pytest


@pytest.fixture
def compressed_file(tmp_path):
    """A file like a PAL-XFEL or Eiger run: a bitshuffle+LZ4 dataset next to gzip and plain ones,
    with attributes on the root, a group and a dataset."""
    path = tmp_path / "compressed.h5"
    frames = np.arange(4096, dtype=np.uint16).reshape(64, 64)
    with h5py.File(path, "w") as f:
        f.attrs["facility"] = "test"
        data = f.create_group("entry/data")
        data.attrs["NX_class"] = "NXdata"
        data.create_dataset("gzip", data=frames, compression="gzip")
        data.create_dataset("bslz4", data=frames, **hdf5plugin.Bitshuffle(cname="lz4"))
        energy = f.create_dataset("entry/instrument/energy", data=np.float64(5.55))
        energy.attrs["units"] = "keV"
    return path
