from setuptools import setup, find_packages

setup(
    name="zilant-prime-core",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        "argon2-cffi>=21.3.0",
        "cryptography>=40.0.0",
        "click>=8.0.0",
    ],
    entry_points={
        "console_scripts": [
            "uyu-box=uyu_box.cli:main",
        ],
    },
)
