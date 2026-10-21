install:
	pip install flake8 mypy

run:
	python3 main.py map.txt

debug:
	python3 -m pdb main.py map.txt

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

clean:
	rm -rf __pycache__  .mypy_cache

.PHONY: install run debug lint clean
