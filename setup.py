from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read().replace(".. include:: toc.rst\n\n", "")

# The lines below can be parsed by `docs/conf.py`.
name = "circuit"
version = "0.5.0"

setup(
    name=name,
    version=version,
    packages=[name,],
    install_requires=[
        "parts~=1.3",
        "logical~=0.4"
    ],
    license="MIT",
    url="https://github.com/reity/circuit",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Minimal native Python library for building " +\
                "and working with logical circuits.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
)
