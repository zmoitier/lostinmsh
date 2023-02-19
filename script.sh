#!/bin/sh

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
    make -C ./docs/ html
    ;;
-f)
    python3 -m isort .
    python3 -m black .
    ;;
-i)
    python3 -m flit install --symlink --user
    ;;
-t)
    python3 -m mypy lostinmsh/
    python3 -m pylint lostinmsh/
    # python3 -m pytest tests/
    ;;
-u)
    python3 -m pip install --user --upgrade pip
    python3 -m pip install --user --upgrade -r requirements.txt
    python3 -m pip install --user --upgrade -r requirements-all.txt
    python3 -m pip install --user --upgrade -r requirements-dev.txt
    python3 -m pip install --user --upgrade -r requirements-doc.txt
    ;;
*)
    echo "The choice are:"
    echo "  > [-c] for cleaning the temporary python file;"
    echo "  > [-d] generate the documentation;"
    echo "  > [-f] for formatting the code;"
    echo "  > [-i] localy locally lostinmsh;"
    echo "  > [-t] for testing the code;"
    echo "  > [-u] for updating the python package."
    exit 1
    ;;
esac
