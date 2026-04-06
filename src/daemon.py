from utils import ClipboardUtils as ClipU
from logic import ClipboardManager as ClipM
import time

def main():

    manager = ClipM()
    last_text = ClipU.get_content()

    try:
        while True:
            current_text = ClipU.get_content()
            if current_text and current_text != last_text:
                last_text = current_text
                result = manager.add_to_db(current_text)
                if result:
                    print("Save to DB!")
            time.sleep(1)
    except KeyboardInterrupt:
        print("Daemon stopped by user")

if __name__ == "__main__":
    main()