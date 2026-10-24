# h5explorer

English · [한국어](README.ko.md)

Explore the structure and metadata of HDF5 files from Python or the command line.

It reads an HDF5 file with h5py and gives you the groups, datasets and attributes as pandas DataFrames,
prints them as a tree and tables with Rich, and exports them to Excel or JSON.
Only metadata is read, so files compressed with HDF5 filter plugins (bitshuffle, LZ4, Blosc, as in
PAL-XFEL and Eiger data) open without `hdf5plugin`.

## Install

Python 3.10 or later, [uv](https://docs.astral.sh/uv/). The package is not on PyPI; install it from a clone:

```sh
git clone https://github.com/NaNIsaac/h5explorer.git
cd h5explorer
```

Create a sample file and run the commands on it:

<!-- test unix -->
```sh
uv venv --python 3.13
uv pip install .
.venv/bin/python -c "import h5py; f = h5py.File('sample.h5', 'w'); f.create_group('raw').create_dataset('temperature', data=[[1.0, 2.0, 3.0]]); f.close()"
.venv/bin/h5tree sample.h5
.venv/bin/h5explore export sample.h5 --output sample.xlsx
```

<!-- test windows -->
```powershell
uv venv --python 3.13
uv pip install .
.venv\Scripts\python -c "import h5py; f = h5py.File('sample.h5', 'w'); f.create_group('raw').create_dataset('temperature', data=[[1.0, 2.0, 3.0]]); f.close()"
.venv\Scripts\h5tree sample.h5
.venv\Scripts\h5explore export sample.h5 --output sample.xlsx
```

## Command line

`h5explore` is a command group; `h5tree` is the same as `h5explore explore` and `h5info` is the same as `h5explore datasets`.

```sh
h5explore explore data.h5                 # tree of groups and datasets
h5explore explore data.h5 --summary       # summary only
h5explore explore data.h5 --max-depth 2   # limit the depth
h5explore explore data.h5 --no-attrs      # hide attributes
h5explore datasets data.h5 --top 20       # table of the largest datasets
h5explore dump data.h5                    # every group, dataset and attribute as plain lines, root included
h5explore export data.h5 --output analysis.xlsx                  # Excel (default)
h5explore export data.h5 --format json --output structure.json   # JSON
h5explore batch ./files --output-dir ./reports --recursive       # report for every HDF5 file in a folder
h5explore compare a.h5 b.h5 c.h5          # compare files
h5explore find ./files --recursive        # list the HDF5 files in a folder
```

## Python

```python
from h5explorer.core import H5Explorer

explorer = H5Explorer("data.h5")

explorer.show_summary()
explorer.show_tree(max_depth=3)
explorer.show_datasets_table(top_n=10)

datasets = explorer.get_datasets_info()        # pandas DataFrames
groups = explorer.get_groups_info()
attributes = explorer.get_attributes_info()
summary = explorer.get_file_summary()          # dict

explorer.export_to_excel("analysis.xlsx")      # sheets: Summary, Datasets, Groups, Attributes
explorer.export_structure_json("structure.json")
```

`H5Batch`, `find_large_datasets`, `analyze_compression_efficiency` and `get_dataset_paths` are in `h5explorer.cli`.

## Layout

```
h5explorer/
  core.py     H5Explorer: scan, DataFrames, Rich output, export
  cli.py      Click commands, H5Batch and helper functions
tests/        pytest
pyproject.toml
```

## Tests

<!-- test -->
```sh
uv run --group dev pytest
```
