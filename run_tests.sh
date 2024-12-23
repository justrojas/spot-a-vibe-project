#!/bin/bash

case $1 in
  "analysis")
    PYTHONPATH=$PYTHONPATH:. python backend/tests/test_analysis.py
    ;;
  "historical") 
    PYTHONPATH=$PYTHONPATH:. python backend/tests/test_historical.py
    ;;
  *)
    echo "Usage: ./run_tests.sh [analysis|historical]"
    ;;
esac
