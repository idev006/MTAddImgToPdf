@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8

echo ========================================================
echo PDF Footer Image Adder
echo ========================================================
echo.

set PYTHON_EXEC="D:\dev\MTAddImgToPdf\my_env\Scripts\python.exe"
set SCRIPT_PATH="%~dp0add_footer.py"

echo Running script: %SCRIPT_PATH%
echo Using Python: %PYTHON_EXEC%
echo.

%PYTHON_EXEC% %SCRIPT_PATH%

echo.
echo ========================================================
pause
