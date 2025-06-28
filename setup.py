from setuptools import find_packages, setup

setup(
    name='mcqgenrator',
    version='1.0.0',
    author='faizanhere221',
    author_email='islam9039438@gmail.com',
    install_requires=["openai", "langchain", "streamlit", "python-dotenv", "PyPDF2"],
    packages=find_packages()
)