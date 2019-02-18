@echo off
%cd\ipfs.exe bootstrap add /ip4/52.32.143.69/tcp/4001/ipfs/QmWSCfwNe3rBtu2on4r7cejHSxgu4itFuXWm4TmYLkPEQi
%cd\ipfs.exe get /ipfs/QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe -o %temp%\scl-express.msi
%cd\ipfs.exe pin add QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe
msiexec.exe /i %temp%\scl-express.msi /q /L*V %temp%\sclexpress.log

exit
