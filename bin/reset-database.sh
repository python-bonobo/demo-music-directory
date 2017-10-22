#! /bin/bash

echo "DROP DATABASE mused;"
echo "DROP ROLE mused;"
echo "CREATE ROLE mused WITH LOGIN PASSWORD 'mused';"
echo "CREATE DATABASE mused WITH OWNER=mused TEMPLATE=template0 ENCODING='utf-8';"
