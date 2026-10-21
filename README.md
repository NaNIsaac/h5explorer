# README.md 내용
readme_content = '''# H5Explorer 🔍

HDF5 파일의 구조를 쉽게 탐색하고 메타데이터를 추출하는 Python 도구입니다.

## ✨ 주요 기능

- 🌳 **아름다운 트리 구조 출력**: Rich 라이브러리를 사용한 컬러풀한 시각화
- 📊 **pandas DataFrame**: 구조화된 메타데이터를 DataFrame으로 제공
- 📈 **상세한 통계**: 파일 크기, 압축률, 데이터 타입 분석
- 📁 **배치 처리**: 여러 파일을 한번에 분석
- 💾 **다양한 내보내기**: Excel, JSON 형식 지원
- 🖥️ **CLI 도구**: 터미널에서 바로 사용 가능

## 🚀 설치

```bash
pip install h5explorer
```

## 📖 사용법

### Python API

```python
from h5explorer import H5Explorer

# 탐색기 생성
explorer = H5Explorer("data.h5")

# 요약 정보 출력
explorer.show_summary()

# 트리 구조 출력
explorer.show_tree(max_depth=3)

# 데이터셋 테이블 출력
explorer.show_datasets_table(top_n=10)

# pandas DataFrame으로 데이터 가져오기
datasets_df = explorer.get_datasets_info()
groups_df = explorer.get_groups_info()
attributes_df = explorer.get_attributes_info()

# Excel로 내보내기
explorer.export_to_excel("analysis.xlsx")
```

### CLI 사용

```bash
# 기본 탐색
h5explore data.h5

# 요약 정보만
h5explore data.h5 --summary

# 최대 깊이 제한
h5explore data.h5 --max-depth 2

# 데이터셋 정보 테이블
h5info data.h5 --top 20

# Excel로 내보내기
h5explore export data.h5 --output analysis.xlsx

# 여러 파일 배치 처리
h5explore batch /path/to/hdf5/files --output-dir ./reports

# 파일 비교
h5explore compare file1.h5 file2.h5 file3.h5
```

## 📊 출력 예시

### 트리 구조
```
📁 experiment_data.h5
├── 📁 metadata/
│   ├── 📊 experiment_info (1×10) [0.01MB] 🏷️ 3 attrs
│   └── 📊 timestamps (1000×1) [0.08MB]
├── 📁 raw_data/
│   ├── 📁 sensor_group1/
│   │   ├── 📊 temperature (1000×5) [0.38MB]
│   │   └── 📊 pressure (1000×3) [0.23MB]
│   └── 📁 sensor_group2/
│       └── 📊 measurements (500×10) [0.38MB]
└── 📁 processed/
    ├── 📊 results (100×20) [0.15MB]
    └── 🏷️ processing_params (5 attrs)
```

### 요약 정보
```
📁 File: experiment_data.h5
💾 Size: 2.45 MB
📊 Data Size: 2.31 MB
🔍 Max Depth: 3

┌─────────────┬───────┐
│ Type        │ Count │
├─────────────┼───────┤
│ Groups      │     5 │
│ Datasets    │     6 │
│ Attributes  │    15 │
│ Compressed  │     2 │
│ Data Types  │     3 │
└─────────────┴───────┘
```

## 🔧 고급 사용법

### 배치 처리
```python
from h5explorer import H5Batch

# 여러 파일 분석
files = ["data1.h5", "data2.h5", "data3.h5"]
batch = H5Batch(files)

# 전체 요약
summary_df = batch.scan_all()

# 파일 간 비교
comparison_df = batch.compare_files()

# 리포트 생성
batch.export_batch_report("./batch_reports")
```

### 유틸리티 함수들
```python
from h5explorer.utils import (
    find_large_datasets,
    analyze_compression_efficiency,
    get_dataset_paths
)

# 큰 데이터셋 찾기
large_datasets = find_large_datasets("data.h5", min_size_mb=10)

# 압축 효율성 분석
compression_stats = analyze_compression_efficiency("data.h5")

# 특정 패턴의 데이터셋 경로
sensor_paths = get_dataset_paths("data.h5", filter_by="sensor")
```

## 📦 패키지 구조

```
h5explorer/
├── __init__.py
├── core/
│   ├── explorer.py      # 메인 탐색 클래스
│   ├── scanner.py       # 파일 스캔 기능
│   └── structure.py     # 구조 분석
├── display/
│   ├── tree.py          # 트리 시각화
│   ├── table.py         # 테이블 출력
│   └── export.py        # 내보내기 기능
├── utils/
│   ├── batch.py         # 배치 처리
│   ├── compare.py       # 파일 비교
│   └── helpers.py       # 유틸리티 함수
└── cli/
    └── main.py          # CLI 인터페이스
```

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 라이선스

MIT License - 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 🙏 감사의 말

- [h5py](https://www.h5py.org/) - HDF5 파일 처리
- [Rich](https://rich.readthedocs.io/) - 아름다운 터미널 출력
- [pandas](https://pandas.pydata.org/) - 데이터 분석
- [Click](https://click.palletsprojects.com/) - CLI 인터페이스
'''

# 사용 예시 스크립트들
example_basic = '''
"""
H5Explorer 기본 사용 예시
"""

from h5explorer import H5Explorer
import numpy as np
import h5py

# 예시 HDF5 파일 생성
def create_sample_file():
    with h5py.File('sample_data.h5', 'w') as f:
        # 메타데이터 그룹
        metadata = f.create_group('metadata')
        metadata.create_dataset('experiment_info', data=np.arange(10))
        metadata.attrs['experiment_date'] = '2024-01-15'
        metadata.attrs['researcher'] = 'Dr. Smith'
        
        # 원시 데이터 그룹
        raw_data = f.create_group('raw_data')
        
        # 센서 데이터
        sensor1 = raw_data.create_group('sensor1')
        sensor1.create_dataset('temperature', 
                             data=np.random.normal(25, 5, (1000, 3)),
                             compression='gzip')
        sensor1.create_dataset('humidity', 
                             data=np.random.normal(60, 10, (1000, 2)))
        
        # 처리된 데이터
        processed = f.create_group('processed')
        processed.create_dataset('daily_averages', 
                                data=np.random.random((30, 5)))
        processed.attrs['processing_date'] = '2024-01-16'
        processed.attrs['method'] = 'rolling_mean'

def main():
    # 샘플 파일 생성
    create_sample_file()
    print("✅ 샘플 파일 생성 완료: sample_data.h5")
    
    # H5Explorer로 분석
    explorer = H5Explorer('sample_data.h5')
    
    print("\n" + "="*50)
    print("📊 파일 요약 정보")
    print("="*50)
    explorer.show_summary()
    
    print("\n" + "="*50)
    print("🌳 파일 구조")
    print("="*50)
    explorer.show_tree()
    
    print("\n" + "="*50)
    print("📈 데이터셋 정보")
    print("="*50)
    explorer.show_datasets_table()
    
    # pandas DataFrame으로 데이터 추출
    print("\n" + "="*50)
    print("🐼 pandas DataFrame 활용")
    print("="*50)
    
    datasets_df = explorer.get_datasets_info()
    print("📊 데이터셋 개수:", len(datasets_df))
    print("💾 총 데이터 크기:", f"{datasets_df['size_mb'].sum():.2f} MB")
    print("🗜️ 압축된 데이터셋:", datasets_df['compression'].notna().sum())
    
    # 가장 큰 데이터셋
    largest = datasets_df.loc[datasets_df['size_mb'].idxmax()]
    print(f"📈 가장 큰 데이터셋: {largest['path']} ({largest['size_mb']:.2f} MB)")
    
    # 속성 정보
    attributes_df = explorer.get_attributes_info()
    print(f"🏷️ 총 속성 개수: {len(attributes_df)}")
    
    # Excel로 내보내기
    explorer.export_to_excel('sample_analysis.xlsx')
    print("\n✅ 분석 결과를 sample_analysis.xlsx로 내보냄")
    
    # JSON으로 내보내기
    explorer.export_structure_json('sample_structure.json')
    print("✅ 구조 정보를 sample_structure.json으로 내보냄")

if __name__ == "__main__":
    main()
'''

example_advanced = '''
"""
H5Explorer 고급 사용 예시 - 배치 처리 및 비교
"""

from h5explorer import H5Explorer, H5Batch
from h5explorer.utils import find_large_datasets, analyze_compression_efficiency
import numpy as np
import h5py
import os

def create_multiple_sample_files():
    """여러 개의 샘플 HDF5 파일 생성"""
    
    # 실험 데이터 1 - 온도 센서
    with h5py.File('experiment1_temperature.h5', 'w') as f:
        f.attrs['experiment_type'] = 'temperature_monitoring'
        f.attrs['duration_days'] = 30
        
        sensors = f.create_group('sensors')
        for i in range(5):
            sensor_data = np.random.normal(25, 3, (720, 4))  # 30일 * 24시간
            sensors.create_dataset(f'sensor_{i:02d}', 
                                 data=sensor_data,
                                 compression='gzip',
                                 compression_opts=9)
        
        metadata = f.create_group('metadata')
        metadata.create_dataset('timestamps', 
                               data=np.arange(720, dtype='datetime64[h]'))
        metadata.create_dataset('locations', 
                               data=[f'Room_{i}'.encode() for i in range(5)])
    
    # 실험 데이터 2 - 압력 센서
    with h5py.File('experiment2_pressure.h5', 'w') as f:
        f.attrs['experiment_type'] = 'pressure_monitoring'
        f.attrs['duration_days'] = 30
        
        sensors = f.create_group('sensors')
        for i in range(3):
            sensor_data = np.random.normal(1013, 50, (720, 2))
            sensors.create_dataset(f'pressure_sensor_{i:02d}', 
                                 data=sensor_data,
                                 compression='lzf')
        
        # 더 큰 처리된 데이터
        processed = f.create_group('processed')
        processed.create_dataset('hourly_analysis', 
                                data=np.random.random((720, 20)))
        processed.create_dataset('daily_summary', 
                                data=np.random.random((30, 50)))
    
    # 실험 데이터 3 - 복합 센서 (압축 없음)
    with h5py.File('experiment3_mixed.h5', 'w') as f:
        f.attrs['experiment_type'] = 'mixed_sensors'
        f.attrs['duration_days'] = 7  # 짧은 기간
        
        temp_group = f.create_group('temperature')
        temp_group.create_dataset('data', data=np.random.normal(22, 2, (168, 10)))
        
        humidity_group = f.create_group('humidity')
        humidity_group.create_dataset('data', data=np.random.normal(55, 5, (168, 10)))
        
        # 큰 이미지 데이터 (압축 없음)
        images = f.create_group('images')
        for i in range(10):
            img_data = np.random.randint(0, 255, (512, 512, 3), dtype=np.uint8)
            images.create_dataset(f'image_{i:03d}', data=img_data)

def analyze_single_files():
    """개별 파일 분석"""
    files = ['experiment1_temperature.h5', 'experiment2_pressure.h5', 'experiment3_mixed.h5']
    
    for filepath in files:
        print(f"\n{'='*60}")
        print(f"📁 분석 중: {filepath}")
        print(f"{'='*60}")
        
        explorer = H5Explorer(filepath)
        
        # 요약 정보
        summary = explorer.get_file_summary()
        print(f"📊 총 데이터셋: {summary['total_datasets']}")
        print(f"💾 파일 크기: {summary['file_size_mb']:.2f} MB")
        print(f"🗜️ 압축된 데이터셋: {summary['compression_used']}")
        
        # 큰 데이터셋 찾기
        large_datasets = find_large_datasets(filepath, min_size_mb=1.0)
        if len(large_datasets) > 0:
            print(f"📈 1MB 이상 데이터셋 ({len(large_datasets)}개):")
            for _, dataset in large_datasets.head(3).iterrows():
                print(f"  • {dataset['path']}: {dataset['size_mb']:.2f} MB")
        
        # 압축 효율성 분석
        compression_stats = analyze_compression_efficiency(filepath)
        comp_ratio = compression_stats.iloc[0]['compression_ratio']
        print(f"🗜️ 압축률: {comp_ratio:.1f}%")

def batch_analysis():
    """배치 분석"""
    print(f"\n{'='*60}")
    print("🔄 배치 분석 시작")
    print(f"{'='*60}")
    
    files = ['experiment1_temperature.h5', 'experiment2_pressure.h5', 'experiment3_mixed.h5']
    batch = H5Batch(files)
    
    # 전체 요약
    summary_df = batch.scan_all()
    print("\n📊 전체 파일 요약:")
    print(summary_df[['filename', 'total_datasets', 'file_size_mb', 
                     'total_data_size_mb', 'compression_used']].to_string(index=False))
    
    # 파일 비교
    comparison_df = batch.compare_files()
    
    # 데이터 타입 분포
    print("\n📈 데이터 타입 분포:")
    dtype_counts = comparison_df['dtype'].value_counts()
    for dtype, count in dtype_counts.head(5).items():
        print(f"  • {dtype}: {count}개")
    
    # 압축 방식 분포
    print("\n🗜️ 압축 방식 분포:")
    compression_counts = comparison_df['compression'].value_counts(dropna=False)
    for comp, count in compression_counts.items():
        comp_name = 'None' if pd.isna(comp) else comp
        print(f"  • {comp_name}: {count}개")
    
    # 파일별 가장 큰 데이터셋
    print("\n📈 파일별 최대 데이터셋:")
    for file in files:
        file_data = comparison_df[comparison_df['file'] == file]
        if len(file_data) > 0:
            largest = file_data.loc[file_data['size_mb'].idxmax()]
            print(f"  • {file}: {largest['dataset_path']} ({largest['size_mb']:.2f} MB)")
    
    # 배치 리포트 생성
    batch.export_batch_report('./batch_reports')
    print("\n✅ 배치 리포트가 ./batch_reports 디렉토리에 생성되었습니다")

def cleanup_files():
    """생성된 파일들 정리"""
    files_to_remove = [
        'experiment1_temperature.h5',
        'experiment2_pressure.h5', 
        'experiment3_mixed.h5',
        'sample_analysis.xlsx',
        'sample_structure.json'
    ]
    
    for file in files_to_remove:
        if os.path.exists(file):
            os.remove(file)
            print(f"🗑️ {file} 삭제됨")

def main():
    print("🚀 H5Explorer 고급 사용 예시")
    print("="*60)
    
    try:
        # 1. 샘플 파일들 생성
        print("1️⃣ 샘플 파일들 생성 중...")
        create_multiple_sample_files()
        print("✅ 샘플 파일 생성 완료")
        
        # 2. 개별 파일 분석
        print("\n2️⃣ 개별 파일 분석")
        analyze_single_files()
        
        # 3. 배치 분석
        print("\n3️⃣ 배치 분석")
        batch_analysis()
        
        print(f"\n{'='*60}")
        print("✅ 모든 분석 완료!")
        print("📁 생성된 리포트:")
        print("  • ./batch_reports/ (배치 분석 결과)")
        print("🔍 CLI 명령어 예시:")
        print("  h5explore experiment1_temperature.h5 --summary")
        print("  h5explore compare experiment*.h5")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
    
    finally:
        # 정리 여부 물어보기
        cleanup = input("\n🗑️ 생성된 파일들을 삭제하시겠습니까? (y/N): ")
        if cleanup.lower() == 'y':
            cleanup_files()
            print("✅ 정리 완료")

if __name__ == "__main__":
    main()
'''