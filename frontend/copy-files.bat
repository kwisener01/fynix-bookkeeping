@echo off
echo ================================================================================
echo COPYING FRONTEND FILES
echo ================================================================================
echo.
echo This script will copy all frontend files to your Next.js project
echo.

set SOURCE=%~dp0
set TARGET=%1

if "%TARGET%"=="" (
    echo ERROR: Please provide the target directory
    echo Usage: copy-files.bat "C:\Projects\contractor_bookkeeping\fynix-frontend"
    pause
    exit /b 1
)

echo Source: %SOURCE%
echo Target: %TARGET%
echo.

echo Copying files...
echo.

xcopy /E /I /Y "%SOURCE%types" "%TARGET%\types"
xcopy /E /I /Y "%SOURCE%lib" "%TARGET%\lib"
xcopy /E /I /Y "%SOURCE%components" "%TARGET%\components"
xcopy /E /I /Y "%SOURCE%app\dashboard" "%TARGET%\app\dashboard"

echo.
echo ================================================================================
echo ✓ Files copied successfully!
echo ================================================================================
echo.
echo Next: Create .env.local file in %TARGET%
echo.

pause
