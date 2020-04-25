#!env/bin/python
from setuptools import setup

setup(
    name="pygfapi",
    version="0.0.3",
    description="Library for interacting with Gravity Forms Web API",
    url="https://bitbucket.org/ArlingtonCounty/pygfapi",
    author="Arlington County",
    author_email="webmaster@arlingtonva.us",
    license="GPLv3",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet",
    ],
    keywords="gravityforms wordpress",
    packages=["pygfapi"],
    install_requires=open("requirements.txt").readlines()
)
