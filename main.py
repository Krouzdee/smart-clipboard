import sys
import argparse
import logging

from logic import ClipboardManager


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

        all_items = []

        for content, content_type, timestamp in history:
            display_text = manager.format_entry(content, content_type)
            all_items.append((content, display_text))


        # --- Interface settings

        search_text = ""
        selected_index = 0        
        
        def get_filtered_items():
            if not search_text:
                return all_items
            return [(c, d) for c, d in all_items if search_text.lower() in c.lower()]


        # --- Creating Interface Components ---

        from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
        from prompt_toolkit.layout.containers import Window, HSplit
        from prompt_toolkit.buffer import Buffer


        search_buffer = Buffer()

        def on_search_change(_):
            nonlocal search_text, selected_index
            search_text = search_buffer.text
            selected_index = 0

            update_list_display()


        search_buffer.on_text_changed = on_search_change


        search_window = Window(content=BufferControl(buffer=search_buffer, focusable=True), height=1, style="class:search")

        list_control = FormattedTextControl(text="")
        list_window = Window(content=list_control)


        def update_list_display():
            items = get_filtered_items()

            if not items:
                list_control.text = [("class:dim", "No matches found")]
                return

            formatted_lines = []
            for i, (_, display) in enumerate(items):
                if i == selected_index:
                    formatted_lines.append(("ansigreen", "→ ")) 
                    formatted_lines.append(("ansigreen", display))
                else:
                    formatted_lines.append(("", "  "))
                    formatted_lines.append(("", display))
                
                # Перенос строки добавляется как отдельный элемент
                formatted_lines.append(("", "\n"))

            # Удаляем последний лишний перенос строки
            if formatted_lines:
                formatted_lines.pop()

            list_control.text = formatted_lines
                

        root_container = HSplit([search_window, list_window])

        # --- Key settings ---

        from prompt_toolkit.key_binding import KeyBindings
        from prompt_toolkit.keys import Keys


        kb = KeyBindings()

        @kb.add("down")
        def _(event):
            nonlocal selected_index
            items = get_filtered_items()
            if items:
                selected_index = (selected_index + 1) % len(items)
                update_list_display()
        
        @kb.add("up")
        def _(event):
            nonlocal selected_index
            items = get_filtered_items()
            if items:
                selected_index = (selected_index - 1) % len(items)
                update_list_display()

        @kb.add("enter")
        def _(event):
            nonlocal selected_index
            items = get_filtered_items()
            if items and selected_index < len(items):
                selected_content = items[selected_index][0]
                event.app.exit(result=selected_content)

        @kb.add("escape")
        def _(event):
            event.app.exit(result=None)



        # --- Launching the application ---

        from prompt_toolkit.layout import Layout
        from prompt_toolkit import Application

        layout = Layout(root_container, focused_element=search_window)

        app = Application(layout=layout, key_bindings=kb, full_screen=False, mouse_support=False, erase_when_done=True)

        if args.search:
            search_buffer.text = args.search
            on_search_change(None)

        update_list_display()

        result = app.run()


        if result:
            manager.set_content(result)
            print("Copied!")
