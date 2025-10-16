#!/bin/sh

# shellcheck source=/dev/null
. "./.venv/bin/activate"

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
    ;;
-d | --docs)
    make -C ./docs/ clean html
    ;;
-f | --format)
    echo ">> run ruff format"
    python -m ruff check --select I --fix .
    python -m ruff format .
    echo ">> run docformatter"
    python -m docformatter --in-place ./
    ;;
-i | --install)
    python -m flit install --symlink
    ;;
-t | --test)
    python -m mypy ./lostinmsh/
    python3 -m ruff check ./lostinmsh/
    python3 -m pytest ./tests/
    ;;
-u | --update)
    uv self update
    rm uv.lock
    uv sync --extra dev
    uv export --format requirements.txt --frozen --no-hashes --no-annotate -o requirements.txt
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
