from utils import ClipboardManager as ClipB
import time

def main():

    last_text = ClipB.get_content()

    try:
        while True:
            current_text = ClipB.get_content()
            if current_text and current_text != last_text:
                print("New!")
                last_text = current_text
            time.sleep(0.5)
    except KeyboardInterrupt:
        return "Daemon stopped by user"

if __name__ == "__main__":
    main()