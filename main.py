import sys
import argparse
import logging
import subprocess
from logic import ClipboardManager
from prompt_toolkit.shortcuts import radiolist_dialog
from rich.text import Text

def format_entry(content, content_type):
    """Formatting based on content type"""
    if content_type == 'url':
        return f"[URL] {content}"
    elif content_type == 'color':
        return f"[COLOR] ■ {content}"
    return content

def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description="Smart Clipboard CLI")
    parser.add_argument("--add", action="store_true", help="Service flag for adding records via wl-paste")
    parser.add_argument("-s", "--search", type=str, help="Search by history entries")
    parser.add_argument("limit", type=int, nargs="?", default=10, help="Number of records to display")

    args = parser.parse_args()
    manager = ClipboardManager()

    if args.add:
        content = sys.stdin.read().strip()
        if content:
            if manager.add_to_db(content):
                logger.info("New content saved to DB.")
        sys.exit(0)

    else:
        history = manager.get_history(limit=args.limit)

        if not history:
            print("Clipboard history is empty.")
            sys.exit(0)

        menu_items = []
        for content, content_type, timestamp in history:
            if args.search and args.search.lower() not in content.lower():
                continue
            
            display_text = format_entry(content, content_type)

            menu_items.append([content, display_text])
        
        if not menu_items:
            print(f"Nothing found for '{args.search}'.")
            sys.exit(0)

        selected = radiolist_dialog(title="Smart Clipboard", text="Select the entry (Enter - copy, Esc - exit):", values=menu_items).run()

        if selected:
            manager.set_content(selected)
            print("Copied to clipboard!")

        if __name__ == "__main__":
            main()