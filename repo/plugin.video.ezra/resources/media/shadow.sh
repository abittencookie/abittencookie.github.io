#!/bin/bash
counter=0
until [ $counter -gt 250 ]
do
echo -n "System : "
read filename
convert "${filename}.png" \( +clone -background black -shadow 50x10+15+15 \) +swap -background none -layers merge +repage "${filename}.png"
 ((counter++))
done
