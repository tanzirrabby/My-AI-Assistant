import streamlit as st
import os
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime


from roles import RoleManager
from memory import MemoryManager
from commands import CommandHandler

ASSISTANT_NAME = os.getenv("ASSISTANT_NAME", "Tanzir's-Assistant")


st.set_page_config(
    page_title=f"{ASSISTANT_NAME} - AI Assistant",
    page_icon="",
    layout="wide"
)


THEME = os.getenv("APP_THEME", "light")  

def _inject_theme_css(theme):
    if theme == "dark":
        user_bg = "#1f2937"  
        assistant_bg = "#111827"  
        text_color = "#ffffff"
        muted = "#9ca3af"
    else:
        user_bg = "#DCF8C6"
        assistant_bg = "#F1F0F7"
        text_color = "#000000"
        muted = "#666666"

    st.markdown(
        f"""
        <style>
        .chat-container{{max-width:900px;margin:10px auto;}}
        .bubble{{padding:12px 16px;border-radius:12px;margin:8px 0;display:inline-block;max-width:80%;}}
        .bubble.user{{background:{user_bg};color:{text_color};border-radius:12px 12px 0 12px;}}
        .bubble.assistant{{background:{assistant_bg};color:{text_color};border-radius:12px 12px 12px 0;}}
        .meta{{font-size:12px;color:{muted};margin-bottom:6px}}
        .sidebar-section{{margin-top:12px;padding-top:8px;border-top:1px solid #eee}}
        .model-card{{background:#fafafa;padding:8px;border-radius:8px;margin-top:6px}}
        .small-muted{{font-size:12px;color:{muted}}}
        </style>
        """,
        unsafe_allow_html=True,
    )

_inject_theme_css(THEME)


with st.container():
    hcol1, hcol2 = st.columns([4,1])
    with hcol1:
        st.markdown(f"# **{ASSISTANT_NAME}**  <span style='font-size:14px;color:gray'>A professional assistant UI</span>", unsafe_allow_html=True)
    with hcol2:
        st.markdown("<div style='text-align:right'><span style='font-size:18px;background:#eee;padding:8px;border-radius:50%;display:inline-block'></span></div>", unsafe_allow_html=True)
    st.markdown("---")



load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
client = None
api_available = False


def _save_api_key_to_env(key):
    return _save_setting_to_env("GROQ_API_KEY", key)


def _save_setting_to_env(k, v):
    try:
        env_path = ".env"
        lines = []
        if os.path.exists(env_path):
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        found = False
        for i, l in enumerate(lines):
            if l.strip().startswith(f"{k}="):
                lines[i] = f"{k}={v}\n"
                found = True
                break
        if not found:
            lines.append(f"{k}={v}\n")
        with open(env_path, "w", encoding="utf-8") as f:
            f.writelines(lines)
        return True, None
    except Exception as e:
        return False, str(e)


def _is_invalid_api_key(err):
    if not err:
        return False
    m = str(err).lower()
    return ("401" in m) or ("invalid api key" in m) or ("invalid_api_key" in m) or ("invalid key" in m) or ("unauthorized" in m)

if api_key:
    try:
        client = Groq(api_key=api_key)
        api_available = True
        st.session_state['api_init_error'] = None
    except Exception as e:
        
        st.session_state['api_init_error'] = str(e)
        
        if _is_invalid_api_key(e):
            st.session_state['invalid_api_key'] = True
        api_available = False
else:
    
    st.session_state['api_init_error'] = 'GROQ_API_KEY not present'
    api_available = False


memory = MemoryManager()


DEFAULT_MODEL_OPTIONS = [
    "llama-3.3-70b-versatile",  
    "llama-3.1-8b-instant",   
    "mixtral-8x7b-32768"       
]


RECOMMENDED_REPLACEMENTS = {
    "llama3-70b-8192": "llama-3.3-70b-versatile",
    "llama3-8b-8192": "llama-3.1-8b-instant",
}

# Start with defaults; we'll try to discover available models from the API below
MODEL_OPTIONS = DEFAULT_MODEL_OPTIONS.copy()

# Ensure we track decommissioned models in session state
if "decommissioned_models" not in st.session_state:
    st.session_state["decommissioned_models"] = []

# Load persisted preferred model (if saved to .env)
persisted_preferred = os.getenv("PREFERRED_MODEL")
if persisted_preferred:
    st.session_state.setdefault("preferred_model", persisted_preferred)

# Human-readable model descriptions
MODEL_DESCRIPTIONS = {
    "llama-3.3-70b-versatile": "Best for complex reasoning and long-form responses.",
    "llama-3.1-8b-instant": "Fast and cost-effective for short conversations.",
    "mixtral-8x7b-32768": "Good alternative for logic-heavy tasks."
}

# Attempt to discover available models from Groq (best-effort; non-fatal)
if api_available and client is not None:
    try:
        raw_models = None
        # Try common SDK method names
        if hasattr(client, "models") and hasattr(client.models, "list"):
            raw_models = client.models.list()
        elif hasattr(client, "list_models"):
            raw_models = client.list_models()
        elif hasattr(client, "get_models"):
            raw_models = client.get_models()
        elif hasattr(client, "available_models"):
            raw_models = client.available_models()

        discovered = []
        if raw_models is not None:
            # Normalize different response shapes
            if hasattr(raw_models, "data"):
                items = raw_models.data
            elif isinstance(raw_models, dict) and "data" in raw_models:
                items = raw_models["data"]
            else:
                items = raw_models

            for item in items:
                name = None
                decommissioned = False
                if isinstance(item, str):
                    name = item
                elif isinstance(item, dict):
                    name = item.get("name") or item.get("id") or item.get("model")
                    # Heuristics for decommissioned flag
                    decommissioned = bool(item.get("decommissioned") or (str(item.get("status", "")).lower() == "decommissioned") or ("decommissioned" in str(item.get("tags", [])).lower()))
                if name and not decommissioned:
                    discovered.append(name)

        if discovered:
            MODEL_OPTIONS = discovered
            st.session_state["available_models"] = MODEL_OPTIONS
            st.info(f"Loaded {len(MODEL_OPTIONS)} models from Groq")

            # If no preferred model is set, try to find a working model automatically
            def _test_model_candidate(candidate):
                try:
                    messages = [
                        {"role": "system", "content": "You are a concise assistant used only for a quick capability test."},
                        {"role": "user", "content": "Say 'ready' if you can respond."}
                    ]
                    resp = client.chat.completions.create(model=candidate, messages=messages, stream=False)
                    # Extract simple text
                    out = ""
                    if hasattr(resp, "choices"):
                        for c in resp.choices:
                            if hasattr(c, "message") and hasattr(c.message, "content"):
                                out += c.message.content
                            elif hasattr(c, "delta") and hasattr(c.delta, "content"):
                                out += c.delta.content
                            elif isinstance(c, dict):
                                out += c.get("message", {}).get("content", "") or c.get("text", "") or c.get("output", "")
                            else:
                                out += str(c)
                    elif isinstance(resp, dict):
                        out = resp.get("output") or resp.get("text") or str(resp)
                    else:
                        out = str(resp)

                    return bool(out and out.strip())
                except Exception:
                    return False

            if "preferred_model" not in st.session_state or not st.session_state.get("preferred_model"):
                # Candidate list - prefer our default order
                candidate_list = DEFAULT_MODEL_OPTIONS + [m for m in MODEL_OPTIONS if m not in DEFAULT_MODEL_OPTIONS]
                for cand in candidate_list:
                    if cand in MODEL_OPTIONS:
                        st.info(f"Testing candidate model: {cand}")
                        if _test_model_candidate(cand):
                            st.success(f"Auto-selected working model: {cand}")
                            st.session_state["preferred_model"] = cand
                            # Re-run so the selected model becomes the default in the UI
                            st.rerun()
                            break
    except Exception as e:
        # Non-fatal: show a small warning but continue with defaults
        st.warning(f"Could not fetch models list from Groq: {e}")

# 3. Sidebar - Settings
with st.sidebar:
    st.title("Control Panel")
    # Assistant Name (editable)
    new_name = st.text_input("Assistant name:", value=os.getenv("ASSISTANT_NAME", ASSISTANT_NAME))
    if st.button("Save Assistant Name"):
        ok, err = _save_setting_to_env("ASSISTANT_NAME", new_name)
        if ok:
            st.success("Assistant name saved. Reloading to apply...")
            st.rerun()
        else:
            st.error(f"Failed to save name: {err}")

    # Role Selection
    selected_role = st.selectbox(
        "Choose Personality:", 
        list(RoleManager.ROLES.keys())
    )

    st.sidebar.markdown("---")
    # Compact display toggle
    compact = st.checkbox("Compact chat view", value=False)
    # Save compact state
    st.session_state['compact_view'] = compact

    # Theme toggle
    theme_choice = st.radio("Theme:", ("light", "dark"), index=0 if THEME=="light" else 1)
    if theme_choice != THEME:
        ok, err = _save_setting_to_env("APP_THEME", theme_choice)
        if ok:
            st.success(f"Theme saved as {theme_choice}. Reloading to apply.")
            st.rerun()
        else:
            st.error(f"Failed to save theme: {err}")

    # Auto-select working model on startup
    auto_select = st.checkbox("Auto-select working model on startup", value=True)

    # Get Role Details
    role_info = RoleManager.get_role_details(selected_role)
    st.info(f"{role_info['icon']} **Active Mode:** {selected_role}")
    
    st.divider()
    
    # Model Selection (Groq offers these for free)
    # Ensure model_option exists with a safe default
    model_option = MODEL_OPTIONS[0] if MODEL_OPTIONS else None
    available_models = [m for m in MODEL_OPTIONS if m not in st.session_state.get("decommissioned_models", [])]
    if not available_models:
        st.warning("⚠️ No available models found. Please check Groq deprecations: https://console.groq.com/docs/deprecations")
        # Fallback to the first known option (won't be used for generation if client rejects it)
        model_option = MODEL_OPTIONS[0]
    else:
        # Use preferred_model from session state if present
        preferred = st.session_state.get("preferred_model")
        default_index = 0
        if preferred in available_models:
            default_index = available_models.index(preferred)
        model_option = st.selectbox(
            "Choose Model:",
            available_models,
            index=default_index,
        )

        # If a preferred model is set, show a control to persist it across restarts
        if st.button("Save preferred model as default"):
            ok, err = _save_setting_to_env("PREFERRED_MODEL", model_option)
            if ok:
                st.success(f"Preferred model '{model_option}' saved. Reload to apply.")
                st.rerun()
            else:
                st.error(f"Failed to save preferred model: {err}")

    # Show how many models we discovered (if discovery ran)
    if st.session_state.get("available_models"):
        st.caption(f"Loaded {len(st.session_state.get('available_models'))} models from Groq")

    # Show a small model info card
    model_desc = MODEL_DESCRIPTIONS.get(model_option, "")
    if model_desc:
        st.markdown(f"<div class='model-card'><strong>{model_option}</strong><br/><span class='small-muted'>{model_desc}</span></div>", unsafe_allow_html=True)
    # Show how many models we discovered (if discovery ran)
    if st.session_state.get("available_models"):
        st.caption(f"Loaded {len(st.session_state.get('available_models'))} models from Groq")
    
    if st.button("🗑️ Clear History"):
        memory.clear_memory()
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    if st.button("Refresh Models"):
        st.info("Refreshing available models from Groq…")
        st.rerun()

    # Show a subtle API status (non-intrusive)
    if not api_available:
        st.caption("Model generation is currently disabled (no API or client). Choose a detected model or refresh models.")
    else:
        st.caption("Model generation enabled")

# 4. Session State Management
if "messages" not in st.session_state:
    st.session_state.messages = memory.load_memory()

# 5. Display Chat History
left_col, right_col = st.columns([3,1])

with left_col:
    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
    compact_view = st.session_state.get('compact_view', False)
    for msg in st.session_state.messages:
        role = msg.get("role")
        content = msg.get("content")
        if role == "assistant":
            header = f"<div class='meta'><strong>{ASSISTANT_NAME}</strong></div>"
            bubble_class = "assistant"
        else:
            header = "<div class='meta'><strong>You</strong></div>"
            bubble_class = "user"
        timestamp = msg.get('time', '')
        timestamp_html = f"<div class='small-muted' style='margin-top:6px'>{timestamp}</div>" if timestamp else ""
        if compact_view:
            st.markdown(f"<div class='bubble {bubble_class}'>{content}{timestamp_html}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"{header}<div class='bubble {bubble_class}'>{content}</div>{timestamp_html}", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_col:
    # Settings and status
    st.markdown("### Session info")
    st.write(f"Messages: {len(st.session_state.messages)}")
    if st.session_state.get("available_models"):
        st.write("Detected models:")
        for m in st.session_state.get('available_models')[:5]:
            st.write(f"- {m}")
    else:
        st.write("No model discovery data yet.")

    st.markdown("---")
    st.markdown("### Settings & Storage")
    if st.button("Export session history"):
        import json
        st.download_button("Download JSON", json.dumps(st.session_state.messages, ensure_ascii=False, indent=2), file_name="session_history.json", mime="application/json")

    uploaded = st.file_uploader("Import session history (JSON)", type=["json"])
    if uploaded is not None:
        try:
            import json
            data = json.load(uploaded)
            if isinstance(data, list):
                st.session_state.messages = data
                st.success("Imported session history into current session.")
            else:
                st.error("Invalid format: expected a JSON array of messages.")
        except Exception as e:
            st.error(f"Failed to import: {e}")

    if st.button("Clear persisted preferred model"):
        ok, err = _save_setting_to_env("PREFERRED_MODEL", "")
        if ok:
            st.success("Cleared persisted preferred model. Reload to apply.")
            st.rerun()
        else:
            st.error(f"Failed to clear preferred model: {err}")


# 6. Main Chat Logic
if user_input := st.chat_input("Type a message or command..."):
    
    # Display User Message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    # A. Check for Commands first
    command_response = CommandHandler.check_command(user_input)
    
    if command_response:
        with st.chat_message("assistant"):
            st.markdown(f"*{command_response}*")
        st.session_state.messages.append({"role": "assistant", "content": command_response, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
    
    else:
        # B. Call Groq (Llama 3)
        if not api_available or client is None:
            with st.chat_message("assistant"):
                st.markdown("⚠️ Groq client not configured. Please add your GROQ_API_KEY in the sidebar or .env.")
            st.session_state.messages.append({"role": "assistant", "content": "Groq API not configured. Unable to generate assistant response.", "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
        else:
            try:
                # Prepare messages with System Prompt + History
                system_prompt = role_info["prompt"] + f" Your assistant name is {ASSISTANT_NAME}. When replying, identify as {ASSISTANT_NAME}."
                messages = [
                    {"role": "system", "content": system_prompt}
                ]
                # Add last 10 messages for context, but sanitize to remove unsupported metadata (e.g., 'time')
                history = st.session_state.messages[-10:]
                for m in history:
                    if not isinstance(m, dict):
                        continue
                    role = m.get("role")
                    content = m.get("content")
                    if role and content is not None:
                        messages.append({"role": role, "content": content})

                # Generate Stream
                stream = client.chat.completions.create(
                    model=model_option,
                    messages=messages,
                    stream=True
                )

                # Stream Output to UI
                with st.chat_message("assistant"):
                    response_container = st.empty()
                    full_response = ""

                    for chunk in stream:
                        content = chunk.choices[0].delta.content
                        if content:
                            full_response += content
                            response_container.markdown(full_response + "▌")

                    response_container.markdown(full_response)

                # Save to history
                st.session_state.messages.append({"role": "assistant", "content": full_response, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

            except Exception as e:
                # Detect Invalid API Key errors
                emsg = str(e)
                if _is_invalid_api_key(emsg):
                    friendly = ("The configured Groq API key appears to be invalid or unauthorized (401). Model generation is disabled until a valid key is provided. "
                                "Please update your GROQ_API_KEY in your environment or account settings.")
                    st.error(f"⚠️ {friendly}")
                    st.session_state['invalid_api_key'] = True
                    # Avoid saving raw traceback; add a short assistant message
                    st.session_state.messages.append({"role": "assistant", "content": friendly, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    # Disable further attempts
                    api_available = False
                # Detect Groq model deprecation / decommission errors
                elif ("model_decommissioned" in emsg) or ("decommissioned" in emsg.lower()) or ("has been decommissioned" in emsg.lower()):
                    # Try to extract model name from error message
                    model_name = None
                    for m in MODEL_OPTIONS:
                        if m in emsg:
                            model_name = m
                            break
                    # fallback pattern match for model-like tokens
                    if not model_name:
                        try:
                            import re
                            m = re.search(r"\b[a-z0-9-]+-\d+b-\d+\b", emsg, re.I)
                            if m:
                                model_name = m.group(0)
                        except Exception:
                            model_name = None

                    if model_name:
                        if model_name not in st.session_state["decommissioned_models"]:
                            st.session_state["decommissioned_models"].append(model_name)
                    # If we have a recommended replacement, try to use it
                    replacement = RECOMMENDED_REPLACEMENTS.get(model_name)
                    if replacement:
                        # Ensure replacement is in the options so it appears in the selector
                        if replacement not in MODEL_OPTIONS:
                            MODEL_OPTIONS.insert(0, replacement)
                        st.session_state["preferred_model"] = replacement
                        friendly = (f"The selected model `{model_name}` has been decommissioned. I recommended `{replacement}` as a replacement and selected it for you. "
                                    "Check https://console.groq.com/docs/deprecations for more options.")
                    else:
                        friendly = (f"The selected model `{model_name or 'selected model'}` has been decommissioned and was removed from the model list. "
                                    "Please choose another model or see https://console.groq.com/docs/deprecations for recommended replacements.")

                    st.error(f"⚠️ {friendly}")
                    # Append short assistant message (no raw traceback)
                    st.session_state.messages.append({"role": "assistant", "content": friendly, "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                    st.rerun()
                else:
                    st.error(f"⚠️ Error: {e}")

   
    try:
        memory.save_memory(st.session_state.messages)
    except Exception as e:
        st.error(f"Failed to save memory: {e}")