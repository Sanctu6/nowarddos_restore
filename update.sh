#!/bin/bash
cd "$( dirname "$1" )"
git clone "https://gitlab.com/a_gonda/nowarddos.git" "tmp" || exit 1
cd "$1"
docker-compose -f docker-compose.yml down
cd ..
rm -rf "$1"
mv "tmp" "$1"
cd "$1"
docker-compose -f docker-compose.yml up --build -d --scale attacker=$2