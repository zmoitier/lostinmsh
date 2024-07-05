#!/bin/sh

check_venv() {
    # python -c "import sys; print(sys.prefix != sys.base_prefix)"
    if [ "$VIRTUAL_ENV" = "" ]; then
        echo "Must be in a virtual environment to update."
        exit 1
    fi
}

remove_directory() {
    find . -name "$1" -type d \
        -exec echo "removing {}" \; \
        -exec rm -dr {} +
}

remove_file() {
    find . -name "$1" -type f \
        -exec echo "removing {}" \; \
        -exec rm {} +
}

case "$1" in
-c)
    remove_directory "__pycache__"
    remove_directory ".ipynb_checkpoints"

    remove_directory ".mypy_cache"
    remove_directory ".ruff_cache"

    remove_directory ".pytest_cache"
    remove_directory "htmlcov"
    remove_file ".coverage"
    ;;
-d)
    make -C ./docs/ clean html
    ;;
-f)
    echo ">> run ruff format"
    python -m ruff format .
    echo ">> run docformatter"
    python -m docformatter --in-place ./
    ;;
-i)
    python -m flit install --symlink
    ;;
-t)
    python -m mypy ./lostinmsh/
    python3 -m ruff check ./lostinmsh/
    # python3 -m pytest ./tests/
    ;;
-u)
    python -m pip install --upgrade pip
    python -m pip install --upgrade -r requirements.txt
    python -m pip install --upgrade -r requirements-all.txt
    python -m pip install --upgrade -r requirements-dev.txt
    python -m pip install --upgrade -r requirements-doc.txt
    ;;
*)
    echo "The choice are:"
    echo "  > [-c] for cleaning the temporary python file;"
    echo "  > [-d] generate the documentation;"
    echo "  > [-f] for formatting the code;"
    echo "  > [-i] locally install lostinmsh;"
    echo "  > [-t] for testing the code;"
    echo "  > [-u] for updating the python package."
    exit 1
    ;;
esac
