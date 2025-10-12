#!/usr/bin/env bash
# Steady chat: 100 VUs for 60s
PROTO=../../proto/gateway.proto
TARGET=0.0.0.0:50055


ghz \
--insecure \
--proto $PROTO \
--call gateway.v1.GatewayService.Append \
--concurrency=100 \
--duration=60s \
--data '{"room_id":"general","user_id":"u-load","text":"hi","idempotency_key":"__RANDOM__"}' \
$TARGET