"""Compression summary should handle valid empty or group-only HDF5 files."""
import h5py

from h5explorer.cli import analyze_compression_efficiency


def test_compression_analysis_for_empty_hdf5(tmp_path):
    path = tmp_path / "empty.h5"
    with h5py.File(path, "w"):
        pass
    summary = analyze_compression_efficiency(str(path))
    row = summary.iloc[0]
    assert row["total_datasets"] == 0
    assert row["compressed_datasets"] == 0
    assert row["compression_ratio"] == 0
    assert row["total_size_mb"] == 0


def test_compression_analysis_for_group_only_hdf5(tmp_path):
    path = tmp_path / "groups_only.h5"
    with h5py.File(path, "w") as file:
        file.create_group("detector/nested")
    summary = analyze_compression_efficiency(str(path))
    assert summary.iloc[0]["total_datasets"] == 0
    assert summary.iloc[0]["compression_ratio"] == 0


def test_compression_analysis_for_mixed_datasets(tmp_path):
    path = tmp_path / "mixed.h5"
    with h5py.File(path, "w") as file:
        file.create_dataset("raw", data=[1, 2, 3])
        file.create_dataset("compressed", data=[1, 2, 3], compression="gzip")
    summary = analyze_compression_efficiency(str(path))
    assert summary.iloc[0]["total_datasets"] == 2
    assert summary.iloc[0]["compressed_datasets"] == 1
    assert summary.iloc[0]["compression_ratio"] == 50.0
