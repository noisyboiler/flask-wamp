test:
	pip install --editable .[dev]
	py.test ./tests -vs
