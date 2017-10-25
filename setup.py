from setuptools import setup

setup(
    name='mrt-file-server',
    packages=['mrt-file-server'],
    include_package_data=True,
    install_requires=[
        'flask',
    ],
)