- pyLint issues:
    https://code.visualstudio.com/docs/python/environments#_choosing-an-environment
    # [pylint] Unable to import 'field.Field'
    Ctrl+Shift+P >> Python: Select Interpreter >> select desired version of python that is installed on your machine

    select and isntall desired linter:
    https://code.visualstudio.com/docs/python/linting
    Ctrl+Shift+P >> search: python linting pylintEnabled >> click: Extensions.Python >> select a linter: Ex: MyPy

- Run UnitTests:
    set PYTHONHASHSEED=0
    cd src
    python -m unittest