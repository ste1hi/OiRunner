from setuptools import setup, find_packages

setup(
    name = 'OiRunner',
    author = 'ste1',
    author_email = '1874076121@qq.com',
    description = 'This package is designed to help oier compile the cpp file conveniently.',
    url = 'https://github.com/ste1hi/OiRunner',
    long_description="README.md",
    long_description_content_type="text/markdown",
    packages = find_packages(),
    python_requires = '>=3.8',
    include_package_data = True,
    entry_points={
        'console_scripts': [
            'oirun = OiRunner.BetterRunner:main' 
        ]
    }
)
