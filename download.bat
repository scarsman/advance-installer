@echo off
SET curr_dir="%~dp0"
%curr_dir%\ipfs.exe bootstrap add /ip4/52.32.143.69/tcp/4001/ipfs/QmWSCfwNe3rBtu2on4r7cejHSxgu4itFuXWm4TmYLkPEQi
%curr_dir%\ipfs.exe get /ipfs/QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe -o %temp%\scl-express.msi
%curr_dir%\ipfs.exe pin add QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe
msiexec.exe /i %temp%\scl-express.msi /q /L*V %temp%\sclexpress.log

exit
