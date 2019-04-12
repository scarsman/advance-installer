@echo off

::download python3.6, requirements, refresh cmd env
curl -s https://www.python.org/ftp/python/3.6.8/python-3.6.8-amd64.exe -o %temp%\python-3.6.8-amd64.exe
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/requirements.txt -o %temp%\requirements.txt
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/refreshenv.cmd -o %temp%\refreshenv.cmd
curl -s https://nodejs.org/dist/v10.15.3/node-v10.15.3-x64.msi -o %temp%\node-v10.15.3-x64.msi 

::install python3.6
%temp%\python-3.6.8-amd64.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0

::install node js
msiexec /i %temp%\node-v10.15.3-x64.msi  /qn /norestart


call %temp%\refreshenv.cmd

pip install -r %temp%\requirements.txt
npm install electron -g
npm install  electron-packager -g
