import subprocess

class ClipboardManager:
    """Tools for working with the system buffer"""

    @staticmethod
    def get_content() -> str:
        """Reads text from the clipboard"""
        try:    
            result = subprocess.run(['wl-paste'], capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else ""
        except Exception as e:
            return f"Error: {e}"

    @staticmethod
    def set_content(text: str):
        """Writes text to the clipboard"""
        try:
            subprocess.run(['wl-copy'], input=text, text=True, check=True)
        except Exception as e:
            return f"Error writing to clipboard: {e}"


