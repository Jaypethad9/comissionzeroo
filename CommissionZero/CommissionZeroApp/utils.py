# utils.py
from twilio.rest import Client

def send_otp(phone_number, otp):
    account_sid = "ACcf7a5a7576f646b245a91c5b3bc51d5c"
    auth_token = "d797a61bcf6a0a69f56f365d81c6d9e3"
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        body=f"Your OTP for login is {otp}",
        from_="+447446917377",
        to=phone_number
    )
    return message.sid
