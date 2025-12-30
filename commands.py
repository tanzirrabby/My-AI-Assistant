import webbrowser
import os
import platform

class CommandHandler:
    @staticmethod
    def check_command(text):
        text = text.lower().strip()

        if "open google" in text:
            webbrowser.open("https://www.google.com")
            return "🔍 Opening Google..."

        elif "open youtube" in text:
            webbrowser.open("https://www.youtube.com")
            return "📺 Opening YouTube..."

        elif "open gmail" in text:
            webbrowser.open("https://mail.google.com")
            return "📧 Opening Gmail..."

        elif "email me" in text or "send email" in text:
            webbrowser.open(
                "mailto:tanzirrabby34383@gmail.com"
            )
            return "✉️ Opening email composer to your Gmail..."

        elif "open linkedin" in text:
            webbrowser.open("https://www.linkedin.com/in/tanzirrabby")
            return "💼 Opening your LinkedIn profile..."

        elif "open codeforces" in text:
            webbrowser.open("https://codeforces.com/profile/tanzirrabby34383")
            return "💻 Opening your Codeforces profile..."

        elif "open twitter" in text or "open x" in text:
            webbrowser.open("https://x.com/Tanzirabby")
            return "🐦 Opening your X (Twitter) profile..."

        elif "open notepad" in text:
            system_platform = platform.system()
            if system_platform == "Windows":
                os.system("notepad")
                return "📝 Opening Notepad..."
            elif system_platform == "Darwin":
                os.system("open -a TextEdit")
                return "📝 Opening TextEdit..."
            else:
                return "❌ Notepad command not supported on this OS."

        return None
