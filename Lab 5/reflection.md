# Lab 5: Reflection

### 1. Which issues were the easiest to fix, and which were the hardest? Why?

**Easiest:** the Flake8 style issues and most Pylint conventions. Missing blank lines (E302), `== None` → `is None`, unused imports, `dict()` → `{}`, and missing docstrings each have one obvious mechanical fix, and the tool tells you the exact line. Renaming camelCase functions to snake_case was also easy because the file is self-contained.

**Hardest:** the security issues, because the tool only says *what* is wrong, not *what to replace it with*:
- **B413 (PyCrypto AES):** the warning points at the import, but the real problem was `MODE_ECB` with space padding, which made identical cards encrypt identically. The fix meant choosing a proper mode (AES-GCM) and handling a per-message nonce, not just swapping libraries.
- **Hardcoded secrets (B105):** removing the string is easy. Deciding where the secret comes from (environment variable) while keeping the demo runnable took more thought.
- **B702 (Mako):** the fix was either Mako's `|h` filter or dropping the template engine. I dropped it and used `html.escape`, which also removed a dependency.

The logic bugs (negative invoice, 4 retries instead of 3, full refund after 25 days, December crash in `next_billing_date`) were also hard. **No tool reported them.** I only found them by running the program and asking whether each output line made sense.

### 2. Did the static analysis tools report any false positives? If so, describe one example.

Yes, partially:
- **Bandit B413** flags `from Crypto.Cipher import AES` as "pyCrypto is no longer maintained". The installed package was actually **pycryptodome**, which is maintained and uses the same `Crypto` namespace. Bandit matches the import name, not the package. The *code* was still insecure because of ECB mode, so the finding led somewhere useful, but the stated reason was a false positive.
- **Bandit B101 (`assert`)** is often a false positive in test code, where asserts are expected. Here it was a real issue because the assert was doing input validation in production code.
- **Pylint I1101 (c-extension-no-member)** on `lxml.etree.fromstring` was noise: the function exists, Pylint just can't introspect the C extension.

The opposite also happened (false negatives): Bandit did **not** flag the `lxml` XML parsing or the timing-unsafe `==` comparison of HMAC signatures. I fixed those from manual review (`defusedxml`, `hmac.compare_digest`).

### 3. How would you integrate static analysis tools into your actual software development workflow?

- **Locally:** run Flake8 and Pylint on save through the editor (VS Code Python and Pylint extensions), and add a **pre-commit hook** (`pre-commit` framework) that runs `flake8`, `pylint --fail-under=9.5` and `bandit -r .` so bad code never reaches a commit.
- **In CI (GitHub Actions):** a job on every push and pull request that installs the tools and runs all three, failing the build if Bandit finds any Medium or High issue, Flake8 reports anything, or the Pylint score drops below a threshold. Reports can be uploaded as build artifacts so reviewers see them in the PR.
- **Configuration in the repo** (`.pylintrc` / `pyproject.toml`, `.flake8`, `.bandit`) so every developer and CI use the same rules, with any deliberate exceptions documented using inline `# nosec` / `# pylint: disable=` comments with a reason.
- Treat the tools as a **first pass, not a replacement for tests and review**: this lab showed that the most damaging bugs (wrong refund amounts, negative invoices) were invisible to all three tools, so unit tests for business logic are still needed.

### 4. What tangible improvements did you observe in the code quality, readability, or potential robustness after applying the fixes?

- **Measurable:** Pylint went from **4.43/10 → 10.00/10**, Bandit from **5 issues (1 High, 1 Medium) → 0**, and Flake8 from **36 violations → 0**.
- **Security:** card data now uses authenticated encryption with a random nonce, secrets are no longer in source control, the invoice HTML is escaped (the XSS payload in the demo now renders as text), webhook signatures use a constant-time comparison, and XML parsing is safe against entity-expansion attacks.
- **Robustness:** the `return`-in-`finally` that could silently swallow exceptions is gone. Validation uses real exceptions instead of `assert`. `next_billing_date` no longer crashes in December or on month-end dates. Importing the module no longer runs the demo.
- **Readability:** consistent snake_case names, a docstring on every function, lines that fit on screen, and literals/comprehensions instead of constructor calls make the file much easier to read and review.
- **Correctness:** the demo output is now sensible: the trial ends on day 14, the coupon works on its expiry day, invalid coupons are ignored instead of producing a negative invoice, payment is retried exactly 3 times, and the refund is prorated (166.5 instead of 999).
