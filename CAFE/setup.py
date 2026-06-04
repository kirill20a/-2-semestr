from setuptools import setup, find_packages

setup(
    name="cafe-is",
    version="1.0.0",
    description="Информационная система автоматизации кафе",
    author="Агаев Кирилл, Асанов Денис",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[],
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)