SHELL=/bin/bash
PROJECT_NAME=bullet_safety_gym
PROJECT_PATH=${PROJECT_NAME}/
PYTHON_FILES = $(shell find setup.py ${PROJECT_NAME} tests -type f -name "*.py")

check_install = python3 -c "import $(1)" || pip3 install $(1) --upgrade
check_install_extra = python3 -c "import $(1)" || pip3 install $(2) --upgrade

pytest:
	$(call check_install, pytest)
	$(call check_install, pytest_cov)
	$(call check_install, pytest_xdist)
	pytest test --cov ${PROJECT_PATH} --durations 0 -v --cov-report term-missing --color=yes

mypy:
	$(call check_install, mypy)
	mypy ${PROJECT_NAME}

lint:
	$(call check_install, flake8)
	$(call check_install_extra, bugbear, flake8_bugbear)
	flake8 ${PYTHON_FILES} --count --show-source --statistics

format:
	$(call check_install, isort)
	isort ${PYTHON_FILES}
	$(call check_install, yapf)
	yapf -ir ${PYTHON_FILES}

check-codestyle:
	$(call check_install, isort)
	$(call check_install, yapf)
	isort --check ${PYTHON_FILES} && yapf -r -d ${PYTHON_FILES}


# commit-checks: check-codestyle

.PHONY: format check-codestyle # commit-checks