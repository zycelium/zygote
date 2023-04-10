#!/bin/sh

export QUART_APP="zycelium.zygote.server:app"
export QUART_ENV="development"
export QUART_DEBUG=0

quart run
