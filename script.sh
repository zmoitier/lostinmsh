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
    make -C ./docs/ clean html
    ;;
-f)
    echo ">> run isort"
    python -m isort ./
    echo ">> run docformatter"
    python -m docformatter --in-place ./
    echo ">> run black"
    python -m black ./
    ;;
-i)
    python -m flit install --symlink --user
    ;;
-t)
    python -m mypy ./lostinmsh/
    python -m pylint ./lostinmsh/
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
