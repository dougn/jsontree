


.PHONY: help clean build

help:
	@echo "Please use \`make <target>' where <target> is one of"
	@echo "  clean      clean the setup and sphinx builds"
	@echo "  build      build sphinx and setup sdist"
	@echo "  release    build, then commit and push, then upload"


clean:
	python setup.py clean
	cd docs && make clean
	rm -f commit.txt

build:
	python setup.py sdist build_sphinx

release: build
	touch commit.txt
	git commit -a -F commit.txt -e && git push
	python setup.py upload upload_sphinx
