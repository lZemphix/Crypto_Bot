from setuptools import setup

setup(
    name='cmx',
    version='0.1',
    py_modules=['cmx'],
    entry_points={
        'console_scripts': [
            'cmx=cmx:main',
        ],
    },
)