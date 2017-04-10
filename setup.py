from setuptools import setup

setup(
    name='logistician',
    version='0.1',
    py_modules=['logistician'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        logistician=logistician:cli
    ''',
)