import h5py
import numpy as np
import pandas as pd

from h5explorer.core import H5Explorer


def test_export_to_excel(tmp_path):
    path = tmp_path / "sample.h5"
    with h5py.File(path, "w") as f:
        group = f.create_group("raw")
        group.attrs["method"] = "rolling_mean"
        group.create_dataset("temperature", data=np.zeros((10, 3)), compression="gzip")
        f.create_dataset("scalar", data=1.0)

    out = tmp_path / "out.xlsx"
    H5Explorer(path).export_to_excel(out)

    sheets = pd.read_excel(out, sheet_name=None)
    assert set(sheets) == {"Summary", "Datasets", "Groups", "Attributes"}
    assert set(sheets["Datasets"]["path"]) == {"raw/temperature", "scalar"}
