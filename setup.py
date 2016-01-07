"""Setup for submit-and-compare xblock"""

import os
from setuptools import setup


def package_data(pkg, root):
    """Generic function to find package_data for `pkg` under `root`."""
    data = []
    for dirname, _, files in os.walk(os.path.join(pkg, root)):
        for fname in files:
            data.append(os.path.relpath(os.path.join(dirname, fname), pkg))

    return {pkg: data}


setup(
    name='xblock-submit-and-compare',
    version='0.4',
    description='Submit and Compare XBlock for self assessment',
    packages=[
        'submit_and_compare',
    ],
    install_requires=[
        'XBlock',
    ],
    entry_points={
        'xblock.v1': [
            'submit-and-compare = submit_and_compare:SubmitAndCompareXBlock',
        ]
    },
    package_data=package_data("submit_and_compare", "static"),
)