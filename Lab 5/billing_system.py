"""Subscription billing system: trials, plans, coupons, proration,
payment retries, refunds, card encryption, webhooks and invoices."""

import os
import hmac
import html
import secrets
import hashlib
import calendar
from datetime import date
from defusedxml import ElementTree
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

PLANS = {"basic": 199, "pro": 499, "team": 999}
GST = 0.18
TRIAL_DAYS = 14
MAX_ATTEMPTS = 3
BILLING_CYCLE_DAYS = 30
WEBHOOK_SECRET = (os.environ.get("BILLING_WEBHOOK_SECRET")
                  or secrets.token_hex(32))
if "BILLING_CARD_KEY" in os.environ:
    CARD_KEY = bytes.fromhex(os.environ["BILLING_CARD_KEY"])
else:
    CARD_KEY = AESGCM.generate_key(bit_length=256)
COUPON_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
subscriptions = {}
coupons = {"WELCOME10": {"percent": 10, "expires": date(2026, 12, 31)},
           "FRIENDS150": {"percent": 150, "expires": date(2027, 1, 31)}}


def subscribe(user, plan, start):
    """Start a trial subscription for a user on the given plan."""
    if plan not in PLANS:
        raise ValueError(f"Unknown plan: {plan}")
    subscriptions[user] = {"plan": plan, "start": start,
                           "status": "trial", "invoices": []}
    return subscriptions[user]


def is_trial_over(user, today):
    """Return True if the user's free trial has ended by today."""
    return (today - subscriptions[user]["start"]).days >= TRIAL_DAYS


def apply_coupon(amount, code, today):
    """Apply a coupon discount to an amount if valid on today."""
    coupon = coupons.get(code)
    if coupon is None or not 0 < coupon["percent"] <= 100:
        return amount
    if today > coupon["expires"]:
        return amount
    return amount - amount * coupon["percent"] / 100


def invoice_amount(user, code=None, today=None):
    """Return the user's invoice total including GST and coupon."""
    if today is None:
        today = date.today()
    plan_price = PLANS[subscriptions[user]["plan"]]
    with_tax = plan_price * (1 + GST)
    return round(apply_coupon(with_tax, code, today), 2)


def next_billing_date(current):
    """Return the billing date one month after current."""
    year, month = divmod(current.month, 12)
    year, month = current.year + year, month + 1
    day = min(current.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def prorate_upgrade(user, new_plan, today, period_end):
    """Switch the user to new_plan and return the prorated charge."""
    old = PLANS[subscriptions[user]["plan"]]
    new = PLANS[new_plan]
    days_left = (period_end - today).days
    days_in_period = calendar.monthrange(today.year, today.month)[1]
    subscriptions[user]["plan"] = new_plan
    return round((new - old) * days_left / days_in_period, 2)


def retry_payment(charge):
    """Call charge until it succeeds; return the attempts made."""
    attempts = 0
    while attempts < MAX_ATTEMPTS:
        attempts += 1
        if charge():
            return attempts
    return attempts


def cancel_refund(user, days_used, period_days=BILLING_CYCLE_DAYS):
    """Cancel the subscription and return the refund for unused days."""
    price = PLANS[subscriptions[user]["plan"]]
    days_unused = max(period_days - days_used, 0)
    subscriptions[user]["status"] = "cancelled"
    return round(price * days_unused / period_days, 2)


def coupon_code():
    """Generate a random, unguessable coupon code."""
    return "SAVE-" + "".join(secrets.choice(COUPON_ALPHABET)
                             for _ in range(6))


def active_users():
    """Return the set of users with no invoices yet."""
    return {user for user, sub in subscriptions.items()
            if not sub["invoices"]}


def encrypt_card(card_number):
    """Encrypt a card number with AES-GCM; return nonce+ct as hex."""
    nonce = secrets.token_bytes(12)
    ciphertext = AESGCM(CARD_KEY).encrypt(nonce, card_number.encode(), None)
    return (nonce + ciphertext).hex()


def verify_webhook(body, signature):
    """Check a webhook body's HMAC-SHA256 signature."""
    expected = hmac.new(WEBHOOK_SECRET.encode(), body,
                        hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)


def parse_webhook(xml_bytes):
    """Parse a webhook XML payload into an event dict."""
    root = ElementTree.fromstring(xml_bytes)
    return {"event": root.findtext("event"), "user": root.findtext("user")}


def render_invoice(user, amount):
    """Render an HTML invoice with user input escaped."""
    if amount < 0:
        raise ValueError("Invoice amount cannot be negative")
    safe_user = html.escape(str(user))
    safe_amount = html.escape(str(amount))
    return f"<h1>Invoice for {safe_user}</h1><p>Total: Rs.{safe_amount}</p>"


def main():
    """Run a short demo of the billing system."""
    subscribe("asha", "pro", date(2026, 9, 1))
    subscribe("<b onmouseover=alert(1)>ravi</b>", "basic", date(2026, 9, 20))
    print("Trial (14 days from 09-01) over on 09-15?",
          is_trial_over("asha", date(2026, 9, 15)))
    print("Pro invoice with WELCOME10:",
          invoice_amount("asha", "WELCOME10", date(2026, 10, 1)))
    print("Pro invoice with FRIENDS150:",
          invoice_amount("asha", "FRIENDS150", date(2026, 10, 1)))
    print("Coupon on its expiry day:",
          invoice_amount("asha", "WELCOME10", date(2026, 12, 31)))
    print("Next billing after 2026-10-15:",
          next_billing_date(date(2026, 10, 15)))
    print("Next billing after 2027-01-31:",
          next_billing_date(date(2027, 1, 31)))
    print("Upgrade pro->team with 10 days left in Feb:",
          prorate_upgrade("asha", "team", date(2027, 2, 18),
                          date(2027, 2, 28)))
    calls = []
    print("Payment attempts (max 3, always failing):",
          retry_payment(lambda: calls.append(1) and False))
    print("Refund after using 25 of 30 days:", cancel_refund("asha", 25))
    print("Same card, same ciphertext?",
          encrypt_card("4111111111111111") == encrypt_card("4111111111111111"))
    sig = hmac.new(WEBHOOK_SECRET.encode(), b"<x/>",
                   hashlib.sha256).hexdigest()
    print("Webhook verified:", verify_webhook(b"<x/>", sig))
    print("Webhook:",
          parse_webhook(b"<hook><event>paid</event><user>asha</user></hook>"))
    print("Invoice HTML:",
          render_invoice("<b onmouseover=alert(1)>ravi</b>", 199))
    print("Coupon:", coupon_code())


if __name__ == "__main__":
    main()
