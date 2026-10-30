# Lab 5: Identified Issues: `billing_system.py`

Line numbers refer to the **original** file (see [reports/before/](reports/before/)).
Rows are ordered by severity: high and medium first, then low, then logic bugs that no tool reported.

## Security issues (Bandit + manual review)

| # | Issue | Type | Tool / Severity | Line(s) | Description | Fix Approach |
|---|-------|------|-----------------|---------|-------------|--------------|
| 1 | Deprecated crypto library + ECB mode | Security | Bandit B413 / **High** | 8, 72-74 | `Crypto.Cipher.AES` (PyCrypto API) is flagged as unmaintained. The card was also encrypted with `MODE_ECB` and space padding, so the same card always produced the same ciphertext ("Same card, same ciphertext? True") | Switched to `cryptography`'s `AESGCM` (authenticated encryption) with a random 12-byte nonce per call, stored as `nonce + ciphertext`. Same card now gives different ciphertext |
| 2 | XSS via Mako template | Security | Bandit B702 / **Medium** | 7, 86 | Mako renders `${user}` without escaping. The demo user `<b onmouseover=alert(1)>ravi</b>` was injected into the invoice HTML as-is | Removed Mako; escape `user` and `amount` with `html.escape()` and build the HTML with an f-string |
| 3 | Hardcoded secrets | Security | Bandit B105 / Low | 14-15 | Live webhook secret `whsec_live_...` and the card key are in source code, so anyone with repo access has them | Read from `BILLING_WEBHOOK_SECRET` / `BILLING_CARD_KEY` env vars; fall back to a random key generated with `secrets` / `AESGCM.generate_key` for the demo |
| 4 | Insecure random for coupon codes | Security | Bandit B311 / Low | 3, 67 | `random.choice` is a predictable PRNG, so coupon codes can be guessed | Use `secrets.choice` |
| 5 | `assert` used for validation | Security | Bandit B101 / Low | 85 | `assert amount >= 0` is stripped under `python -O`, so negative invoices pass silently | `if amount < 0: raise ValueError(...)` |
| 6 | Timing attack on signature check | Security | Manual | 78 | `expected == signature` returns early on the first differing byte, leaking the signature through timing | `hmac.compare_digest(expected, signature)` |
| 7 | XML parsing with lxml (XXE / billion laughs) | Security | Manual | 6, 81 | `lxml.etree.fromstring` on untrusted webhook bodies can be abused with entity expansion | Use `defusedxml.ElementTree.fromstring` |

## Code quality issues (Pylint)

| # | Issue | Type | Pylint code | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|---------|-------------|--------------|
| 8 | `return` in `finally` | Bug | W0150, W0134, E0601 | 60-64 | `return refund` in `finally` swallows any exception. `refund` could be unassigned (E0601), and the `print` after it is unreachable. Python 3.14 also raises a `SyntaxWarning` at import | Removed the pointless `try/finally`; compute and return the refund directly |
| 9 | Non-snake_case function names | Convention | C0103 | 24-84 (13 functions) | `isTrialOver`, `applyCoupon`, `invoiceAmount`, … break PEP 8 naming | Renamed to `is_trial_over`, `apply_coupon`, `invoice_amount`, etc. |
| 10 | Missing docstrings | Convention | C0114, C0116 | 1, all functions | No module or function documentation | Added a module docstring and a one-line docstring to every function |
| 11 | Unused imports | Warning | W0611 | 1 | `os` and `sys` imported but unused | Removed `sys`. `os` is now used to read secrets from the environment |
| 12 | Module-level `main()` call | Convention | n/a (design) | 108 | Importing the module ran the demo and mutated global state | Wrapped in `if __name__ == "__main__":` |
| 13 | `dict()` / `list()` / `set([...])` | Refactor | R1735, R1734, R1718, C0206 | 16, 21, 70 | Constructor calls where literals and comprehensions are clearer and faster | `{}`, `[]`, and `{user for user, sub in subscriptions.items() if ...}` |
| 14 | Redundant `u""` prefix, `%` formatting | Warning / Convention | W1406, C0209 | 86 | Python 2 leftovers | Plain f-string |

## Style issues (Flake8)

| # | Issue | Type | Flake8 code | Line(s) | Description | Fix Approach |
|---|-------|------|-------------|---------|-------------|--------------|
| 15 | Multiple imports on one line + unused | Style | E401, F401 | 1 | `import os, sys` | One import per line, unused removed |
| 16 | Missing blank lines | Style | E302, E305 | 20-107 (16 places) | Only one blank line between top-level functions | Two blank lines before and after each top-level definition |
| 17 | Comparison to `None` with `==` | Style / Bug | E711 (also Pylint C0121) | 29 | `coupon == None` can be fooled by a custom `__eq__` | `coupon is None` |
| 18 | Lines too long | Style | E501 (also Pylint C0301) | 21, 67, 70, 77, 86, 91-104 (15 lines) | Lines up to 126 chars, limit 79 | Wrapped calls and extracted constants (`COUPON_ALPHABET`) |

## Logic bugs found by running the program (not reported by any tool)

| # | Issue | Type | Line(s) | Description | Fix Approach |
|---|-------|------|---------|-------------|--------------|
| 19 | Negative invoice from FRIENDS150 | Bug | 18, 27-33 | 150% coupon made the invoice **-294.41** | `apply_coupon` ignores coupons whose percent is not in (0, 100] |
| 20 | Coupon rejected on its expiry day | Bug | 31 | `today >= expires` treated the last valid day as expired | `today > expires` |
| 21 | Trial off-by-one | Bug | 25 | 14-day trial from 09-01 still active on 09-15 (`> 14`) | `>= TRIAL_DAYS` |
| 22 | Too many payment retries | Bug | 52 | `while attempts <= MAX_ATTEMPTS` made **4** attempts with max 3 | `while attempts < MAX_ATTEMPTS` |
| 23 | Full refund regardless of usage | Bug | 58-64 | Refund after using 25 of 30 days was the full **999** | Refund `price * unused_days / period_days` (166.5) and mark the subscription `cancelled` |
| 24 | `next_billing_date` crashes | Bug | 41 | `month + 1` raises `ValueError` for December (month 13) and for 31st -> 30-day month | Roll over the year with `divmod` and clamp the day with `calendar.monthrange` |
| 25 | Proration uses fixed 30-day month | Bug | 48 | 10 days left in a 28-day February was charged as 10/30 | Divide by the actual days in the month (`calendar.monthrange`) |
| 26 | `today=None` crashes coupon check; float noise in money | Bug | 35-38 | `None >= date` raises `TypeError`; amounts printed as `588.8199999999999` | Default `today` to `date.today()`; round money to 2 decimals |
| 27 | Unknown plan accepted | Bug | 20-22 | `subscribe` stored any plan name, failing later with `KeyError` | Raise `ValueError` for unknown plans |

## Result

| Tool | Before | After |
|------|--------|-------|
| Pylint | **4.43/10** (46 messages) | **10.00/10** (0 messages) |
| Bandit | 5 issues (1 High, 1 Medium, 3 Low) | 0 issues |
| Flake8 | 36 violations | 0 violations |
