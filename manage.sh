#!/bin/sh

remove_directory() {
    find . \
        -type d \
        -name "$1" \
        -exec echo "removing {}" \; \
        -exec rm -dr {} +
}

remove_file() {
    find . \
        -type f \
        -name "$1" \
        -exec echo "removing {}" \; \
        -exec rm {} +
}

case "$1" in
-c | --clean)
    remove_directory "__pycache__"
    remove_directory ".ipynb_checkpoints"

    remove_directory ".mypy_cache"
    remove_directory ".ruff_cache"

    remove_directory ".pytest_cache"
    remove_directory "htmlcov"
    remove_file ".coverage"

    remove_directory "_build"

    remove_file "*.msh"
    ;;
-d | --docs)
    make -C ./docs/ clean html
    ;;
-f | --format)
    echo ">> run ruff format"
    python -m ruff check --select I --fix .
    python -m ruff format .
    echo ">> run docformatter"
    python -m docformatter --in-place ./lostinmsh/
    ;;
-i | --install)
    uv pip install -e .
    ;;
-t | --test)
    python -m mypy ./lostinmsh/
    python -m pytest --cov=lostinmsh --cov-report=html ./tests/
    find ./tests/ -name "*.msh" -delete
    ;;
-u | --update)
    uv self update
    rm uv.lock
    uv sync --all-extras
    uv export --format requirements.txt --frozen --no-hashes --no-annotate -o requirements.txt
    uv export --extra plot --format requirements.txt --frozen --no-hashes --no-annotate -o requirements-plot.txt
    uv export --extra doc --format requirements.txt --frozen --no-hashes --no-annotate -o docs/requirements.txt
    ;;
*)
    echo "The choice are:"
    echo "  > [-c | --clean] for cleaning the temporary python file;"
    echo "  > [-d | --docs] generate the documentation;"
    echo "  > [-f | --format] for formatting the code;"
    echo "  > [-i | --install] locally install lostinmsh;"
    echo "  > [-t | --test] for testing the code;"
    echo "  > [-u | --update] for updating the python package."
    exit 1
    ;;
esac
