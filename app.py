from flask import Flask, request, jsonify, render_template
import os

app = Flask(__name__)

class AgentDavide:
    def __init__(self):
        self.steps = [
            {"q": "Hey! I'm Davide. What's your name?", "key": "name"},
            {"q": "Nice to meet you, {name}! Are you looking to **buy**, **sell**, or just **explore**?", "key": "goal", "options": ["buy", "sell", "explore"]},
            {"q": "Got it. When are you hoping to make this happen?", "key": "timeline"},
            {"q": "Ballpark — what’s your budget or target sale price?", "key": "budget"},
            {"q": "Which area are you focused on? (e.g. Pacific Heights, Marin)", "key": "area"},
        ]
        self.curiosity = [
            "Most people miss this one thing that saves $15k+…",
            "I see this mistake all the time — want me to show you?",
            "There’s a hidden opportunity in {area} right now…"
        ]

    def respond(self, user_input, state):
        step_idx = state.get("step", 0)
        data = state.get("data", {})
        msg_count = state.get("msg_count", 0) + 1
        state["msg_count"] = msg_count

        if msg_count >= 5:
            return {
                "message": f"*{data.get('name', 'Friend')}*, you're asking **all the right questions** — but this is too good for chat.\n\n"
                           f"Let’s jump on a **2-min call** and I’ll save you **$47k+**.\n\n"
                           f"**Call me now: (415) 349-0919**",
                "end": True,
                "force_call": True
            }

        if step_idx >= len(self.steps):
            return {
                "message": f"Alright {data.get('name', '')}, here’s the deal:\n"
                           f"Based on your {data.get('goal', '')} in {data.get('area', '')}...\n"
                           f"**most people overpay by $47k**.\n\n"
                           f"**Call me at (415) 349-0919** — 2 minutes, zero pressure.",
                "end": True
            }

        step = self.steps[step_idx]
        q = step["q"].format(**data) if "{name}" in step["q"] or "{area}" in step["q"] else step["q"]

        if user_input.strip():
            key = step["key"]
            data[key] = user_input.strip()
            state["data"] = data
            state["step"] = step_idx + 1

            if key in ["goal", "budget"] and msg_count < 5:
                curiosity = random.choice(self.curiosity)
                if "{area}" in curiosity and data.get("area"):
                    curiosity = curiosity.format(area=data["area"])
                q = f"*{curiosity}* Want me to show you?"

        return {
            "message": q,
            "options": step.get("options"),
            "step": state["step"],
            "data": data,
            "msg_count": msg_count
        }

agent = AgentDavide()
sessions = {}

@app.route("/")
def index():
    return render_template("chat.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id", "default")
    user_input = data.get("message", "")

    if session_id not in sessions:
        sessions[session_id] = {"step": 0, "data": {}, "msg_count": 0}

    response = agent.respond(user_input, sessions[session_id])
    sessions[session_id].update({
        "step": response.get("step", sessions[session_id]["step"]),
        "data": response.get("data", sessions[session_id]["data"]),
        "msg_count": response.get("msg_count", sessions[session_id].get("msg_count", 0))
    })

    return jsonify(response)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)  # But comment for prod
# Actually, comment the whole if block for gunicorn:
# if __name__ == "__main__":
#     app.run(debug=True)
