# h5explorer

Explore the structure of an HDF5 file: print its group tree, list datasets by size, collect
datasets, groups and attributes into pandas DataFrames, and export the structure to JSON.
Works from Python or from the command line.

## Install

```bash
pip install git+https://github.com/NaNIsaac/h5explorer
```

This installs the `h5explore` command and the `h5explorer` package. It needs h5py, pandas, numpy,
rich, click and openpyxl.

## Command line

```bash
h5explore explore data.h5                 # group and dataset tree
h5explore explore data.h5 --summary       # file summary only
h5explore explore data.h5 --max-depth 2   # limit the tree depth
h5explore datasets data.h5 --top 20       # largest datasets as a table
h5explore export data.h5 -o data.json --format json
h5explore compare a.h5 b.h5               # datasets side by side
h5explore find ./runs -r                  # list HDF5 files
```

`h5tree` and `h5info` are shortcuts for `h5explore explore` and `h5explore datasets`.

## Python

```python
from h5explorer.core import H5Explorer

explorer = H5Explorer("data.h5")
explorer.show_summary()
explorer.show_tree(max_depth=3)

datasets = explorer.get_datasets_info()      # one row per dataset: path, shape, dtype, size_mb, ...
attributes = explorer.get_attributes_info()
explorer.export_structure_json("structure.json")
```

`H5Batch` in `h5explorer.cli` scans and compares several files; `find_large_datasets` and
`analyze_compression_efficiency` in the same module work on a single file.
