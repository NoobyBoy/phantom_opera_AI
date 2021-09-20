#!/bin/bash

phantom="src/phantom.py"
inspector="src/inspector.py"

if [[ $1 == "-h" ]]; then
  echo "Usage :"
  echo "   ./launch.sh [Option]"
  echo ""
  echo "  -h                              display information about the script"
  echo "  -i, --inspector [path]          change the default parameter for the path of inspector file by the precised one"
  echo "  -p, --phantom [path]            change the default parameter for the path of phantom file  by the precised one"
  echo "  -ri, --random_inspector         change the default parameter for the path of inspector by phantom_opera/random_inspector.py"
  echo "  -ri, --random_phantom           change the default parameter for the path of phantom by phantom_opera/random_phantom.py"
  echo ""
  exit 0
fi

if [ -z $1 ]; then
  python3 phantom_opera/server.py &
  sleep 0.5
  python3 src/inspector.py &
  sleep 0.5
  python3 src/phantom.py &
  wait
  echo ""
else

  until [ $# = 0 ]
  do
    if [[ $1 == "-p" ]] || [[ $1 == "--phantom" ]]; then
      shift
      phantom=$1
    fi
    if [[ $1 == "-ri" ]] || [[ $1 == "--random_inspector" ]]; then
      inspector="phantom_opera/random_inspector.py"
    fi
    if [[ $1 == "-rp" ]] || [[ $1 == "--random_phantom" ]]; then
      phantom="phantom_opera/random_fantom.py"
    fi
    shift
  done
  python3 phantom_opera/server.py &
  sleep 0.5
  python3 $inspector &
  sleep 0.5
  python3 $phantom &
  wait
  echo ""
fi
