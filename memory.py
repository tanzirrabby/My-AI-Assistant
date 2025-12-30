import json
import os

class MemoryManager:
    def __init__(self, file_path="chat_history.json"):
        self.file_path = file_path

    def load_memory(self):
        """Loads chat history from the local JSON file."""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def save_memory(self, messages):
        """Saves the current chat session to JSON."""
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=4, ensure_ascii=False)
            
    def clear_memory(self):
        """Wipes the history file."""
        if os.path.exists(self.file_path):
            os.remove(self.file_path)