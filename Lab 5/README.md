# Lab 5: Static Code Analysis — Subscription Billing System

**Your file:** `billing_system.py`
**Python:** 3.10 or newer

Follow the lab handout for the full instructions.

## About the program

A SaaS subscription billing system. It handles free trials and plan subscriptions, coupons, billing dates, upgrade proration, payment retries and refunds, encrypts card numbers, verifies signed XML webhooks and renders HTML invoices.

The code works, but only just. It has quality, style and security problems of the kind Pylint, Flake8 and Bandit are built to find.

## What to do

1. **Run it first** and read the output carefully:
   ```bash
   python billing_system.py
   ```
   It runs a short built-in demo and prints the results; it does not ask for input. Read every line and ask whether a sensible program would print that. Not every problem in this file is something a tool will flag, so pay attention to output that looks wrong.

2. **Install the tools:**
   ```bash
   python -m pip install pylint bandit flake8 lxml mako pycryptodome
   ```
   `lxml`, `mako` and `pycryptodome` are installed as well because the program imports them; without them it stops with `ModuleNotFoundError`. If you fix the XML parsing or encryption issues with `defusedxml` or `cryptography`, install those too: `python -m pip install defusedxml cryptography`.

3. **Run the analysis** and save the reports:
   ```bash
   python -m pylint billing_system.py > pylint_report.txt
   python -m bandit -r billing_system.py > bandit_report.txt
   python -m flake8 billing_system.py > flake8_report.txt
   ```
   Use the `python -m` form: it works everywhere, including Windows where a bare `pylint` is often "not recognized". The tools exit with a non-zero status whenever they find issues; that is expected, not an error. In Windows PowerShell 5.1, `>` saves files as UTF-16; if a report looks garbled, use `python -m pylint billing_system.py | Out-File -Encoding utf8 pylint_report.txt` instead.

4. **Document the issues** in `issues.md` using this table (at least 4 rows, high and medium severity first):

   | Issue | Type | Line(s) | Description | Fix Approach |
   |-------|------|---------|-------------|--------------|
   | ... | ... | ... | ... | ... |

5. **Fix the code.** Fix at least 4 of the issues you documented, then rerun all three tools to confirm they are gone. Repeat until you are satisfied. The program should still do its job when you are done.

6. **Reflect.** Answer the four reflection questions from the handout in `reflection.md`.

## Deliverables

1. `billing_system.py`: your cleaned version, with at least 4 issues fixed.
2. `issues.md`: the completed issue table.
3. `reflection.md`: your answers to the reflection questions.

**Target:** aim for a Pylint score above 9.5 on your final file. A perfect 10.00/10 is very good.

Be ready to explain the bugs you found and how you fixed them. You may be called on to present.

---

## Work Done (PES1UG24CS909)

### Results

| Tool | Before | After |
|------|--------|-------|
| Pylint | **4.43/10** | **10.00/10** |
| Bandit | 5 issues (1 High, 1 Medium, 3 Low) | **0 issues** |
| Flake8 | 36 violations | **0 violations** (empty report) |

### Commits

| Commit | Change |
|--------|--------|
| `30b11c4` | Original `billing_system.py` + before reports |
| `aa27ba6` | **Bandit:** fix all security issues (AES-GCM via `cryptography`, secrets from env, `secrets` module, HTML escaping instead of Mako, no `assert`, `defusedxml`, `hmac.compare_digest`) |
| `a0b06ed` | **Flake8:** fix all style/formatting issues |
| `9d8f02d` | **Pylint:** fix code quality issues (naming, docstrings, return-in-finally, literals, `__main__` guard). Score 10.00/10 |
| `6c1a191` | Fix logic bugs found by running the program that no tool reported (negative invoice, retry count, refund, billing date, proration, trial/expiry off-by-one) |

### Deliverables

| File | Contents |
|------|----------|
| [billing_system.py](billing_system.py) | Cleaned and fixed program |
| [issues.md](issues.md) | Issue table (27 issues: type, lines, description, fix) |
| [reflection.md](reflection.md) | Answers to the reflection questions |
| [reports/before/](reports/before/) | `pylint_report.txt`, `bandit_report.txt`, `flake8_report.txt` on the original code |
| [reports/after/](reports/after/) | The same three reports on the fixed code |

### Running

```bash
python -m venv venv
venv\Scripts\activate            # Windows  (source venv/bin/activate on Linux/macOS)
python -m pip install -r requirements.txt
python billing_system.py
```

Optional: set `BILLING_WEBHOOK_SECRET` (string) and `BILLING_CARD_KEY` (64 hex chars = 256-bit key). If unset, a random key is generated for each run.

### Program output after fixes

```
Trial (14 days from 09-01) over on 09-15? True
Pro invoice with WELCOME10: 529.94
Pro invoice with FRIENDS150: 588.82
Coupon on its expiry day: 529.94
Next billing after 2026-10-15: 2026-11-15
Next billing after 2027-01-31: 2027-02-28
Upgrade pro->team with 10 days left in Feb: 178.57
Payment attempts (max 3, always failing): 3
Refund after using 25 of 30 days: 166.5
Same card, same ciphertext? False
Webhook verified: True
Webhook: {'event': 'paid', 'user': 'asha'}
Invoice HTML: <h1>Invoice for &lt;b onmouseover=alert(1)&gt;ravi&lt;/b&gt;</h1><p>Total: Rs.199</p>
Coupon: SAVE-XXXXXX   (random each run)
```
