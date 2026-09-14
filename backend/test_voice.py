import os
from twilio.rest import Client

# ============================================================
# TWILIO CONFIGURATION
# ============================================================

ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_FROM = os.getenv("TWILIO_FROM")
CAREGIVER_PHONE = os.getenv("CAREGIVER_PHONE")

# ============================================================
# CHECK CONFIGURATION
# ============================================================

if not ACCOUNT_SID:
    raise RuntimeError("TWILIO_ACCOUNT_SID is not set")

if not AUTH_TOKEN:
    raise RuntimeError("TWILIO_AUTH_TOKEN is not set")

if not TWILIO_FROM:
    raise RuntimeError("TWILIO_FROM is not set")

if not CAREGIVER_PHONE:
    raise RuntimeError("CAREGIVER_PHONE is not set")

print("=" * 70)
print("SANJEEVANI AI - TWILIO PYTHON TEST")
print("=" * 70)

print("Account SID : configured")
print("From number : configured")
print("To number   : configured")

# ============================================================
# SEND SMS
# ============================================================

client = Client(ACCOUNT_SID, AUTH_TOKEN)

message = client.messages.create(
    body=(
        "🚨 SANJEEVANI AI TEST ALERT\n\n"
        "This is a test message from the Sanjeevani AI "
        "Level 2 caregiver notification system."
    ),
    from_=TWILIO_FROM,
    to=CAREGIVER_PHONE
)

print()
print("SMS SENT SUCCESSFULLY")
print("Message SID:", message.sid)
print("=" * 70)