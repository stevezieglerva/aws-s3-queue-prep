cls

call ..\Scripts\activate
set text_logging=Y
call python -m unittest integration_tests.py integration_tests_S3TextFromLambdaEvent.py

call deactivate
