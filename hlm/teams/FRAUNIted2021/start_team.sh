#!/bin/sh

HOST=localhost

./start $HOST ./ 1 &
sleep 1
./start $HOST ./ 2 &
./start $HOST ./ 3 &
./start $HOST ./ 4 &
./start $HOST ./ 5 &
sleep 1
./start $HOST ./ 6 &
./start $HOST ./ 7 &
./start $HOST ./ 8 &
sleep 1
./start $HOST ./ 9 &
./start $HOST ./ 10 &
./start $HOST ./ 11 &
sleep 1
./start $HOST ./ 12 &

