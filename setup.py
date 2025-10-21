"""
Setup script for F1 Commentary package.
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_file.exists():
    requirements = requirements_file.read_text().strip().split('\n')
    requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="f1-commentary",
    version="1.0.0",
    author="F1 Commentary Team",
    author_email="",
    description="A comprehensive toolkit for F1 race data collection, analysis, commentary generation, and visualization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/f1-commentary",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
            "pre-commit>=2.0",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=1.0",
            "myst-parser>=0.15",
        ],
    },
    entry_points={
        "console_scripts": [
            "f1-commentary=f1_commentary.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "f1_commentary": [
            "visualization/assets/*",
            "visualization/track_data/*",
        ],
    },
    keywords="f1 formula1 racing data analysis commentary visualization",
    project_urls={
        "Bug Reports": "https://github.com/your-username/f1-commentary/issues",
        "Source": "https://github.com/your-username/f1-commentary",
        "Documentation": "https://f1-commentary.readthedocs.io/",
    },
)
