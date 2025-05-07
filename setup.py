from pathlib import Path
from setuptools import setup

ROOT = Path(__file__).parent
setup(
    name="zilant-prime-core",
    version="0.1.0",
    description="ZILANT Prime™ cryptographic core",
    long_description=(ROOT / "README.md").read_text(encoding="utf-8"),
    long_description_content_type="text/markdown",
    author="QuantumKey UYU",
    license="MIT",
    python_requires=">=3.9",
    package_dir={"": "src"},
    py_modules=["aead", "kdf", "vdf", "tlv", "zil", "uyi"],
    install_requires=["cryptography>=42", "argon2-cffi>=23", "click>=8.1"],
    extras_require={
        "dev": ["pytest>=8", "hypothesis>=6", "bandit>=1.7", "flake8>=6"],
    },
    entry_points={"console_scripts": ["uyi=uyi:cli"]},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
