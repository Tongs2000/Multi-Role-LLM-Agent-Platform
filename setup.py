from setuptools import find_packages, setup


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="openmanus",
    version="0.1.0",
    author="mannaandpoem and OpenManus Team",
    author_email="mannaandpoem@gmail.com",
    description="A versatile agent that can solve various tasks using multiple tools",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mannaandpoem/OpenManus",
    packages=find_packages(),
    install_requires=[
        "pydantic~=2.10.6",
        "openai~=1.66.3",
        "tenacity~=9.0.0",
        "pyyaml~=6.0.2",
        "loguru~=0.7.3",
        "numpy",
        "datasets~=3.4.1",
        "fastapi~=0.115.11",
        "tiktoken~=0.9.0",
        "html2text~=2024.2.26",
        "gymnasium~=1.1.1",
        "pillow~=11.1.0",
        "browsergym~=0.13.3",
        "uvicorn~=0.34.0",
        "unidiff~=0.7.5",
        "googlesearch-python~=1.3.0",
        "baidusearch~=1.0.3",
        "duckduckgo_search~=7.5.3",
        "aiofiles~=24.1.0",
        "pydantic_core~=2.27.2",
        "colorama~=0.4.6",
        "playwright~=1.51.0",
        "docker~=7.1.0",
        "pytest~=8.3.5",
        "pytest-asyncio~=0.25.3",
        "httpx>=0.27.0",
        "tomli>=2.0.0",
        "boto3~=1.37.18",
        "requests~=2.32.3",
        "beautifulsoup4~=4.13.3",
        "huggingface-hub~=0.29.2",
        "setuptools~=75.8.0",
        "confluent-kafka~=2.3.0",
        "aiokafka~=0.8.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "openmanus=main:main",
        ],
    },
)
