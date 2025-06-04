#!/bin/sh
# Ensure strict permissions on critical files
umask 027
for f in config.yaml sbom.json sealed_aes_key.bin context_key.ctx; do
    [ -f "$f" ] && chmod 600 "$f"
done
