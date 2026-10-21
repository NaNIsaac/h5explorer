from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="h5explorer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="HDF5 파일 구조 탐색 및 메타데이터 추출 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/h5explorer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "h5py>=3.6.0",
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "rich>=12.0.0",
        "click>=8.0.0",
        "openpyxl>=3.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
            "mypy",
        ],
        "docs": [
            "sphinx",
            "sphinx-rtd-theme",
        ],
    },
    entry_points={
        "console_scripts": [
            "h5explore=h5explorer.cli:cli",
            "h5tree=h5explorer.cli:explore",
            "h5info=h5explorer.cli:datasets",
        ],
    },
    keywords="hdf5, data-analysis, scientific-computing, data-exploration",
)
