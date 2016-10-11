from setuptools import setup

setup(
    name='ooktools',
    description='On-off keying tools for your SDR',
    author='Leon Jacobs',
    author_email='leonja511@gmail.com',
    url='https://github.com/leonjza/ooktools',
    download_url='https://github.com/leonjza/ooktools/tarball/1.2',
    keywords=['sdr', 'on-off', 'keying', 'rfcat', 'radio'],
    version='1.2',
    packages=[
        'ooktools',
        'ooktools.commands',
    ],
    include_package_data=True,
    install_requires=[
        'bitstring',
        'click',
        'matplotlib',
        'numpy',
        'peakutils',
    ],
    entry_points={
        'console_scripts': [
            'ooktools=ooktools.console:cli',
        ],
    },
)
