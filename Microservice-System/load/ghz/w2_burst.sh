#!/usr/bin/env bash
# Bursty: 200 VUs for 15s
PROTO=../../proto/gateway.proto
TARGET=0.0.0.0:50055


ghz \
--insecure \
--proto $PROTO \
--call gateway.v1.GatewayService.Append \
--concurrency=200 \
--duration=15s \
--data '{"room_id":"general","user_id":"u-burst","text":"boom","idempotency_key":"__UUID__"}' \
$TARGET