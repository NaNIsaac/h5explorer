"""Explore the structure of HDF5 files and extract their metadata as pandas DataFrames."""

from pathlib import Path
import json
from typing import Any
import h5py
import pandas as pd
import numpy as np
from rich.console import Console
from rich.tree import Tree
from rich.table import Table
from rich.panel import Panel
from rich import box


def _excel_cell(value: Any) -> Any:
    """Excel cells cannot hold a tuple, list, dict or ndarray, so convert them to str."""
    if isinstance(value, tuple | list | dict | np.ndarray):
        return str(value)
    return value


# Plugin filter id to name: hdf5plugin.FILTERS of hdf5plugin 7.1, inverted (tests check they agree).
PLUGIN_FILTERS = {
    307: "bzip2",
    32001: "blosc",
    32004: "lz4",
    32008: "bshuf",
    32013: "zfp",
    32015: "zstd",
    32017: "sz",
    32018: "fcidecomp",
    32024: "sz3",
    32026: "blosc2",
    32028: "sperr",
    32033: "htj2k",
}


def compression_name(dataset: h5py.Dataset) -> str | None:
    """Compression filter name: h5py's own name for gzip, lzf and szip, the PLUGIN_FILTERS name for plugin filters.

    h5py reports every plugin filter as "unknown", so the ids are read from the filter pipeline.
    An id missing from the table gives "filter <id>", several filters are joined with "+".
    None when the dataset is not compressed.
    """
    if dataset.compression != "unknown":
        return dataset.compression
    plist = dataset.id.get_create_plist()
    codes = [plist.get_filter(i)[0] for i in range(plist.get_nfilters())]
    # Ids below 256 are HDF5 built-in filters (deflate, shuffle, fletcher32, ...).
    return "+".join(PLUGIN_FILTERS.get(c, f"filter {c}") for c in codes if c >= 256) or "unknown"


class H5Explorer:
    """Explore an HDF5 file and extract its metadata."""

    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)
        self.console = Console()
        self._structure_df = None
        self._datasets_df = None
        self._groups_df = None
        self._attributes_df = None

        if not self.filepath.exists():
            raise FileNotFoundError(f"HDF5 파일을 찾을 수 없습니다: {filepath}")

    def scan_structure(self) -> pd.DataFrame:
        """One row per object (root, groups, datasets); cached."""
        if self._structure_df is not None:
            return self._structure_df

        structure_data = []

        def visitor(name, obj):
            path_parts = name.split("/")
            depth = len(path_parts) - 1 if name else 0
            parent = "/".join(path_parts[:-1]) if depth > 0 else ""

            if isinstance(obj, h5py.Group):
                obj_type = "Group"
                shape = None
                dtype = None
                size_bytes = 0
                compression = None
            elif isinstance(obj, h5py.Dataset):
                obj_type = "Dataset"
                shape = obj.shape
                dtype = str(obj.dtype)
                size_bytes = obj.nbytes
                compression = compression_name(obj)
            else:
                return

            attr_count = len(obj.attrs)

            structure_data.append(
                {
                    "path": name,
                    "name": path_parts[-1] if path_parts[-1] else "root",
                    "type": obj_type,
                    "parent": parent,
                    "depth": depth,
                    "shape": shape,
                    "dtype": dtype,
                    "size_bytes": size_bytes,
                    "size_mb": size_bytes / (1024 * 1024) if size_bytes > 0 else 0,
                    "compression": compression,
                    "attr_count": attr_count,
                }
            )

        with h5py.File(self.filepath, "r") as f:
            # visititems does not visit the root group.
            visitor("", f)
            f.visititems(visitor)

        self._structure_df = pd.DataFrame(structure_data)
        return self._structure_df

    def get_datasets_info(self) -> pd.DataFrame:
        if self._datasets_df is not None:
            return self._datasets_df

        structure_df = self.scan_structure()
        self._datasets_df = structure_df[structure_df["type"] == "Dataset"].copy()

        self._datasets_df["elements"] = self._datasets_df["shape"].apply(
            lambda x: np.prod(x) if x is not None else 0
        )
        self._datasets_df["dimensions"] = self._datasets_df["shape"].apply(
            lambda x: len(x) if x is not None else 0
        )

        return self._datasets_df

    def get_groups_info(self) -> pd.DataFrame:
        if self._groups_df is not None:
            return self._groups_df

        structure_df = self.scan_structure()
        groups_df = structure_df[structure_df["type"] == "Group"].copy()

        group_children = []
        for _, group in groups_df.iterrows():
            group_path = group["path"]
            children = structure_df[structure_df["parent"] == group_path]
            child_datasets = len(children[children["type"] == "Dataset"])
            child_groups = len(children[children["type"] == "Group"])

            group_children.append(
                {
                    "path": group_path,
                    "child_datasets": child_datasets,
                    "child_groups": child_groups,
                    "total_children": child_datasets + child_groups,
                }
            )

        children_df = pd.DataFrame(group_children)
        self._groups_df = groups_df.merge(children_df, on="path", how="left")

        return self._groups_df

    def get_attributes_info(self) -> pd.DataFrame:
        if self._attributes_df is not None:
            return self._attributes_df

        attributes_data = []

        def extract_attrs(name, obj):
            for attr_name, attr_value in obj.attrs.items():
                if isinstance(attr_value, np.ndarray):
                    attr_type = f"array({attr_value.dtype})"
                    attr_shape = attr_value.shape
                    attr_size = attr_value.nbytes
                    if attr_value.size <= 10:
                        attr_repr = str(attr_value.tolist())
                    else:
                        attr_repr = f"array{attr_shape}"
                else:
                    attr_type = type(attr_value).__name__
                    attr_shape = None
                    attr_size = len(str(attr_value))
                    attr_repr = str(attr_value)

                attributes_data.append(
                    {
                        "object_path": name,
                        "attr_name": attr_name,
                        "attr_type": attr_type,
                        "attr_shape": attr_shape,
                        "attr_size": attr_size,
                        "attr_value": (
                            attr_repr[:100] + "..."
                            if len(attr_repr) > 100
                            else attr_repr
                        ),
                    }
                )

        with h5py.File(self.filepath, "r") as f:
            extract_attrs("", f)
            f.visititems(extract_attrs)

        self._attributes_df = pd.DataFrame(attributes_data)
        return self._attributes_df

    def get_file_summary(self) -> dict[str, Any]:
        structure_df = self.scan_structure()
        datasets_df = self.get_datasets_info()
        groups_df = self.get_groups_info()
        attributes_df = self.get_attributes_info()

        file_size = self.filepath.stat().st_size

        return {
            "file_path": str(self.filepath),
            "file_size_bytes": file_size,
            "file_size_mb": file_size / (1024 * 1024),
            "total_groups": len(groups_df),
            "total_datasets": len(datasets_df),
            "total_attributes": len(attributes_df),
            "max_depth": structure_df["depth"].max(),
            "total_data_size_mb": datasets_df["size_mb"].sum(),
            "compression_used": datasets_df["compression"].notna().sum(),
            "datatypes_used": datasets_df["dtype"].nunique(),
            "largest_dataset": (
                datasets_df.loc[datasets_df["size_mb"].idxmax(), "path"]
                if len(datasets_df) > 0
                else None
            ),
            "largest_dataset_size_mb": (
                datasets_df["size_mb"].max() if len(datasets_df) > 0 else 0
            ),
        }

    def show_tree(self, max_depth: int | None = None, show_attrs: bool = True):
        structure_df = self.scan_structure()

        if max_depth is not None:
            structure_df = structure_df[structure_df["depth"] <= max_depth]

        tree = Tree(self.filepath.name, style="bold blue")
        path_to_node = {"": tree}

        # Sort by depth so a parent node exists before its children.
        for _, row in structure_df.sort_values("depth").iterrows():
            if row["path"] == "":  # the root is already the tree
                continue

            parent_node = path_to_node.get(row["parent"], tree)

            if row["type"] == "Dataset":
                shape_str = (
                    f"({', '.join(map(str, row['shape']))})" if row["shape"] else ""
                )
                size_str = f" [{row['size_mb']:.2f}MB]" if row["size_mb"] > 0.01 else ""
                node_text = f"{row['name']} {shape_str}{size_str}".rstrip()
                style = "green"
            else:
                node_text = f"{row['name']}/"
                style = "blue"

            if show_attrs and row["attr_count"] > 0:
                node_text += f" ({row['attr_count']} attrs)"

            new_node = parent_node.add(node_text, style=style)
            path_to_node[row["path"]] = new_node

        self.console.print(tree)

    def show_summary(self):
        summary = self.get_file_summary()

        main_info = f"""
File: {summary['file_path']}
Size: {summary['file_size_mb']:.2f} MB
Data Size: {summary['total_data_size_mb']:.2f} MB
Max Depth: {summary['max_depth']}
        """

        stats_table = Table(title="Structure Statistics", box=box.ROUNDED)
        stats_table.add_column("Type", style="cyan")
        stats_table.add_column("Count", justify="right", style="magenta")

        stats_table.add_row("Groups", str(summary["total_groups"]))
        stats_table.add_row("Datasets", str(summary["total_datasets"]))
        stats_table.add_row("Attributes", str(summary["total_attributes"]))
        stats_table.add_row("Compressed Datasets", str(summary["compression_used"]))
        stats_table.add_row("Data Types", str(summary["datatypes_used"]))

        self.console.print(
            Panel(main_info.strip(), title="File Information", border_style="blue")
        )
        self.console.print(stats_table)

        if summary["largest_dataset"]:
            largest_info = f"Largest Dataset: {summary['largest_dataset']} ({summary['largest_dataset_size_mb']:.2f} MB)"
            self.console.print(
                Panel(largest_info, title="Largest Dataset", border_style="yellow")
            )

    def show_datasets_table(self, top_n: int | None = None, sort_by: str = "size"):
        """Print a table of datasets; sort_by is size, name or elements."""
        datasets_df = self.get_datasets_info()

        if sort_by == "name":
            datasets_df = datasets_df.sort_values("path")
        else:
            column = {"size": "size_mb", "elements": "elements"}[sort_by]
            datasets_df = datasets_df.sort_values(column, ascending=False)
        if top_n:
            datasets_df = datasets_df.head(top_n)

        table = Table(title="Datasets Information", box=box.ROUNDED)
        table.add_column("Path", style="cyan")
        table.add_column("Shape", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Size (MB)", justify="right", style="magenta")
        table.add_column("Compression", style="blue")
        table.add_column("Attrs", justify="right", style="white")

        for _, row in datasets_df.iterrows():
            shape_str = str(row["shape"]) if row["shape"] else "N/A"
            size_str = f"{row['size_mb']:.3f}"
            compression_str = str(row["compression"]) if pd.notna(row["compression"]) else "None"

            table.add_row(
                row["path"],
                shape_str,
                row["dtype"],
                size_str,
                compression_str,
                str(row["attr_count"]),
            )

        self.console.print(table)

    def export_to_excel(self, output_path: str | Path):
        """Write summary, datasets, groups and attributes to one Excel sheet each."""
        sheets = {
            "Summary": pd.DataFrame(
                self.get_file_summary().items(), columns=["key", "value"]
            ),
            "Datasets": self.get_datasets_info(),
            "Groups": self.get_groups_info(),
            "Attributes": self.get_attributes_info(),
        }
        with pd.ExcelWriter(output_path) as writer:
            for name, df in sheets.items():
                df.map(_excel_cell).to_excel(writer, sheet_name=name, index=False)

    def export_structure_json(self, output_path: str):
        data = {
            "summary": self.get_file_summary(),
            "structure": self.scan_structure().to_dict("records"),
            "datasets": self.get_datasets_info().to_dict("records"),
            "groups": self.get_groups_info().to_dict("records"),
            "attributes": self.get_attributes_info().to_dict("records"),
        }

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)

        self.console.print(f"JSON 파일로 내보내기 완료: {output_path}")

    def dump_lines(self) -> list[str]:
        """Plain-text lines that are easy to grep: groups as "name/", datasets as "name  shape dtype", attributes as "    @key = value"

        The root group ("/") and its attributes come first (visititems does not visit the root).
        """
        lines = []

        def show(name, obj):
            match obj:
                case h5py.Dataset():
                    lines.append(f"{name}  {obj.shape} {obj.dtype}")
                case _:
                    lines.append(f"{name}/")
            lines.extend(f"    @{key} = {value}" for key, value in obj.attrs.items())

        with h5py.File(self.filepath, "r") as f:
            show("", f)
            f.visititems(show)
        return lines


if __name__ == "__main__":
    explorer = H5Explorer(r"X:\XRR_AI\hdf5_XRR\xrr_data.h5")

    explorer.show_summary()

    explorer.show_tree(max_depth=3)

    explorer.show_datasets_table(top_n=10)

    datasets_df = explorer.get_datasets_info()
    attributes_df = explorer.get_attributes_info()

    explorer.export_structure_json("hdf5_structure.json")
