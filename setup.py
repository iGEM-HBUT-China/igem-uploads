from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = [
    "prettytable",
    "requests",
    "lxml"
]

setup(
    name="igem-uploads",
    version="1.2.1",
    author="iGEM-HBUT-China",
    author_email="liangtianyi2002@outlook.com",
    description="Helps iGEMers upload their files to the iGEM server.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/iGEM-HBUT-China/igem-uploads",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved",
    ],
)
