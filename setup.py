"""Setup configuration for DataDialogue."""
from setuptools import setup, find_packages

setup(
    name="datadialogue",
    version="1.0.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "streamlit>=1.31.1",
        "langchain>=0.3.0",
        "langchain-core>=0.3.0",
        "langchain-openai>=0.2.0",
        "langchain-groq>=0.2.0",
        "langgraph>=0.2.28",
        "python-dotenv>=1.0.1",
        "pandas>=2.2.0",
        "plotly>=5.19.0",
        "matplotlib>=3.8.3",
        "seaborn>=0.13.2",
        "typing-extensions>=4.9.0",
        "pydantic>=2.6.1",
    ],
)
