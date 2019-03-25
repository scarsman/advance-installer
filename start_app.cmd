set curpath="%cd%"


echo start "SCLBackend"  %curpath%\SCLExpress.exe > %curpath%\scl_backend.bat
start "SCLBackend"  %curpath%\SCLExpress.exe
schtasks /create /tn "SCLBackend" /tr %curpath%\SCLExpress.exe /sc onlogon

echo start "SCLRemote"  %curpath%\..\scl_remote\sclremote\SCLRemote.exe > %curpath%\..\scl_remote\sclremote\sclremote.bat


type NUL > %curpath%\..\scl_remote\sclremote\config.ini
echo [info] >> %curpath%\..\scl_remote\sclremote\config.ini
echo username=%USERNAME% >>  %curpath%\..\scl_remote\sclremote\config.ini 


echo start "Syncthing" %curpath%\..\scl_remote\syncthing\syncthing.exe -no-console -no-browser > %curpath%\..\scl_remote\syncthing\syncthing.bat

schtasks /create /tn "SCLRemote" /tr %curpath%\..\scl_remote\sclremote\sclremote.exe /sc onlogon

schtasks /create /tn "Syncthing" /tr %curpath%\..\scl_remote\syncthing\syncthing.bat /sc onlogon

exit
