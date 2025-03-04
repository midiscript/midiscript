from setuptools import setup, find_packages

setup(
    name="midiscript",
    version="0.2.1",
    packages=find_packages(),
    author="arsnovo",
    description="Programming language for musicians",
    python_requires=">=3.6",
    install_requires=[
        "midiutil>=1.2.1",
    ],
)
