.PHONY: python-clean
python-clean:
	find $(TOP_DIR) -name '*.pyc' | xargs rm -f
	find $(TOP_DIR) -name '__pycache__' | xargs rm -rf
