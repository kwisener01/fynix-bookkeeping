@echo off
echo ================================================================================
echo FYNIX FRONTEND - AUTOMATED SETUP
echo ================================================================================
echo.

echo Step 1: Installing all npm dependencies...
echo.

npm install @supabase/supabase-js ^
  lucide-react ^
  @radix-ui/react-dialog ^
  @radix-ui/react-dropdown-menu ^
  @radix-ui/react-toast ^
  class-variance-authority ^
  clsx ^
  tailwind-merge ^
  react-dropzone ^
  date-fns ^
  recharts

echo.
echo ================================================================================
echo Step 2: Creating directory structure...
echo ================================================================================
echo.

if not exist "types" mkdir types
if not exist "lib" mkdir lib
if not exist "components" mkdir components

echo ✓ Directories created
echo.

echo ================================================================================
echo Step 3: Setup complete!
echo ================================================================================
echo.
echo Next steps:
echo   1. Copy files from frontend/ folder to this directory
echo   2. Create .env.local file with your Supabase credentials
echo   3. Run: npm run dev
echo.
echo ================================================================================

pause
