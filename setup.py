#!/usr/bin/env python3
"""
SafeErase Python Package Setup
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "python-ui" / "requirements.txt"
requirements = []
if requirements_file.exists():
    with open(requirements_file, 'r') as f:
        requirements = [
            line.strip() 
            for line in f 
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="safeerase",
    version="1.0.0",
    author="SafeErase Project",
    author_email="contact@safeerase.com",
    description="Professional secure data wiping solution with tamper-proof certificates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/safeerase/SafeErase",
    project_urls={
        "Bug Tracker": "https://github.com/safeerase/SafeErase/issues",
        "Documentation": "https://docs.safeerase.com",
        "Source Code": "https://github.com/safeerase/SafeErase",
    },
    packages=find_packages(include=["python_ui*", "python_api*", "python_tools*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Systems Administration",
        "Topic :: Security",
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-mock>=3.10.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "coverage>=7.0.0",
        ],
        "crypto": [
            "cryptography>=41.0.0",
            "pycryptodome>=3.19.0",
        ],
        "ui": [
            "customtkinter>=5.2.0",
            "pillow>=10.0.0",
            "tkinter-tooltip>=2.1.0",
        ],
        "tools": [
            "pyyaml>=6.0.0",
            "rich>=13.7.0",
            "tqdm>=4.66.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "safeerase-ui=python_ui.main:main",
            "safeerase-scan=python_tools.device_scanner:main",
            "safeerase-validate=python_tools.certificate_validator:main",
            "safeerase-schedule=python_tools.wipe_scheduler:main",
        ],
    },
    include_package_data=True,
    package_data={
        "python_ui": ["assets/*", "*.ico"],
        "python_tools": ["*.yaml", "*.json"],
    },
    zip_safe=False,
    keywords=[
        "data-wiping", "secure-erase", "data-destruction", "compliance",
        "nist", "dod", "certificate", "forensics", "security", "privacy"
    ],
)
