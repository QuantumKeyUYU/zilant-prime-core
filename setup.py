#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from pathlib import Path

this_dir = Path(__file__).parent
long_description = (this_dir / "README.md").read_text(encoding="utf-8")

setup(
    name="zilant-prime-core",
    version="0.1.0",
    description="Core library for ZILANT Prime phase VDF and encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages("src"),
    package_dir={"": "src"},
    install_requires=[
        "aead>=0.2,<1.0",
        "cryptography>=3.4.7",
        "argon2-cffi>=21.3.0",
        "hypothesis>=6.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "flake8>=5.0.0",
            "black>=23.0",
            "isort>=5.0",
            "bandit>=1.7",
            "pre-commit>=2.20",
        ],
    },
    entry_points={
        "console_scripts": [
            "bench-vdf=bench_vdf:main",
        ],
    },
    python_requires=">=3.9, <3.14",
)
