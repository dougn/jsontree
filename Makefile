


.PHONY: help clean build test

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean      clean the setup and sphinx builds"
	@echo "  build      build sphinx and setup sdist"
	@echo "  release    build, then commit and push, then upload"


clean:
	python setup.py clean
	cd docs && make clean
	rm -f commit.txt

test:
	cd docs && make doctest
	
build: test
	python setup.py build_sphinx bdist_wheel --universal

release: build
	python setup.py upload_sphinx
	twine upload dist/jsontree*.whl
