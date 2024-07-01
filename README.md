# OiHelper

[![Test and Lint](https://img.shields.io/github/actions/workflow/status/ste1hi/OiRunner/main.yml?logo=github&label=Test%20and%20Lint)](https://github.com/ste1hi/OiRunner/actions/workflows/main.yml)
![last commit](https://img.shields.io/github/last-commit/ste1hi/OiRunner)
[![Codecov](https://img.shields.io/codecov/c/github/ste1hi/OiRunner)](https://app.codecov.io/gh/ste1hi/OiRunner)
![Static Badge](https://img.shields.io/badge/platform-Windows%20%7C%20Linux-yellow)
[![PyPI](https://img.shields.io/pypi/v/OiRunner)](https://pypi.org/project/OiRunner/)
![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12-blue)

This package is designed to help oier compile the cpp file conveniently.

## Features

- Compile cpp file.
- Judge program result.
- Project manager.
- Super easy to use, you don't need write more source code, just use in command line.

## Install
You can install this package via pip conveniently.

```bash
pip install OiRunner
```

## Basic Usage
You can use this module in command line.

```bash
oirun <your_program_file_name>
```

This command will compile your program file and run the executable file in command line directly.

## Project Manager
```bash
oirunner make <project name>
```
This command will make a project named `<project name>` in current directory. In the directory, some files will be created. `in.txt` will be created as input file, `out.txt` will be created as output file, `ans.txt` will be created as answer file. If you want to name these files like `<project name>.in`, add the `-f` or `--follow_project` flag.

If `cpp` file was expected to be created, add the `-c` or `--cpp` flag. The `<project name>.cpp` will be created.

## Advanced Usage

- [Judge program result](docs/judge.md)
- [Automatic operation](docs/automation.md)


# License
Copyright ste1hi, 2024.

Distributed under the terms of the [MIT License](./LICENSE).