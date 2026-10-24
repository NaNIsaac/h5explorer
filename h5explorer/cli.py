"""
H5Explorer CLI 인터페이스 및 추가 유틸리티 함수들
"""
from typing import List
from pathlib import Path
import sys

import click
import pandas as pd

from h5explorer.core import H5Explorer


class H5Batch:
    """여러 HDF5 파일을 배치로 처리하는 클래스"""

    def __init__(self, file_paths: List[str]):
        self.file_paths = [Path(p) for p in file_paths]
        self.explorers = {}

    def scan_all(self) -> pd.DataFrame:
        """모든 파일의 요약 정보를 DataFrame으로 반환"""
        batch_data = []

        for filepath in self.file_paths:
            try:
                explorer = H5Explorer(filepath)
                summary = explorer.get_file_summary()
                summary["filename"] = filepath.name
                batch_data.append(summary)
                self.explorers[str(filepath)] = explorer

            except Exception as e:
                print(f"{filepath} 처리 중 오류: {e}")
                continue

        return pd.DataFrame(batch_data)

    def compare_files(self) -> pd.DataFrame:
        """파일들의 구조를 비교"""
        comparison_data = []

        for filepath in self.file_paths:
            if str(filepath) in self.explorers:
                explorer = self.explorers[str(filepath)]
                datasets_df = explorer.get_datasets_info()

                for _, dataset in datasets_df.iterrows():
                    comparison_data.append(
                        {
                            "file": filepath.name,
                            "dataset_path": dataset["path"],
                            "shape": dataset["shape"],
                            "dtype": dataset["dtype"],
                            "size_mb": dataset["size_mb"],
                            "compression": dataset["compression"],
                        }
                    )

        return pd.DataFrame(comparison_data)

    def export_batch_report(self, output_dir: str | Path):
        """배치 처리 결과를 디렉토리에 저장"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # 전체 요약
        summary_df = self.scan_all()
        summary_df.to_excel(output_dir / "batch_summary.xlsx", index=False)

        # 파일별 상세 정보. 폴더가 달라도 stem이 같으면 번호를 붙여 덮어쓰지 않는다.
        used: dict[str, int] = {}
        for filepath, explorer in self.explorers.items():
            stem = Path(filepath).stem
            used[stem] = used.get(stem, 0) + 1
            filename = stem if used[stem] == 1 else f"{stem}_{used[stem]}"
            try:
                explorer.export_to_excel(output_dir / f"{filename}_detail.xlsx")
                explorer.export_structure_json(
                    output_dir / f"{filename}_structure.json"
                )
            except Exception as e:
                print(f"{filename} 내보내기 중 오류: {e}")

        # 비교 리포트
        comparison_df = self.compare_files()
        comparison_df.to_excel(output_dir / "files_comparison.xlsx", index=False)

        print(f"배치 리포트 생성 완료: {output_dir}")


def find_hdf5_files(directory: str, recursive: bool = True) -> List[str]:
    """디렉토리에서 HDF5 파일들을 찾기"""
    directory = Path(directory)

    if recursive:
        pattern = "**/*.h5"
        hdf5_files = list(directory.glob(pattern))
        hdf5_files.extend(list(directory.glob("**/*.hdf5")))
    else:
        hdf5_files = list(directory.glob("*.h5"))
        hdf5_files.extend(list(directory.glob("*.hdf5")))

    return [str(f) for f in hdf5_files]


# CLI 명령어 정의
@click.group()
@click.version_option()
def cli():
    """H5Explorer - HDF5 파일 구조 탐색 도구"""
    pass


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--max-depth", "-d", type=int, help="최대 표시 깊이")
@click.option("--no-attrs", is_flag=True, help="속성 정보 숨기기")
@click.option("--summary", "-s", is_flag=True, help="요약 정보만 표시")
def explore(filepath, max_depth, no_attrs, summary):
    """HDF5 파일 구조 탐색"""
    try:
        explorer = H5Explorer(filepath)

        if summary:
            explorer.show_summary()
        else:
            explorer.show_tree(max_depth=max_depth, show_attrs=not no_attrs)

    except Exception as e:
        click.echo(f"오류: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--top", "-t", type=int, default=20, help="표시할 상위 데이터셋 개수")
@click.option(
    "--sort-by",
    type=click.Choice(["size", "name", "elements"]),
    default="size",
    help="정렬 기준",
)
def datasets(filepath, top, sort_by):
    """데이터셋 정보 테이블 출력"""
    try:
        explorer = H5Explorer(filepath)
        explorer.show_datasets_table(top_n=top, sort_by=sort_by)

    except Exception as e:
        click.echo(f"오류: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
def dump(filepath):
    """모든 그룹·데이터셋과 속성을 한 줄씩 평문으로 출력 (루트 속성 포함)"""
    try:
        for line in H5Explorer(filepath).dump_lines():
            click.echo(line)

    except Exception as e:
        click.echo(f"오류: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--output", "-o", required=True, help="출력 파일 경로")
@click.option(
    "--format",
    "output_format",
    type=click.Choice(["excel", "json"]),
    default="excel",
    help="출력 형식",
)
def export(filepath, output, output_format):
    """구조 정보를 파일로 내보내기"""
    try:
        explorer = H5Explorer(filepath)

        if output_format == "excel":
            explorer.export_to_excel(output)
        elif output_format == "json":
            explorer.export_structure_json(output)

    except Exception as e:
        click.echo(f"오류: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--output-dir", "-o", required=True, help="출력 디렉토리")
@click.option("--recursive", "-r", is_flag=True, help="하위 디렉토리 포함")
def batch(directory, output_dir, recursive):
    """디렉토리의 모든 HDF5 파일을 배치 처리"""
    try:
        hdf5_files = find_hdf5_files(directory, recursive)

        if not hdf5_files:
            click.echo("HDF5 파일을 찾을 수 없습니다.")
            return

        click.echo(f"{len(hdf5_files)}개의 HDF5 파일을 발견했습니다.")

        batch_processor = H5Batch(hdf5_files)
        batch_processor.export_batch_report(output_dir)

    except Exception as e:
        click.echo(f"오류: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("filepaths", nargs=-1, required=True, type=click.Path(exists=True))
def compare(filepaths):
    """여러 HDF5 파일 구조 비교"""
    try:
        batch_processor = H5Batch(filepaths)

        # 요약 비교
        summary_df = batch_processor.scan_all()

        click.echo("\n파일 요약 비교:")
        click.echo(
            summary_df[
                [
                    "filename",
                    "total_groups",
                    "total_datasets",
                    "file_size_mb",
                    "total_data_size_mb",
                ]
            ].to_string(index=False)
        )

        # 구조 비교
        comparison_df = batch_processor.compare_files()

        # 공통 데이터셋 찾기
        common_paths = comparison_df.groupby("dataset_path").size()
        common_paths = common_paths[common_paths == len(filepaths)]

        if len(common_paths) > 0:
            click.echo(f"\n공통 데이터셋 ({len(common_paths)}개):")
            for path in common_paths.index[:10]:  # 상위 10개만 표시
                click.echo(f"  • {path}")
        else:
            click.echo("\n공통 데이터셋이 없습니다.")

    except Exception as e:
        click.echo(f"오류: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument("directory", type=click.Path(exists=True, file_okay=False))
@click.option("--recursive", "-r", is_flag=True, help="하위 디렉토리 포함")
def find(directory, recursive):
    """디렉토리에서 HDF5 파일 찾기"""
    hdf5_files = find_hdf5_files(directory, recursive)

    if hdf5_files:
        click.echo(f"{len(hdf5_files)}개의 HDF5 파일을 발견했습니다:")
        for file in sorted(hdf5_files):
            file_path = Path(file)
            file_size = file_path.stat().st_size / (1024 * 1024)  # MB
            click.echo(f"  {file} ({file_size:.2f} MB)")
    else:
        click.echo("HDF5 파일을 찾을 수 없습니다.")


if __name__ == "__main__":
    cli()


# 추가 유틸리티 함수들
def quick_summary(filepath: str) -> dict:
    """빠른 요약 정보 반환 (CLI에서 사용)"""
    explorer = H5Explorer(filepath)
    return explorer.get_file_summary()


def get_dataset_paths(filepath: str, filter_by: str = None) -> List[str]:
    """데이터셋 경로 리스트 반환"""
    explorer = H5Explorer(filepath)
    datasets_df = explorer.get_datasets_info()

    if filter_by:
        # 간단한 필터링 (경로에 특정 문자열 포함)
        datasets_df = datasets_df[
            datasets_df["path"].str.contains(filter_by, case=False)
        ]

    return datasets_df["path"].tolist()


def find_large_datasets(filepath: str, min_size_mb: float = 10.0) -> pd.DataFrame:
    """큰 데이터셋 찾기"""
    explorer = H5Explorer(filepath)
    datasets_df = explorer.get_datasets_info()
    return datasets_df[datasets_df["size_mb"] >= min_size_mb].sort_values(
        "size_mb", ascending=False
    )


def analyze_compression_efficiency(filepath: str) -> pd.DataFrame:
    """압축 효율성 분석"""
    explorer = H5Explorer(filepath)
    datasets_df = explorer.get_datasets_info()

    # 압축된 것과 안 된 것 비교
    compressed = datasets_df[datasets_df["compression"].notna()]
    uncompressed = datasets_df[datasets_df["compression"].isna()]

    analysis = {
        "total_datasets": len(datasets_df),
        "compressed_datasets": len(compressed),
        "compression_ratio": len(compressed) / len(datasets_df) * 100,
        "compressed_size_mb": compressed["size_mb"].sum(),
        "uncompressed_size_mb": uncompressed["size_mb"].sum(),
        "total_size_mb": datasets_df["size_mb"].sum(),
    }

    return pd.DataFrame([analysis])
