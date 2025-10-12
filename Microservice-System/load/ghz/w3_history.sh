#!/usr/bin/env bash
# History replay: 50 VUs stream List
PROTO=../../proto/gateway.proto
TARGET=0.0.0.0:50055


ghz \
--insecure \
--proto $PROTO \
--call gateway.v1.GatewayService.List \
--concurrency=50 \
--duration=30s \
--data '{"room_id":"general","from_offset":0,"limit":0}' \
$TARGET