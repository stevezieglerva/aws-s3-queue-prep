set function_name=aws-s3-to-es

REM Zip the lambda function
call del /q lambda_function.zip
call "c:\Program Files\7-Zip\7z.exe" a lambda_function.zip *.py
cd .\Lib\site-packages
call "c:\Program Files\7-Zip\7z.exe" a ..\..\lambda_function.zip *
cd ..\..\

REM Upload the new code
call aws lambda update-function-code --function-name %function_name% --zip-file fileb://lambda_function.zip

call cd .\tests\integration_test_aws-s3-to-es-bucket
call full_integration_test_s3_sync.bat
call cd ..\..

echo %time%

