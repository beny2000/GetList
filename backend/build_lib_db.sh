#!/bin/bash
version=$(awk -F"'" '/version/ {print $2}' ./lib_db_package/setup.py)
echo Building "lib-db-$version.tar.gz" package
tar -czvf "lib_db-$version.tar.gz" ./lib_db_package

