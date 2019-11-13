@echo off

cd C:\Users\felix.sterzelmaier\Desktop\workspaces\ITSG_ansible\02_synergy\git\synergy-ansible\feste-script

echo.
echo Setting Paths
set pythonpath="C:\Users\felix.sterzelmaier\AppData\Local\Programs\Python\Python37\"
set srcpath=%cd%

rem echo.
rem echo Install dependences
rem C:
rem cd %pythonpath%
rem cd Scripts
rem pip.exe install --upgrade pip
rem pip.exe install xlrd pytz tzlocal

echo.
echo Run Script...
cd %srcpath%
%pythonpath%python.exe --version
%pythonpath%python.exe convert.py


echo.
echo End of Script...
pause