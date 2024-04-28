from setuptools import setup, find_packages

setup(
    name = 'OiRunner',
    version = '0.0.3',
    author = 'ste1',
    author_email = '1874076121@qq.com',
    description = 'This package is designed to help oier compile the cpp file conveniently.',
    url = 'https://github.com/ste1hi/OiRunner',
    packages = find_packages(),
    python_requires = '>=3.6',
    include_package_data = True,
    entry_points={
        'console_scripts': [
            'oirun = OiRunner.BetterRunner:main' 
        ]
    }
)
