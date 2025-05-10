from pathlib import Path

from setuptools import find_packages, setup

here = Path(__file__).parent
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name="zilant-prime-core",
    version="0.1.0",
    description="Core library for ZILANT Prime phase VDF and encryption",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="you@example.com",
    license="MIT",
    python_requires=">=3.9,<4.0",  # <-- сюда тоже
    packages=find_packages(where="src"),
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
            "bandit>=1.7.0",
            "pre-commit>=2.20.0",
            "isort>=5.0",
            "black>=23.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bench-vdf=bench_vdf:main",
        ],
    },
)
