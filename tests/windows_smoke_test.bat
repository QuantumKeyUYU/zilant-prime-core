@echo off
echo Testing zilant-gui.exe launch...
dist\zilant-gui.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 (
  echo GUI smoke test failed.
  exit /b 1
)
echo GUI smoke test passed.
exit /b 0
