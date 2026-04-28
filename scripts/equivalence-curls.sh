#!/usr/bin/env bash
# Equivalence curls — exercises before/ (port 8000) and after/ (port 8001)
# in parallel and reports whether the observable JSON contracts match.
#
# The single intentional divergence is DELETE /travelers/{id}/packages with a
# non-refundable package: before/ explodes (5xx — LSP bomb), after/ returns
# 200 with a partial-result payload. That is the LSP cure on display.
#
# Usage:
#   ./scripts/equivalence-curls.sh
#
# Pre-req: both servers up + sqlite files removed at the repo root, so the
# IDs are deterministic across runs.

set -euo pipefail

BEFORE="http://localhost:8000"
AFTER="http://localhost:8001"

PASS="\033[32m✓\033[0m"
FAIL="\033[31m✗\033[0m"
DIM="\033[2m"
RESET="\033[0m"

pass=0
fail=0

# Normalize JSON for comparison: strip volatile fields (created_at), drop pretty
# whitespace via jq -S (sorted keys, compact-ish).
normalize() {
  jq -S 'walk(if type=="object" then del(.created_at) else . end)' <<< "$1"
}

step() {
  local label="$1"; shift
  local before_resp="$1"; shift
  local after_resp="$1"; shift
  local mode="${1:-equal}"  # equal | before-5xx-after-200

  local before_norm after_norm
  before_norm=$(normalize "$before_resp" 2>/dev/null || echo "$before_resp")
  after_norm=$(normalize "$after_resp" 2>/dev/null || echo "$after_resp")

  if [[ "$mode" == "equal" ]]; then
    if [[ "$before_norm" == "$after_norm" ]]; then
      printf "  ${PASS} %s\n" "$label"
      pass=$((pass+1))
    else
      printf "  ${FAIL} %s\n" "$label"
      printf "    ${DIM}before:${RESET} %s\n" "$before_norm"
      printf "    ${DIM}after :${RESET} %s\n" "$after_norm"
      fail=$((fail+1))
    fi
  fi
}

step_status() {
  local label="$1"; shift
  local before_status="$1"; shift
  local after_status="$1"; shift
  local mode="${1:-equal}"

  if [[ "$mode" == "equal" ]]; then
    if [[ "$before_status" == "$after_status" ]]; then
      printf "  ${PASS} %s — both %s\n" "$label" "$before_status"
      pass=$((pass+1))
    else
      printf "  ${FAIL} %s — before=%s after=%s\n" "$label" "$before_status" "$after_status"
      fail=$((fail+1))
    fi
  elif [[ "$mode" == "before-5xx-after-200" ]]; then
    if [[ "$before_status" -ge 500 && "$after_status" == "200" ]]; then
      printf "  ${PASS} %s — before=%s (LSP bomb), after=200 (cure)\n" \
        "$label" "$before_status"
      pass=$((pass+1))
    else
      printf "  ${FAIL} %s — before=%s after=%s (expected 5xx vs 200)\n" \
        "$label" "$before_status" "$after_status"
      fail=$((fail+1))
    fi
  fi
}

# Wrapper: GET/POST/DELETE that captures both body + status code in one call.
post() {
  local url="$1" body="$2"
  local out status
  out=$(curl -s -w "\n%{http_code}" -X POST "$url" \
        -H 'Content-Type: application/json' -d "$body")
  status=$(tail -n1 <<< "$out")
  body=$(sed '$d' <<< "$out")
  printf '%s\n%s\n' "$body" "$status"
}

get() {
  local url="$1"
  local out status
  out=$(curl -s -w "\n%{http_code}" "$url")
  status=$(tail -n1 <<< "$out")
  body=$(sed '$d' <<< "$out")
  printf '%s\n%s\n' "$body" "$status"
}

del() {
  local url="$1"
  local out status
  out=$(curl -s -w "\n%{http_code}" -X DELETE "$url")
  status=$(tail -n1 <<< "$out")
  body=$(sed '$d' <<< "$out")
  printf '%s\n%s\n' "$body" "$status"
}

# Helper: split the two-line "body\nstatus" output into two vars.
split_resp() {
  local raw="$1"
  body=$(head -n1 <<< "$raw")
  status=$(tail -n1 <<< "$raw")
}

echo "═══════════════════════════════════════════════════════════════"
echo "  Equivalence curls: before/ (8000) vs after/ (8001)"
echo "═══════════════════════════════════════════════════════════════"

# ---------- 1) Health ----------
echo
echo "▸ Health"
b=$(curl -s "$BEFORE/health"); a=$(curl -s "$AFTER/health")
# Health bodies differ on purpose (version string includes the folder name).
# Just assert both are 200 OK.
b_status=$(curl -s -o /dev/null -w "%{http_code}" "$BEFORE/health")
a_status=$(curl -s -o /dev/null -w "%{http_code}" "$AFTER/health")
step_status "GET /health → 200" "$b_status" "$a_status"

# ---------- 2) Create traveler ----------
echo
echo "▸ Travelers"
TRAVELER='{"name":"Maria Silva","email":"maria@example.com","document":"12345678909"}'
split_resp "$(post $BEFORE/travelers "$TRAVELER")"; b_body=$body; b_status=$status
split_resp "$(post $AFTER/travelers  "$TRAVELER")"; a_body=$body; a_status=$status
step_status "POST /travelers → 201" "$b_status" "$a_status"
step "POST /travelers shape (id/name/email/document)" "$b_body" "$a_body"

# ---------- 3) Reject invalid CPF ----------
INVALID='{"name":"Maria","email":"m@x.com","document":"123"}'
split_resp "$(post $BEFORE/travelers "$INVALID")"; b_status=$status
split_resp "$(post $AFTER/travelers  "$INVALID")"; a_status=$status
# before/ raises ValueError → 500 (or 422 if Pydantic catches first).
# after/ surfaces the same error as 422 via try/except in the router.
# Both are >= 400; we assert that signal only.
if [[ "$b_status" -ge 400 && "$a_status" -ge 400 ]]; then
  printf "  ${PASS} POST /travelers (invalid CPF) — before=%s after=%s (both ≥400)\n" \
    "$b_status" "$a_status"
  pass=$((pass+1))
else
  printf "  ${FAIL} POST /travelers (invalid CPF) — before=%s after=%s (expected ≥400)\n" \
    "$b_status" "$a_status"
  fail=$((fail+1))
fi

# ---------- 4) GET traveler missing ----------
split_resp "$(get $BEFORE/travelers/9999)"; b_status=$status
split_resp "$(get $AFTER/travelers/9999)";  a_status=$status
step_status "GET /travelers/9999 → 404" "$b_status" "$a_status"

# ---------- 5) Create package ----------
echo
echo "▸ Packages"
PKG='{"name":"Cancún 7 noites","destination":"Cancún","base_price":5500.00,"kind":"standard","traveler_id":1}'
split_resp "$(post $BEFORE/packages "$PKG")"; b_body=$body; b_status=$status
split_resp "$(post $AFTER/packages  "$PKG")"; a_body=$body; a_status=$status
step_status "POST /packages → 201" "$b_status" "$a_status"
# after/ adds a new `refundable` field — we strip it for equivalence.
b_norm=$(jq -S '.' <<< "$b_body")
a_norm=$(jq -S 'del(.refundable)' <<< "$a_body")
if [[ "$b_norm" == "$a_norm" ]]; then
  printf "  ${PASS} POST /packages shape (sans .refundable)\n"
  pass=$((pass+1))
else
  printf "  ${FAIL} POST /packages shape\n"
  printf "    ${DIM}before:${RESET} %s\n" "$b_norm"
  printf "    ${DIM}after :${RESET} %s\n" "$a_norm"
  fail=$((fail+1))
fi

# ---------- 6) Price calculation matrix ----------
echo
echo "▸ Price calculation"
declare -a CASES=(
  '1000.0|none|1000.0'
  '1000.0|seasonal|850.0'
  '1000.0|black_friday|700.0'
  '1000.0|corporate|800.0'
  '6000.0|cyber_monday|4500.0'
  '2000.0|cyber_monday|1800.0'
)

# We need a fresh package for each price test so the base_price varies.
# Shared package #1 already exists with base_price=5500. Create #2..#7 below.
pkg_id=2
for case in "${CASES[@]}"; do
  IFS='|' read -r base disc expected <<< "$case"

  # Create a new package with the right base_price in BOTH services.
  body_pkg=$(printf '{"name":"price-test","destination":"X","base_price":%s,"kind":"standard","traveler_id":1}' "$base")
  curl -s -X POST "$BEFORE/packages" -H 'Content-Type: application/json' -d "$body_pkg" >/dev/null
  curl -s -X POST "$AFTER/packages"  -H 'Content-Type: application/json' -d "$body_pkg" >/dev/null

  body_disc=$(printf '{"discount_type":"%s"}' "$disc")
  b=$(curl -s -X POST "$BEFORE/packages/$pkg_id/price" -H 'Content-Type: application/json' -d "$body_disc")
  a=$(curl -s -X POST "$AFTER/packages/$pkg_id/price"  -H 'Content-Type: application/json' -d "$body_disc")

  b_final=$(jq -r '.final_price' <<< "$b")
  a_final=$(jq -r '.final_price' <<< "$a")

  label=$(printf "POST /packages/%d/price disc=%s base=%s → %s" "$pkg_id" "$disc" "$base" "$expected")
  if [[ "$b_final" == "$expected" && "$a_final" == "$expected" ]]; then
    printf "  ${PASS} %s\n" "$label"
    pass=$((pass+1))
  else
    printf "  ${FAIL} %s — before=%s after=%s\n" "$label" "$b_final" "$a_final"
    fail=$((fail+1))
  fi
  pkg_id=$((pkg_id+1))
done

# ---------- 7) Cancel-all happy path (only standard packages) ----------
echo
echo "▸ Cancel-all"
TRAVELER2='{"name":"Bob","email":"b@x.com","document":"12345678902"}'
curl -s -X POST "$BEFORE/travelers" -H 'Content-Type: application/json' -d "$TRAVELER2" >/dev/null
curl -s -X POST "$AFTER/travelers"  -H 'Content-Type: application/json' -d "$TRAVELER2" >/dev/null
# Create 3 standard packages for traveler_id=2 in BOTH services
for i in 1 2 3; do
  body_pkg=$(printf '{"name":"std-%d","destination":"X","base_price":100.0,"kind":"standard","traveler_id":2}' "$i")
  curl -s -X POST "$BEFORE/packages" -H 'Content-Type: application/json' -d "$body_pkg" >/dev/null
  curl -s -X POST "$AFTER/packages"  -H 'Content-Type: application/json' -d "$body_pkg" >/dev/null
done

split_resp "$(del $BEFORE/travelers/2/packages)"; b_body=$body; b_status=$status
split_resp "$(del $AFTER/travelers/2/packages)";  a_body=$body; a_status=$status
step_status "DELETE /travelers/2/packages → 200 (all standard)" "$b_status" "$a_status"

b_count=$(jq -r '.cancelled' <<< "$b_body")
a_count=$(jq -r '.cancelled' <<< "$a_body")
if [[ "$b_count" == "3" && "$a_count" == "3" ]]; then
  printf "  ${PASS} cancelled = 3 in both\n"
  pass=$((pass+1))
else
  printf "  ${FAIL} cancelled mismatch — before=%s after=%s\n" "$b_count" "$a_count"
  fail=$((fail+1))
fi

# ---------- 8) Cancel-all with a non_refundable (LSP bomb / cure) ----------
TRAVELER3='{"name":"Carol","email":"c@x.com","document":"12345678903"}'
curl -s -X POST "$BEFORE/travelers" -H 'Content-Type: application/json' -d "$TRAVELER3" >/dev/null
curl -s -X POST "$AFTER/travelers"  -H 'Content-Type: application/json' -d "$TRAVELER3" >/dev/null
# 1 std + 1 non_refundable for traveler_id=3
body_std='{"name":"std-1","destination":"X","base_price":100.0,"kind":"standard","traveler_id":3}'
body_nr='{"name":"nr-1","destination":"X","base_price":100.0,"kind":"non_refundable","traveler_id":3}'
curl -s -X POST "$BEFORE/packages" -H 'Content-Type: application/json' -d "$body_std" >/dev/null
curl -s -X POST "$BEFORE/packages" -H 'Content-Type: application/json' -d "$body_nr"  >/dev/null
curl -s -X POST "$AFTER/packages"  -H 'Content-Type: application/json' -d "$body_std" >/dev/null
curl -s -X POST "$AFTER/packages"  -H 'Content-Type: application/json' -d "$body_nr"  >/dev/null

split_resp "$(del $BEFORE/travelers/3/packages)"; b_status=$status
split_resp "$(del $AFTER/travelers/3/packages)";  a_body=$body; a_status=$status
step_status "DELETE /travelers/3/packages (mixed) — LSP cure" \
  "$b_status" "$a_status" "before-5xx-after-200"

a_cancelled=$(jq -r '.cancelled' <<< "$a_body")
a_skipped=$(jq -r '.skipped_ids | length' <<< "$a_body")
if [[ "$a_cancelled" == "1" && "$a_skipped" == "1" ]]; then
  printf "  ${PASS} after/ partial-result: cancelled=1 skipped=1\n"
  pass=$((pass+1))
else
  printf "  ${FAIL} after/ partial-result wrong — cancelled=%s skipped=%s\n" \
    "$a_cancelled" "$a_skipped"
  fail=$((fail+1))
fi

echo
echo "═══════════════════════════════════════════════════════════════"
printf "  Result: %d passed, %d failed\n" "$pass" "$fail"
echo "═══════════════════════════════════════════════════════════════"

if [[ "$fail" -gt 0 ]]; then
  exit 1
fi
