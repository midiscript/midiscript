from setuptools import setup, find_packages

setup(
    name="midiscript",
    version="0.2.3",
    packages=find_packages(),
    author="arsnovo",
    description="Programming language for musicians",
    python_requires=">=3.6",
    install_requires=[
        "midiutil>=1.2.1",
    ],
    entry_points={
        "console_scripts": [
            "midiscript=midiscript.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Musicians",
        "Topic :: Multimedia :: Sound/Audio :: MIDI",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
)
