from setuptools import setup, find_packages

setup(
    name="midiscript",
    version="0.2.2",
    author="arsnovo",
    description="Programming language for musicians",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[
        "midiutil>=1.2.1",
    ],
    entry_points={
        "console_scripts": [
            "midiscript=midiscript.cli:main",
        ],
    },
)
