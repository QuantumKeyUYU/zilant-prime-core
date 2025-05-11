from setuptools import setup, find_packages

setup(
    name="zilant-prime-core",
    version="0.1.0",
    description="Core library for Zilant Prime",
    author="Your Name",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.9",
    install_requires=[
        "argon2-cffi>=21.3.0",    # <-- добавляем зависимость
        "cryptography>=41.0.0",
        "numpy>=1.25.0",
        "scipy>=1.15.3",
        "cffi>=1.17.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "flake8>=6.0",
            "bandit>=1.7.4",
            "mypy>=1.0",
        ]
    },
)
