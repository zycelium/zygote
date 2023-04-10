#!/bin/sh

. .env

uvicorn --port 3965 zycelium.zygote.server:app
