from setuptools import setup, find_packages
import jsontree

setup(
    name="jsontree",
    version=jsontree.__version_string__,
    description="Utility class for managing json tree data as python objects. "
        "Recursive depth dictionaries with keys as attributes and "
        "json serialization.",
    long_description=open('README.rst').read(),
    url="https://github.com/dougn/jsontree/",
    author=jsontree.__author__,
    author_email=jsontree.__email__,
    license="BSD",
    py_modules=['jsontree'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Utilities",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    keywords=["json", "utility", "util"],
)
