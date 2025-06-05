# SPDX-FileCopyrightText: 2025 Zilant Prime Core contributors
# SPDX-License-Identifier: MIT

from setuptools import find_packages, setup

setup(
    name="zilant_prime_core",
    version="0.1.0",
    description="Zilant Prime Core library",
    author="Zilant Prime Core contributors",
    license="MIT",
    # говорим setuptools, что пакеты лежат в папке src/
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=[
        "click",
        "cryptography",
    ],
    entry_points={
        "console_scripts": [
            "zilant=zilant_prime_core.cli:cli",
        ],
    },
)
