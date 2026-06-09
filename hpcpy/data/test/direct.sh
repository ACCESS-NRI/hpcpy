#!/bin/bash

echo "PID is $$"
echo "Running...."

# for ((initialization; condition; increment))
for ((i=1; i<=5; i++))
do
    echo "Counter: $i"
    echo "Sleeping for 10s"
    sleep 10
done