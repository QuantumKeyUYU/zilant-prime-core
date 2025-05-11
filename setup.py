from setuptools import setup, find_packages

setup(
    name="zilant-prime-core",
    version="0.1.0",
    description="Zero-knowledge VDF and related primitives",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "cryptography>=41.0.0",
        "numpy>=1.25.0",
        "scipy>=1.10.1",         # забираем версию, поддерживающую Py3.9–3.11
        "argon2-cffi>=23.1.0",   # новая зависимость
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "flake8>=6.0",
            "bandit>=1.7",
            "mypy>=1.5",
        ],
    },
    python_requires=">=3.9, <4",
)
