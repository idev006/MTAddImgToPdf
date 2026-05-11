@echo off
setlocal enabledelayedexpansion

:: Get escape character for colors
for /F "tokens=1,2 delims=#" %%a in ('"prompt #$H#$E# & echo on & for %%b in (1) do rem"') do set "ESC=%%b"

set "GREEN=%ESC%[92m"
set "RED=%ESC%[91m"
set "YELLOW=%ESC%[93m"
set "CYAN=%ESC%[96m"
set "RESET=%ESC%[0m"

echo.
echo %CYAN%========================================%RESET%
echo %CYAN%       Git Push Automation v2.0%RESET%
echo %CYAN%========================================%RESET%
echo.

:: Check if git repo
git rev-parse --is-inside-work-tree >nul 2>&1
if %errorlevel% neq 0 (
    echo %RED%[!] Error: Not a git repository.%RESET%
    pause
    exit /b 1
)

:: Get current branch
for /f "tokens=*" %%i in ('git rev-parse --abbrev-ref HEAD') do set "BRANCH=%%i"

:: Stage all changes
echo %GREEN%[+]%RESET% Staging all changes...
git add .

:: Check if there are changes to commit
git diff --cached --quiet
if %errorlevel% equ 0 (
    echo %YELLOW%[!] No changes to commit.%RESET%
    goto :end
)

:: Show summary of changes
echo %GREEN%[+]%RESET% Changes to be committed:
echo.
git status --short
echo.

:: Get commit message from argument or prompt
set "COMMIT_MSG=%~1"

if "%COMMIT_MSG%"=="" (
    set /p "COMMIT_MSG=%GREEN%[?]%RESET% Enter commit message (Enter for 'Update'): "
)

if "!COMMIT_MSG!"=="" (
    set "COMMIT_MSG=Update"
)

:: Commit changes
echo.
echo %GREEN%[+]%RESET% Committing to branch [%CYAN%!BRANCH!%RESET%]...
git commit -m "!COMMIT_MSG!"
if %errorlevel% neq 0 (
    echo %RED%[!] Commit failed.%RESET%
    goto :end
)

:: Push to origin
echo.
echo %GREEN%[+]%RESET% Pushing to origin %CYAN%!BRANCH!%RESET%...
git push origin !BRANCH!
if %errorlevel% neq 0 (
    echo %RED%[!] Push failed.%RESET%
) else (
    echo.
    echo %GREEN%[SUCCESS] Successfully pushed to !BRANCH!%RESET%
)

:end
echo.
echo %CYAN%========================================%RESET%
echo %CYAN%        Process Completed!%RESET%
echo %CYAN%========================================%RESET%
echo.

:: Only pause if run without arguments (interactive mode)
if "%~1"=="" pause

