clean:
	rm -rf dist/

prepare:
	pip3 install -r requirements.txt -r test_requirements.txt

build:
	python3 setup.py sdist

checkstyle:
	python3 -m pylint -j 0 -f parseable mlsteam
