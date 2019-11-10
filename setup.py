from setuptools import setup

with open("README.md", "r") as fh:
    DESCR = fh.read()

setup(
    name='xviz',
    version='0.0.2',
    description='Python implementation of XVIZ protocol',
    author='Yuanxin Zhong',
    author_email='cmpute@gmail.com',
    url="https://github.com/cmpute/xviz.py",
    long_description=DESCR,
    packages=['xviz'],
    install_requires=['numpy', 'easydict'],
)
