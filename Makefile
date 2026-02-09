.PHONY: help test_with_coverage build_with_django_18

# Default target
help:
	@echo "Available commands:"
	@echo "  make test_with_coverage - Run tests with coverage report"
	@echo "  make build_with_django_18 - Build and run docker image with django 1.8"

# Run tests with coverage
test_with_coverage:
	@echo "Running tests with coverage..."
	python -m coverage run -m unittest discover -s fitbit_tests && python -m coverage report -m

# Start build with django version 1.8 and start container
build_with_django_18:
	@echo "Starting Docker build..."
	docker build -t python-fitbit18 --build-arg REQUIREMENTS_FILE=requirements/django18/test.txt .
	docker run -it --rm python-fitbit18
