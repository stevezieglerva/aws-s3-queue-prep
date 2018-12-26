set function_name=aws-code-index-escape-files
title %function_name%

call cd .\tests
call run_all_tests.bat
set test_error=%ERRORLEVEL%
call cd ..
IF %test_error%==1 goto failed

call commit_and_push.bat

REM Zip the lambda function
call del /q lambda_function.zip
call "c:\Program Files\7-Zip\7z.exe" a lambda_function.zip *.py
cd .\Lib\site-packages
call "c:\Program Files\7-Zip\7z.exe" a ..\..\lambda_function.zip *
cd ..\..\

REM Upload the new code
call aws lambda update-function-code --function-name %function_name% --zip-file fileb://lambda_function.zip
goto end

:failed
echo *** Tests failed, so aborted packaging


:end
echo %time%
