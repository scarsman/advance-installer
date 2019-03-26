set curpath="%cd%"


start "SCLBackend"  %curpath%\SCLExpress.exe
schtasks /create /tn "SCLBackend" /tr %curpath%\SCLExpress.exe /sc onlogon

echo start "SCLRemote"  %curpath%\..\scl-remote\sclremote\SCLRemote.exe > %curpath%\..\scl-remote\sclremote\sclremote.bat


type NUL > %curpath%\..\scl-remote\sclremote\config.ini
echo [info] >> %curpath%\..\scl-remote\sclremote\config.ini
echo username=%USERNAME% >>  %curpath%\..\scl-remote\sclremote\config.ini 


echo start "Syncthing" %curpath%\..\scl-remote\syncthing\syncthing.exe -no-console -no-browser > %curpath%\..\scl-remote\syncthing\syncthing.bat

schtasks /create /tn "SCLRemote" /tr %curpath%\..\scl-remote\sclremote\sclremote.exe /sc onlogon

schtasks /create /tn "Syncthing" /tr %curpath%\..\scl-remote\syncthing\syncthing.bat /sc onlogon

exit
