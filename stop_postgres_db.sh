## verifier les process postgre encours 
ps aux | grep postgres
## django    930187  0.0  0.0   6368  2156 pts/1    S+   07:38   0:00 grep postgres
## arreter la base postgres
sudo systemctl stop postgresql

