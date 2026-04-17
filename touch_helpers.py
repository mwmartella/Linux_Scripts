"""
Touch-friendly GUI helpers for FreeSimpleGUI on Linux tablets.

Provides touch_combo() — a fullscreen scrollable listbox popup that
replaces Combo dropdowns (which can't finger-scroll on Linux/Tk).

Also provides make_touch_combo_row() to build the Input + Select button
layout row, and handle_touch_combos() to wire up the events.
"""
import FreeSimpleGUI as sg


# ---------------------------------------------------------------------------
# Standalone popup selector (scrollable with finger)
# ---------------------------------------------------------------------------
def touch_combo(title, items, font=("Sans", 16, "bold"), size=(50, 12)):
    """
    Opens a popup with a scrollable listbox + optional filter box.
    Returns the selected item string, or None if cancelled.
    """
    layout = [
        [sg.Text(title, font=font)],
        [sg.Input('', key='-FILTER-', font=font, enable_events=True,
                  size=(size[0], 1), tooltip='Type to filter')],
        [sg.Listbox(items, key='-LIST-', font=font, size=size,
                    select_mode=sg.LISTBOX_SELECT_MODE_SINGLE,
                    enable_events=False, bind_return_key=True)],
        [sg.Button('OK', font=font, size=(12, 2), border_width=2),
         sg.Button('Cancel', font=font, size=(12, 2), border_width=2,
                   button_color=('white', 'firebrick3'))],
    ]
    window = sg.Window(title, layout, finalize=True, resizable=True,
                       modal=True, keep_on_top=True)
    window.Maximize()

    all_items = list(items)
    selected = None

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Cancel'):
            break

        if event == '-FILTER-':
            filter_text = values['-FILTER-'].lower()
            filtered = [i for i in all_items if filter_text in str(i).lower()]
            window['-LIST-'].update(filtered)

        if event == 'OK':
            if values['-LIST-']:
                selected = values['-LIST-'][0]
            break

    window.close()
    return selected


# ---------------------------------------------------------------------------
# Layout helpers — drop-in replacement for sg.Combo
# ---------------------------------------------------------------------------
SELECT_BTN_FONT = ("Sans", 14, "bold")
DISPLAY_FONT = ("Sans", 14, "bold")


def make_touch_combo_row(label, key, default='--Select--', display_size=30):
    """
    Returns a layout row: [ read-only Input | Select button ]
    Use in place of sg.Combo.

    key      — the key for the hidden Input that stores the value
    label    — text shown on the Select button, e.g. 'Select Worker'
    """
    return [
        sg.Input(default, key=key, font=DISPLAY_FONT, size=(display_size, 1),
                 readonly=True, disabled_readonly_background_color='#1a1a2e',
                 disabled_readonly_text_color='white'),
        sg.Button(label, key=f'_SELECT_{key}_', font=SELECT_BTN_FONT,
                  size=(16, 1), border_width=2),
    ]


def handle_touch_combos(event, window, combos_config):
    """
    Call this right after window.read(). Checks if a Select button was
    pressed and opens touch_combo for the matching config.

    combos_config: dict mapping key -> (popup_title, items_list)
        e.g. {'Field': ('Select Field', FieldList),
               'Worker': ('Select Worker', WorkerList)}

    Returns True if a combo event was handled (so you can skip/continue),
    False otherwise.
    """
    for key, (title, items) in combos_config.items():
        if event == f'_SELECT_{key}_':
            choice = touch_combo(title, items)
            if choice is not None:
                window[key].update(choice)
            return True
    return False


