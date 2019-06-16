


.PHONY: help clean build test

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean      clean the setup and sphinx builds"
	@echo "  build      build sphinx and setup sdist"
	@echo "  release    build, then commit and push, then upload"


clean:
	python setup.py clean
	cd docs && make clean
	rm -rf build dist __pycache__ *.pyc *.egg-info

test:
	cd docs && make doctest
	
build: test
	python setup.py build_sphinx bdist_wheel --universal
	ls dist/*

release: build
	twine upload dist/jsontree*.whl
