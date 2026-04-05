#!/usr/bin/env zsh
# Configure FlClash override rules for TUN mode compatibility
# Adds DIRECT rules for SSH, Cloudflare Tunnel, and Tailscale
set -e

DB="$HOME/Library/Application Support/com.follow.clash/database.sqlite"

if [[ ! -f "$DB" ]]; then
  echo ">>> FlClash database not found, skipping"
  exit 0
fi

# Rules to prepend (bypassing TUN for specific traffic)
rules=(
  "PROCESS-NAME,ssh,DIRECT"
  "PROCESS-NAME,cloudflared,DIRECT"
  "DOMAIN-SUFFIX,argotunnel.com,DIRECT"
  "DOMAIN-SUFFIX,tailscale.com,DIRECT"
  "DOMAIN-SUFFIX,tailscale.io,DIRECT"
  "IP-CIDR,100.64.0.0/10,DIRECT,no-resolve"
  "IP-CIDR6,fd7a:115c:a1e0::/48,DIRECT,no-resolve"
)

echo ">>> Inserting FlClash override rules..."

# Insert rules (skip if already exists)
for i in {1..${#rules[@]}}; do
  rule="${rules[$i]}"
  existing=$(sqlite3 "$DB" "SELECT id FROM rules WHERE value='$rule';")
  if [[ -n "$existing" ]]; then
    echo "    $rule -> already exists (id=$existing), skipping"
  else
    sqlite3 "$DB" "INSERT INTO rules (id, value) VALUES ($i, '$rule');"
    echo "    $rule -> inserted (id=$i)"
  fi
done

# Link rules to all profiles
echo ">>> Linking rules to profiles..."
profiles=($(sqlite3 "$DB" "SELECT id FROM profiles;"))

for pid in "${profiles[@]}"; do
  label=$(sqlite3 "$DB" "SELECT label FROM profiles WHERE id=$pid;")
  for i in {1..${#rules[@]}}; do
    mapping_id="${pid}_added_${i}"
    existing=$(sqlite3 "$DB" "SELECT id FROM profile_rule_mapping WHERE id='$mapping_id';")
    if [[ -z "$existing" ]]; then
      sqlite3 "$DB" "INSERT INTO profile_rule_mapping (id, profile_id, rule_id, scene, \"order\") VALUES ('$mapping_id', $pid, $i, 'added', '$i');"
    fi
  done
  echo "    $label -> linked"
done

echo ">>> Done. Restart FlClash to apply."
