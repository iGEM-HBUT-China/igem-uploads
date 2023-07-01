from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

requirements = ["wheel"]

setup(
    name="igem-uploads",
    version="0.0.1",
    author="lty2002",
    author_email="liangtianyi2002@outlook.com",
    description="Helps iGEMers upload their files to the iGEM server.",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/iGEM-HBUT-China/igem-uploads",
    packages=find_packages(),
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
    ],
)
