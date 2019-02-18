@echo off

SET curr_dir="%~dp0"
cd %curr_dir%

ipfs.exe bootstrap add /ip4/52.32.143.69/tcp/4001/ipfs/QmWSCfwNe3rBtu2on4r7cejHSxgu4itFuXWm4TmYLkPEQi
ipfs.exe get /ipfs/QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe -o %temp%\scl-express.msi
ipfs.exe pin add QmPvtGa2bU2BPNax6tfgE5qbqePekaXdd4T3KbzpamgZwe

timeout 5

exit
