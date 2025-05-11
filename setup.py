from setuptools import setup, find_packages

setup(
    name="zilant-prime-core",
    version="0.1.0",
    description="Core engine for ZILANT Prime™",
    author="Ваше Имя",
    author_email="you@example.com",
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "cryptography>=41.0.0",
        "numpy>=1.25.0",
        "scipy>=1.11.0",
    ],
    python_requires=">=3.7",
)
