.PHONY: build install release clean clean-file

build:lint
	python3 -m build

install:build
	pip3 install .

release: build
	python3 -m twine upload dist/*

clean:
	rm -rf dist build *.egg-info
	pip uninstall -y OiRunner

lint:
	flake8 OiRunner/ --count --statistics --max-line-length=127

clean-file:
	rm -rf dist build *.egg-info