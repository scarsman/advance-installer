@echo off

#add bootstrap privatepeer
%1\ipfs.exe bootstrap add /ip4/52.32.143.69/tcp/4001/ipfs/QmWSCfwNe3rBtu2on4r7cejHSxgu4itFuXWm4TmYLkPEQi
#download the installer
%1\ipfs.exe get /ipfs/QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe -o $env:temp\scl-express.msi

%1\ipfs.exe pin add QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe

#install msi
msiexec.exe /i $env:temp\scl-express.msi /q /L*V $env:temp\sclexpress.log

exit
