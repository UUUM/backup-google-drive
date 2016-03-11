.PHONY: python-clean
python-clean:
	find $(TOP_DIR) \
		-name '*.pyc' -o \
		-name __pycache__ -o \
		-name .cache -o \
		-name .eggs -o \
		-name '*.egg-info' | xargs rm -rf

.PHONY: python-test
python-test:
	python setup.py test
