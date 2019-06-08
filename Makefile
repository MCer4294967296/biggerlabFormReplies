venv: vendor/venv-update requirements.txt
	vendor/venv-update \
		venv= --python python3 venv \
		install= -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
