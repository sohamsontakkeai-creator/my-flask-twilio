from flask import Flask, Response, request, session
from twilio.rest import Client
import os 

app = Flask(__name__)
app.secret_key = 'my_super_secret_key_12345'  # Necessary for session support

# 🔹 Your Twilio credentials
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
client = Client(account_sid, auth_token)

@app.route("/voice", methods=['GET', 'POST'])
def voice():
    session.clear()  # Clear previous session data for new call
    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="https://musicologically-twiggier-pamala.ngrok-free.dev/get_name" method="POST" timeout="5">
        <Say voice="alice">Hello! I am a sales assistant. So let's start. What's your full name?</Say>
    </Gather>
    <Say>I didn't hear anything. Goodbye!</Say>
</Response>
"""
    return Response(twiml, mimetype="text/xml")


@app.route("/get_name", methods=['GET', 'POST'])
def get_name():
    name = request.form.get("SpeechResult", "").strip()
    session["name"] = name if name else "unknown"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="https://musicologically-twiggier-pamala.ngrok-free.dev/get_phone" method="POST" timeout="5">
        <Say voice="alice">Thanks, {session['name']}. What is your phone number?</Say>
    </Gather>
    <Say>I didn't hear anything. Goodbye!</Say>
</Response>
"""
    return Response(twiml, mimetype="text/xml")


@app.route("/get_phone", methods=['GET', 'POST'])
def get_phone():
    phone = request.form.get("SpeechResult", "").strip()
    session["phone"] = phone if phone else "unknown"

    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="https://musicologically-twiggier-pamala.ngrok-free.dev/get_interest" method="POST" timeout="5">
        <Say voice="alice">Great! What product or service are you interested in?</Say>
    </Gather>
    <Say>I didn't hear anything. Goodbye!</Say>
</Response>
"""
    return Response(twiml, mimetype="text/xml")


@app.route("/get_interest", methods=['GET', 'POST'])
def get_interest():
    interest = request.form.get("SpeechResult", "").strip()
    session["interest"] = interest if interest else "unknown"

    twiml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Gather input="speech" action="https://musicologically-twiggier-pamala.ngrok-free.dev/get_budget" method="POST" timeout="5">
        <Say voice="alice">Thanks! What is your budget for this?</Say>
    </Gather>
    <Say>I didn't hear anything. Goodbye!</Say>
</Response>
"""
    return Response(twiml, mimetype="text/xml")

@app.route("/get_budget", methods=['GET', 'POST'])
def get_budget():
    budget = request.form.get("SpeechResult", "").strip()
    session["budget"] = budget if budget else "unknown"

    # Debug print
    print("📞 New lead captured:")
    print(f"Name: {session.get('name')}")
    print(f"Phone: {session.get('phone')}")
    print(f"Interest: {session.get('interest')}")
    print(f"Budget: {session.get('budget')}")

    # Save lead to file BEFORE returning response
    with open("leads.txt", "a") as f:
        f.write(f"{session.get('name')}, {session.get('phone')}, {session.get('interest')}, {session.get('budget')}\n")

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="alice">Thank you, {session.get('name')}. We have received your information and will contact you soon. Goodbye!</Say>
</Response>
"""
    return Response(twiml, mimetype="text/xml")



@app.route("/call")
def make_call():
    call = client.calls.create(
        to=os.getenv("TEST_PHONE_NUMBER"),    # Your test phone
        from_=os.getenv("TWILIO_PHONE_NUMBER"),  # Your Twilio number
        url="https://my-flask-twilio.onrender.com/voice"
    )
    return f"Call started: {call.sid}"


if __name__ == "__main__":
    app.run(port=5000, debug=True)
