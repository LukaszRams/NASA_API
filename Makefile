.PHONY: help clean
VENV = .venv
PYTHON = $(VENV)/Scripts/python.exe
PYINSTALLER = $(VENV)/Scripts/pyinstaller.exe


help:
	@echo "---------------HELP-----------------"
	@echo "make setup     To setup the project"
	@echo "make run       To run the project "
	@echo "make mypy      To run mypy on"
	@echo "make black     To run style checker"
	@echo "make clean     To clean the project"
	@echo "------------------------------------"

activate: setup pyproject.toml
	poetry shell

setup: pyproject.toml
	python -m poetry install

mypy: setup
	$(PYTHON) -m mypy --strict .

black: setup
	$(PYTHON) -m black .

pylint: setup
	$(PYTHON) -m pylint *

flake: setup
	$(PYTHON) -m flake8 --statistics

isort: setup
	$(PYTHON) -m isort .

all: mypy black pylint flake isort
	@echo run all without main program

run: setup
	$(PYTHON) main.py

clean:
	rm -rf .venv
	rm -rf nasaAPI

export: $(VENV)
	poetry export --with=dev --without-hashes --output=requirements_dev.txt
	poetry export --without-hashes --output=requirements.txt

update: $(VENV)
	poetry update

test: $(VENV)
	$(PYTHON) -m coverage run -m unittest
	$(PYTHON) -m coverage report -m
	$(PYTHON) -m coverage html
	@echo Open codecov report at http://localhost:63342/NASA_API/htmlcov/index.html?_ij_reload=RELOAD_ON_SAVE


build: clean
	python -m poetry install --without dev --with build
	$(PYINSTALLER) -F --windowed --name NASA_API --specpath=./nasaApi/build --workpath=./nasaApi/build --distpath=./nasaApi main.py
	$(MAKE) clean



