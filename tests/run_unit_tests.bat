cls

call ..\Scripts\activate
set text_logging=Y
call python -m unittest unit_tests.py

call deactivate
