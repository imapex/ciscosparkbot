"""
spark-python Installer using setuptools
"""
import os
from setuptools import setup


base_dir = os.path.dirname(__file__)

about = {}
with open(os.path.join(base_dir, "ciscosparkbot", "__about__.py")) as f:
    exec(f.read(), about)

setup(
    name=about["__title__"],
    version=about["__version__"],
    packages=["ciscosparkbot"],
    author=about["__author__"],
    author_email=about["__email__"],
    url=about["__uri__"],
    license=about["__license__"],
    install_requires=["requests",
                      "ciscosparkapi==0.5.5",
                      "Flask>=0.12.1"
                      ],
    description="Python Bot for Cisco Spark",
)
