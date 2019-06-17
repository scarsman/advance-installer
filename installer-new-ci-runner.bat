@echo off
setlocal enableextensions disabledelayedexpansion

set gitlab_token="%1"
set ci_dir="C:\Users\Administrator\Desktop\ci-cd"

if not exist %ci_dir% mkdir %ci_dir%
if not exist %ci_dir%\scl_installer mkdir %ci_dir%\scl_installer


::download python3.6, requirements, refresh cmd env
curl -s https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe -o %USERPROFILE%\python-3.6.8-amd64.exe
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/requirements.txt -o %USERPROFILE%\requirements.txt
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/refreshenv.cmd -o %USERPROFILE%\refreshenv.cmd
curl -s https://nodejs.org/dist/v10.15.3/node-v10.15.3-x64.msi -o %USERPROFILE%\node-v10.15.3-x64.msi 

::install python3.6
echo Installing python 3.6
%USERPROFILE%\python-3.6.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

::install node js
echo Installing nodejs
msiexec /i %USERPROFILE%\node-v10.15.3-x64.msi  /qn /norestart

echo Refreshing cmd/system environment
call %USERPROFILE%\refreshenv.cmd

echo Installing python pip modules
pip install -r %USERPROFILE%\requirements.txt

echo Installing electron electron-packager
call npm install electron electron-packager -g

echo Refreshing cmd/system environment
call %USERPROFILE%\refreshenv.cmd


echo Installing advanced installer
curl -s https://www.advancedinstaller.com/downloads/advinst.msi -o %USERPROFILE%\advinst.msi
msiexec /i %USERPROFILE%\advinst.msi /qn /norestart

echo Installing gitlab runner
curl -s https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-windows-amd64.exe -o %USERPROFILE%\gitlab-runner.exe
%USERPROFILE%\gitlab-runner.exe uninstall
%USERPROFILE%\gitlab-runner.exe install

echo Register gitlab runner
%USERPROFILE%\gitlab-runner.exe register --non-interactive --url https://gitlab.com/ --registration-token %gitlab_token% --executor shell --name ci-runner --output-limit 10240 --builds-dir %ci_dir% --custom_build_dir-enabled
more +1 %USERPROFILE%\config.toml > %USERPROFILE%\config.toml.temp
echo concurrent = 3 > %USERPROFILE%\config.toml
type %USERPROFILE%\config.toml.temp >> %USERPROFILE%\config.toml
del %USERPROFILE%\config.toml.temp

echo Start gitlab runner
%USERPROFILE%\gitlab-runner.exe start

echo Installing git
curl -s https://github.com/git-for-windows/git/releases/download/v2.22.0.windows.1/Git-2.22.0-64-bit.exe -o %USERPROFILE%\Git-2.exe
%USERPROFILE%\Git-2.exe /quiet
