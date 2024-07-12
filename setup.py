from setuptools import setup, find_packages

version = {}
with open("dna_mutator/version.py") as fp:
    exec(fp.read(), version)

setup(
    name="dna_mutator",
    version=version["__version__"],
    author="B237870",
    author_email="egf-software@ed.ac.uk",
    description="Create variants of DNA sequences",
    long_description=open("pypi-readme.rst").read(),
    long_description_content_type="text/x-rst",
    license="MIT",
    keywords="biology dna",
    packages=find_packages(exclude="docs"),
    include_package_data=True,
    install_requires=["biopython"],
)
