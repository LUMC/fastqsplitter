# Copyright (c) 2019 Leiden University Medical Center
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from setuptools import find_packages, setup

with open("README.md", "r") as readme_file:
    LONG_DESCRIPTION = readme_file.read()

setup(
    name="fastqsplitter",
    version="0.1.0-dev",
    description="Splits FASTQ files evenly.",
    author="Leiden University Medical Center",
    author_email="sasc@lumc.nl",  # A placeholder for now
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/markdown",
    license="MIT",
    keywords="fastq split",
    zip_safe=False,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url="https://github.com/LUMC/fastqsplitter",
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires=">=3.5",  # Because we use type annotation.
    install_requires=[
        # Temporarily use git branch.
        # Wait until https://github.com/marcelm/xopen/pull/11 is merged and
        # released
        "xopen @ https://github.com/rhpvorderman/xopen/"
        "releases/download/parallelopen/xopen-0.5.2.dev2+gd2fa806.tar.gz"
    ],
    entry_points={
        "console_scripts": [
            'fastqsplitter=fastqsplitter:main'
        ]
    }
)