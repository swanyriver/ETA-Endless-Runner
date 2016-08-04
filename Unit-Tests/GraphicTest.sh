#!/usr/bin/env bash
python ../graphicAssets.py
echo -e "\n\n Difference from Standard\n\n"
python ../graphicAssets.py | diff graphicsTestSample.txt -

