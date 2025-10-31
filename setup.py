"""
Setup configuration for loggerheads package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="loggerheads",
    version="1.1.1",
    author="Mitchel Dennis",
    author_email="elmitchay@gmail.com",
    description="Blockchain-powered work tracker with automated payments - track work hours, submit to blockchain, earn USDC automatically",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/stElmitchay/loggerheads",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Office/Business :: Scheduling",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: MacOS",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires=">=3.8",
    install_requires=[
        # Core tracking dependencies
        "pygetwindow>=0.0.9",
        "pillow>=10.0.0",
        "pytesseract>=0.3.10",
        "pynput>=1.7.6",

        # UI and display
        "rich>=13.0.0",
        "textual>=0.41.0",

        # Blockchain integration
        "solana>=0.30.0",
        "solders>=0.18.0",

        # API and networking
        "requests>=2.31.0",
        "flask>=2.3.0",
        "flask-cors>=4.0.0",
        "flask-limiter>=3.5.0",

        # Configuration and utilities
        "python-dotenv>=1.0.0",

        # Liveness detection (biometric verification)
        "opencv-python>=4.8.0",
    ],
    entry_points={
        "console_scripts": [
            "loggerheads=loggerheads.cli:main",
            "daily-tracker=loggerheads.cli:main",
        ],
    },
    include_package_data=True,
    keywords="work-tracker blockchain solana cryptocurrency automation time-tracking",
    project_urls={
        "Bug Reports": "https://github.com/stElmitchay/loggerheads/issues",
        "Documentation": "https://github.com/stElmitchay/loggerheads#readme",
    },
)
