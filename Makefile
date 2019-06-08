venv: vendor/venv-update requirements.txt
	vendor/venv-update \
		venv= -ppython3 venv \
		install= -r requirements.txt

.PHONY: clean
clean:
	rm -rf venv
