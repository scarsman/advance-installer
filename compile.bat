@echo on

setlocal

:: kill running processes
taskkill /f /im sclexpress.exe
taskkill /f /im sclremote.exe
taskkill /f /im syncthing.exe
taskkill /f /im scl_appv1.exe

if not exist %cd%\scl-app mkdir %cd%\scl-app
cd %cd%\scl-app

set curpath="%cd%"

if not exist %curpath%\scl-installer mkdir %curpath%\scl-installer

if exist %curpath%\scl-installer\scl-backend rmdir /s /q %curpath%\scl-installer\scl-backend
if exist %curpath%\scl-installer\scl-remote rmdir /s /q %curpath%\scl-installer\scl-remote

mkdir %curpath%\scl-installer\scl-backend
mkdir %curpath%\scl-installer\scl-remote


if not exist %curpath%\scl-winapp (
git clone -b development --single-branch https://scarsman@bitbucket.org/shortcut-lab/scl-winapp.git
cd %curpath%\scl-winapp
) else (
cd %curpath%\scl-winapp
git status -uno --porcelain | find /i "DB_Connect.py" && git add * && git commit -am "commit local changes" || echo "no changes"
git fetch origin development
git merge -s recursive -X theirs origin/development
)

:: download scl icon
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/scl.ico -o %temp%\scl.ico

:: download pyinstaller db_connect
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/pyinstaller-db-connect.py -o %temp%\DB_Connect.py

:: download syncthing bat 
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/syncthing.cmd -o %temp%\syncthing.cmd

:: download start_app.cmd
curl -s https://raw.githubusercontent.com/scarsman/advance-installer/master/start_app.cmd -o %temp%\start_app.cmd

:: copy pyinstaller db config
echo F | xcopy /S /Q /Y /F %temp%\DB_Connect.py scl_backend\scl_db

:: compile backend
:: need to chdir to main directory in order the exe will work
cd scl_backend
pyinstaller SCLExpress.py --onefile --noconsole --icon=%temp%\scl.ico
cd ..
:: compile frontend
set DEBUG=*
call electron-packager scl_interface\scl_app --platform=win32 --arch=x64 scl_appv1 --icon=%temp%\scl.ico --overwrite

echo F | xcopy /S /Q /Y /F scl_backend\dist\SCLExpress.exe %curpath%\scl-installer\scl-backend
echo F | xcopy /S /Q /Y /F scl_backend\scl_db\db\scldb8.db %curpath%\scl-installer\scl-backend
echo F | xcopy /S /Q /Y /F scl_backend\scl_db\db\SCL_FTI3.db %curpath%\scl-installer\scl-backend
echo F | xcopy /S /Q /Y /F %temp%\syncthing.cmd %curpath%\scl-installer\scl-backend
:: manually add tasks in scheduler; comment when running via advanced installer
echo F | xcopy /S /Q /Y /F %temp%\start_app.cmd %curpath%\scl-installer\scl-backend

:: copy frontend to installer folder
echo D | xcopy /S /Q /Y /F scl_appv1-win32-x64 %curpath%\scl-installer\scl_appv1-win32-x64

:: copy scl-remote to installer folder
echo D | xcopy /S /Q /Y /F scl_remote\INSTALL_FILES %curpath%\scl-installer\scl-remote

:: uninstall the package
::msiexec /x E:\SCL-Express-SetupFiles\SCL-Express.msi /qn /norestart
:: create msi package
::"C:\Program Files (x86)\Caphyon\Advanced Installer 15.7\bin\x86\AdvancedInstaller.com" /rebuild E:\SCL-Express.aip

:: install msi
::msiexec /i E:\SCL-Express-SetupFiles\SCL-Express.msi /qn /norestart

:: start task scheduled

call %curpath%\scl-installer\scl-backend\start_app.cmd

schtasks /run /tn "SCLBackend"
schtasks /run /tn "SCLRemote"
schtasks /run /tn "Syncthing"
