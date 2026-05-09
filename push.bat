@echo off
setlocal enabledelayedexpansion

echo.
echo ========================================
echo        Git Push Automation Script
echo ========================================
echo.

:: Stage all changes
echo [+] Staging all changes...
git add .

:: Check if there are changes to commit
git diff --cached --quiet
if !errorlevel! equ 0 (
    echo [!] No changes to commit.
    goto :end
)

:: Get commit message
set "commit_msg="
set /p commit_msg="Enter commit message (Press Enter for 'Update'): "

if "!commit_msg!"=="" (
    set "commit_msg=Update"
)

:: Commit changes
echo.
echo [+] Committing changes: "!commit_msg!"
git commit -m "!commit_msg!"

:: Push to main
echo.
echo [+] Pushing to origin main...
git push origin main

:end
echo.
echo ========================================
echo        Process Completed!
echo ========================================
echo.
pause
