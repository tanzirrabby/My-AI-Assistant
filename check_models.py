from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("GROQ_API_KEY not found in .env. Please add your key and retry.")
    raise SystemExit(1)

client = Groq(api_key=api_key)

print("Fetching available models from Groq...")
recommended = "llama-3.3-70b-versatile"
found = False
models = []

try:
    raw = None
    if hasattr(client, "models") and hasattr(client.models, "list"):
        raw = client.models.list()
    elif hasattr(client, "list_models"):
        raw = client.list_models()
    elif hasattr(client, "get_models"):
        raw = client.get_models()
    elif hasattr(client, "available_models"):
        raw = client.available_models()

    if raw is not None:
        if hasattr(raw, "data"):
            items = raw.data
        elif isinstance(raw, dict) and "data" in raw:
            items = raw["data"]
        else:
            items = raw

        for item in items:
            name = None
            if isinstance(item, str):
                name = item
            elif isinstance(item, dict):
                name = item.get("name") or item.get("id")
            if name:
                models.append(name)
                print(f"- {name}")
                if name == recommended:
                    found = True

    CANDIDATE_MODELS = [
        recommended,
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
        "mixtral-8x7b-32768"
    ]

    to_test = [m for m in CANDIDATE_MODELS if m in models] if models else CANDIDATE_MODELS

    if not to_test:
        print(
            f"\nNote: none of the candidate models were found in your account. "
            f"Found models: {', '.join(models) if models else 'none'}"
        )
    else:
        succeeded = False
        for candidate in to_test:
            print(f"\nTrying candidate model: {candidate} ...")
            try:
                messages = [
                    {"role": "system", "content": "You are a concise assistant."},
                    {"role": "user", "content": "Say hello and identify yourself briefly."}
                ]
                resp = client.chat.completions.create(
                    model=candidate,
                    messages=messages,
                    stream=False
                )

                out = ""
                if hasattr(resp, "choices"):
                    for c in resp.choices:
                        if hasattr(c, "message") and hasattr(c.message, "content"):
                            out += c.message.content
                        elif hasattr(c, "delta") and hasattr(c.delta, "content"):
                            out += c.delta.content
                        elif isinstance(c, dict):
                            out += (
                                c.get("message", {}).get("content", "")
                                or c.get("text", "")
                                or c.get("output", "")
                            )
                        else:
                            out += str(c)
                elif isinstance(resp, dict):
                    out = resp.get("output") or resp.get("text") or str(resp)
                else:
                    out = str(resp)

                if out and out.strip():
                    print(f"\nSuccess with {candidate}:\n")
                    print(out)
                    succeeded = True
                    break
                else:
                    print(f"{candidate} returned no usable output.")
            except Exception as e:
                print(f"{candidate} failed: {e}")

        if not succeeded:
            print(
                "\nNo candidate models produced a successful test completion. "
                "Consider checking account access or trying other models."
            )
except Exception as e:
    print(f"Error fetching models: {e}")
