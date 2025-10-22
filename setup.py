#!/usr/bin/env python3
"""
Praven Pro setup script
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="praven-pro",
    version="2.1.0",
    author="George Redpath",
    author_email="ghredpath@hotmail.com",
    description="Automated biological validation for BirdNET acoustic monitoring",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ziforge/praven-pro",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    license="Non-Commercial (Commercial licensing available - contact ghredpath@hotmail.com)",
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.5.0",
        "numpy>=1.20.0",
        "requests>=2.25.0",
        "scikit-learn>=1.0.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "web": ["flask>=2.0.0"],
        "viz": ["plotly>=5.0.0", "matplotlib>=3.5.0"],
        "dev": ["pytest>=7.0.0", "black>=22.0.0", "flake8>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "praven=validate:main",
            "praven-web=web_app:main",
        ],
    },
    include_package_data=True,
    package_data={
        "praven": [
            "data/*.json",
            "data/*.csv",
        ],
    },
    keywords="birdnet acoustic monitoring ornithology bioacoustics validation",
    project_urls={
        "Documentation": "https://github.com/Ziforge/praven-pro/blob/main/README.md",
        "Source": "https://github.com/Ziforge/praven-pro",
        "Bug Reports": "https://github.com/Ziforge/praven-pro/issues",
    },
)
