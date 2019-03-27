set curpath=%cd%
if exist %LOCALAPPDATA%\sclexpressdb ( rmdir /s /q %LOCALAPPDATA%\sclexpressdb )

mkdir %LOCALAPPDATA%\sclexpressdb

echo F | xcopy /S /Q /Y /F %curpath%\scldb8.db %LOCALAPPDATA%\sclexpressdb
echo F | xcopy /S /Q /Y /F %curpath%\SCL_FTI3.db %LOCALAPPDATA%\sclexpressdb

taskkill /F /IM  SCLExpress.exe
start "SCLBackend"  "%curpath%\SCLExpress.exe"
echo start "SCLBackend"  "%curpath%\SCLExpress.exe" > %curpath%\sclbackend.bat
schtasks /create /tn "SCLBackend" /tr "%curpath%\sclbackend.bat" /sc onlogon /F

echo start "SCLRemote"  "%curpath%\..\scl-remote\sclremote\SCLRemote.exe" > %curpath%\..\scl-remote\sclremote\sclremote.bat


type NUL > %curpath%\..\scl-remote\sclremote\config.ini
echo [info] >> %curpath%\..\scl-remote\sclremote\config.ini
echo username=%USERNAME% >>  %curpath%\..\scl-remote\sclremote\config.ini 


echo start "Syncthing" %curpath%\..\scl-remote\syncthing\syncthing.exe -no-console -no-browser > %curpath%\..\scl-remote\syncthing\syncthing.bat

schtasks /create /tn "SCLRemote" /tr "%curpath%\..\scl-remote\sclremote\sclremote.exe" /sc onlogon /F

schtasks /create /tn "Syncthing" /tr "%curpath%\..\scl-remote\syncthing\syncthing.bat" /sc onlogon /F

exit
