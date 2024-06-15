from setuptools import setup, find_packages

setup(
    name='sabcli',
    version='0.1.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'click',
        'pytest',
        'requests',
        'openai',
        'PyYaml'
    ],
    entry_points={
        'console_scripts': [
            'sabcli=sabcli.cli:cli',
            'scli=sabcli.cli:cli',
        ]
    },
)
