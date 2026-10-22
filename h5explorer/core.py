"""
H5Explorer - HDF5 파일 구조 탐색 및 메타데이터 추출 도구
pandas DataFrame 기반으로 구조화된 정보 제공
"""

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
    """Excel 셀에 쓸 수 없는 tuple, list, dict, ndarray는 문자열로 바꿈"""
    if isinstance(value, tuple | list | dict | np.ndarray):
        return str(value)
    return value


class H5Explorer:
    """HDF5 파일 탐색 및 메타데이터 추출 클래스"""

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
        """HDF5 파일 전체 구조를 DataFrame으로 반환"""
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
                compression = obj.compression
            else:
                return

            # 속성 개수
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
            # 루트 그룹 추가
            visitor("", f)
            f.visititems(visitor)

        self._structure_df = pd.DataFrame(structure_data)
        return self._structure_df

    def get_datasets_info(self) -> pd.DataFrame:
        """데이터셋 정보만 추출"""
        if self._datasets_df is not None:
            return self._datasets_df

        structure_df = self.scan_structure()
        self._datasets_df = structure_df[structure_df["type"] == "Dataset"].copy()

        # 추가 정보 계산
        self._datasets_df["elements"] = self._datasets_df["shape"].apply(
            lambda x: np.prod(x) if x is not None else 0
        )
        self._datasets_df["dimensions"] = self._datasets_df["shape"].apply(
            lambda x: len(x) if x is not None else 0
        )

        return self._datasets_df

    def get_groups_info(self) -> pd.DataFrame:
        """그룹 정보만 추출"""
        if self._groups_df is not None:
            return self._groups_df

        structure_df = self.scan_structure()
        groups_df = structure_df[structure_df["type"] == "Group"].copy()

        # 각 그룹별 하위 아이템 개수 계산
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
        """모든 속성 정보를 DataFrame으로 추출"""
        if self._attributes_df is not None:
            return self._attributes_df

        attributes_data = []

        def extract_attrs(name, obj):
            for attr_name, attr_value in obj.attrs.items():
                # 속성 값 타입과 크기 정보
                if isinstance(attr_value, np.ndarray):
                    attr_type = f"array({attr_value.dtype})"
                    attr_shape = attr_value.shape
                    attr_size = attr_value.nbytes
                    # 배열이 작으면 값 표시, 크면 요약
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
        """파일 전체 요약 정보"""
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
        """Rich를 사용한 트리 구조 출력"""
        structure_df = self.scan_structure()

        if max_depth is not None:
            structure_df = structure_df[structure_df["depth"] <= max_depth]

        # 루트 트리 생성
        tree = Tree(self.filepath.name, style="bold blue")
        path_to_node = {"": tree}

        # 깊이 순으로 정렬
        for _, row in structure_df.sort_values("depth").iterrows():
            if row["path"] == "":  # 루트는 이미 추가됨
                continue

            parent_node = path_to_node.get(row["parent"], tree)

            # 노드 텍스트 구성
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

            # 속성 정보 추가
            if show_attrs and row["attr_count"] > 0:
                node_text += f" ({row['attr_count']} attrs)"

            new_node = parent_node.add(node_text, style=style)
            path_to_node[row["path"]] = new_node

        self.console.print(tree)

    def show_summary(self):
        """파일 요약 정보 출력"""
        summary = self.get_file_summary()

        # 메인 정보 패널
        main_info = f"""
File: {summary['file_path']}
Size: {summary['file_size_mb']:.2f} MB
Data Size: {summary['total_data_size_mb']:.2f} MB
Max Depth: {summary['max_depth']}
        """

        # 통계 테이블
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

        # 가장 큰 데이터셋 정보
        if summary["largest_dataset"]:
            largest_info = f"Largest Dataset: {summary['largest_dataset']} ({summary['largest_dataset_size_mb']:.2f} MB)"
            self.console.print(
                Panel(largest_info, title="Largest Dataset", border_style="yellow")
            )

    def show_datasets_table(self, top_n: int | None = None, sort_by: str = "size"):
        """데이터셋 정보를 테이블로 출력 (sort_by: size, name, elements)"""
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
        """요약, 데이터셋, 그룹, 속성 정보를 시트별로 Excel에 저장"""
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
        """구조 정보를 JSON으로 내보내기"""
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


# 사용 예시
if __name__ == "__main__":
    # 예시 사용법
    explorer = H5Explorer(r"X:\XRR_AI\hdf5_XRR\xrr_data.h5")

    # 요약 정보 출력
    explorer.show_summary()

    # 트리 구조 출력
    explorer.show_tree(max_depth=3)

    # 데이터셋 테이블 출력 (큰 것부터 10개)
    explorer.show_datasets_table(top_n=10)

    # pandas DataFrame으로 데이터 가져오기
    datasets_df = explorer.get_datasets_info()
    attributes_df = explorer.get_attributes_info()

    # 내보내기
    explorer.export_structure_json("hdf5_structure.json")
