set curpath=%~dp0

type NUL > "%curpath%..\scl-remote\sclremote\config.ini"
echo [info] >> "%curpath%..\scl-remote\sclremote\config.ini"
echo username=%USERNAME% >>  "%curpath%..\scl-remote\sclremote\config.ini" 

exit


