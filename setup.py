from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name="circuit",
    version="0.3.0",
    packages=["circuit",],
    install_requires=[
        "parts>=0.2.1",
        "logical>=0.1.0"
    ],
    license="MIT",
    url="https://github.com/reity/circuit",
    author="Andrei Lapets",
    author_email="a@lapets.io",
    description="Minimal native Python library for building " +\
                "and working with logical circuits.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    test_suite="nose.collector",
    tests_require=["nose"],
)
