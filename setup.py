from setuptools import setup, find_packages

setup(
    name="zilant-prime-core",
    version="0.1.0",
    author="Ваше Имя",
    author_email="you@example.com",
    description="Core library for Zilant Prime containers with VDF, AEAD and CLI",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourorg/zilant-prime-core",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0",
        "cryptography>=39.0.0",
        # и другие зависимости...
    ],
    entry_points={
        "console_scripts": [
            "zilant=zilant_prime_core.cli:cli",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
