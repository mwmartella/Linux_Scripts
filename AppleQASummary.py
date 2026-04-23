"""
Apple QA Daily Summary
Standalone program – shows a per-worker breakdown of all QA defect stats
for a selected Block (Field) and date.
"""

import platform
import datetime
import sqlite3
import re

import pandas as pd
import FreeSimpleGUI as sg
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────
BASE_PATH  = str(Path.home() / 'OneDrive' / '~FARM DATA' / 'Timesheet App') + '/'
CompName   = platform.node()

TITLE_FONT  = ("Sans", 22, "bold")
HEADER_FONT = ("Sans", 16, "bold")
BTN_FONT    = ("Sans", 14, "bold")
BTN_SIZE    = (20, 2)
BTN_PAD     = (8, 5)
TABLE_FONT  = ("Sans", 12, "bold")
STAT_FONT   = ("Sans", 13, "bold")
WARN_FONT   = ("Sans", 18, "bold")

btn_kwargs  = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
back_kwargs = dict(font=BTN_FONT, size=(12, 1), pad=BTN_PAD,
                   button_color=('white', 'firebrick3'), border_width=2)

QA_COLS = [
    "Super_ID", "TimeStamp", "CheckID", "FruitChecked",
    "BruiseOld", "BruiseNew", "Sunburn", "Colour", "Hail", "Insect", "MiscDamage",
    "Variety", "Block"
]

DEFECT_COLS = ["BruiseOld", "BruiseNew", "Sunburn", "Colour", "Hail", "Insect", "MiscDamage"]
DEFECT_LABELS = {
    "BruiseOld":   "Bruise Old",
    "BruiseNew":   "Bruise New",
    "Sunburn":     "Sunburn",
    "Colour":      "Colour",
    "Hail":        "Hail",
    "Insect":      "Insect",
    "MiscDamage":  "Misc Damage",
}

sg.theme('DarkBlue3')


def _colour_for(value, lower, upper):
    if value <= lower:
        return 'lime green'
    if value <= upper:
        return 'yellow'
    return 'tomato2'


def _centred_window(inner, title='Apple QA Summary'):
    layout = [
        [sg.VPush()],
        [sg.Push(), sg.Column(inner, element_justification='c'), sg.Push()],
        [sg.VPush()],
    ]
    w = sg.Window(title, layout, finalize=True, resizable=True)
    w.Maximize()
    return w


def _load_qa_variables():
    """Return (defect_lower, defect_upper) from HarvestQAVariables.xlsx, or (5, 10) as defaults."""
    try:
        vars_df = pd.read_excel(BASE_PATH + 'WORKER DATA/HarvestQAVariables.xlsx')
        def _var(cls):
            row = vars_df.loc[vars_df['Class'] == cls]
            return float(row['Variable'].tolist()[0]) if len(row) else 0.0
        return _var('Defect Lower Limit'), _var('Defect Upper Limit')
    except Exception:
        return 5.0, 10.0


def _pct(value, total):
    try:
        return round(value / total * 100, 1) if total > 0 else 0.0
    except Exception:
        return 0.0


def AppleQASummary():
    defect_lower, defect_upper = _load_qa_variables()

    # ── Connect to QA DB ───────────────────────────────────────────────────
    qa_db_path = BASE_PATH + f'{CompName} AppleLog.db'
    try:
        conn   = sqlite3.connect(qa_db_path)
        cursor = conn.cursor()
        cursor.execute(
            f"CREATE TABLE IF NOT EXISTS QA "
            f"({', '.join([c + ' TEXT' for c in QA_COLS])})"
        )
        conn.commit()
    except Exception as e:
        sg.popup_error(f'Could not open QA database:\n{e}', title='QA Summary Error', font=WARN_FONT)
        return

    # ── DATE PICKER SCREEN ─────────────────────────────────────────────────
    today_str = datetime.datetime.today().strftime('%Y-%m-%d')

    # Pull available dates from DB
    try:
        raw_dates = cursor.execute(
            "SELECT DISTINCT substr(TimeStamp, 1, 10) FROM QA ORDER BY TimeStamp DESC"
        ).fetchall()
        date_list = [r[0] for r in raw_dates if r[0]]
    except Exception:
        date_list = []

    if not date_list:
        date_list = [today_str]

    layout = [
        [sg.Text('Apple QA Daily Summary', font=TITLE_FONT)],
        [sg.Text('Select Date', font=HEADER_FONT)],
        [sg.Listbox(values=date_list, default_values=[date_list[0]],
                    size=(20, min(len(date_list), 10)),
                    font=TABLE_FONT, key='-DATE-', select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)],
        [sg.Button('NEXT', **btn_kwargs), sg.Button('QUIT', **back_kwargs)],
    ]
    win = _centred_window(layout)
    ev, vals = win.read()
    win.close()
    if ev in (sg.WIN_CLOSED, 'QUIT'):
        conn.close()
        return

    selected_dates = vals.get('-DATE-', [])
    selected_date  = selected_dates[0] if selected_dates else today_str

    # ── Load all QA rows for the selected date ─────────────────────────────
    try:
        raw = cursor.execute("SELECT * FROM QA").fetchall()
        qa_df = pd.DataFrame(raw, columns=QA_COLS)
        qa_df = qa_df[qa_df['TimeStamp'].str.contains(selected_date, na=False)]
        for col in ['FruitChecked'] + DEFECT_COLS:
            qa_df[col] = pd.to_numeric(qa_df[col], errors='coerce').fillna(0)
    except Exception as e:
        sg.popup_error(f'Failed to load QA data:\n{e}', title='QA Summary Error', font=WARN_FONT)
        conn.close()
        return

    if qa_df.empty:
        sg.popup(f'No QA records found for {selected_date}.', title='QA Summary', font=WARN_FONT)
        conn.close()
        return

    # CheckID is stored as "{WorkerName}{YYYYMMDD}{BinNumber}" — strip the date+bin suffix
    # so we can group by actual worker name.
    qa_df['Worker'] = qa_df['CheckID'].str.replace(r'\d{8,}.*$', '', regex=True).str.strip()

    # ── BLOCK SELECTION SCREEN ─────────────────────────────────────────────
    while True:
        blocks = sorted(qa_df['Block'].dropna().unique().tolist())
        if not blocks:
            sg.popup('No blocks found in QA data.', title='QA Summary', font=WARN_FONT)
            conn.close()
            return

        layout = [
            [sg.Text('Apple QA Daily Summary', font=TITLE_FONT)],
            [sg.Text(f'Date: {selected_date}', font=HEADER_FONT)],
            [sg.Text('Select Block / Field', font=HEADER_FONT)],
            [sg.Listbox(values=blocks, size=(30, min(len(blocks), 10)),
                        font=TABLE_FONT, key='-BLOCK-',
                        select_mode=sg.LISTBOX_SELECT_MODE_SINGLE)],
            [sg.Button('VIEW SUMMARY', **btn_kwargs), sg.Button('BACK', **back_kwargs)],
        ]
        win = _centred_window(layout)
        ev, vals = win.read()
        win.close()
        if ev in (sg.WIN_CLOSED, 'BACK'):
            conn.close()
            return

        selected_blocks = vals.get('-BLOCK-', [])
        if not selected_blocks:
            sg.popup('Please select a block.', title='QA Summary', font=BTN_FONT)
            continue
        selected_block = selected_blocks[0]
        break

    # ── Filter to selected block ───────────────────────────────────────────
    block_df = qa_df[qa_df['Block'] == selected_block].copy()

    # ── BUILD SUMMARY SCREEN ───────────────────────────────────────────────
    # Overall totals row
    total_fruit = block_df['FruitChecked'].sum()
    total_checks = len(block_df)
    overall = {}
    for col in DEFECT_COLS:
        overall[col] = _pct(block_df[col].sum(), total_fruit)

    # Per-worker breakdown — full day totals (all blocks), one row per worker
    workers = sorted(qa_df['Worker'].dropna().unique().tolist())

    # Table: columns = Worker | Checks | Fruit | BruiseOld% | BruiseNew% | Sunburn% | Colour% | Hail% | Insect% | MiscDmg%
    headings = ['Worker', 'Checks', 'Fruit'] + [DEFECT_LABELS[c] for c in DEFECT_COLS]

    table_rows = []
    for worker in workers:
        w_df    = qa_df[qa_df['Worker'] == worker]   # all bins for this worker, full day
        w_fruit = w_df['FruitChecked'].sum()
        w_chks  = len(w_df)
        row = [worker, w_chks, int(w_fruit)]
        for col in DEFECT_COLS:
            row.append(f"{_pct(w_df[col].sum(), w_fruit)}%")
        table_rows.append(row)

    # Overall total row for the full day
    day_fruit  = qa_df['FruitChecked'].sum()
    day_checks = len(qa_df)
    overall_row = ['— DAY TOTAL —', day_checks, int(day_fruit)]
    for col in DEFECT_COLS:
        overall_row.append(f"{_pct(qa_df[col].sum(), day_fruit)}%")
    table_rows.append(overall_row)

    # Colour-coded overall bar
    stat_rows = []
    for col in DEFECT_COLS:
        pct   = overall[col]
        colour = _colour_for(pct, defect_lower, defect_upper)
        stat_rows.append(
            sg.Text(f'{DEFECT_LABELS[col]}: {pct}%', font=STAT_FONT, text_color=colour, pad=(12, 3))
        )

    # Split stat_rows into pairs for a two-column display
    stat_layout = []
    for i in range(0, len(stat_rows), 2):
        pair = stat_rows[i:i+2]
        stat_layout.append(pair)

    # ── Detail rows for the "View Checks" screen ──────────────────────────
    detail_headings = ['Timestamp', 'Worker', 'Check ID', 'Fruit'] + [DEFECT_LABELS[c] for c in DEFECT_COLS]
    detail_rows = []
    for _, r in block_df.sort_values('TimeStamp').iterrows():
        row = [r['TimeStamp'], r['Worker'], r['CheckID'], int(r['FruitChecked'])]
        for col in DEFECT_COLS:
            row.append(int(r[col]))
        detail_rows.append(row)

    while True:
        layout = [
            [sg.Text('Apple QA Daily Summary', font=TITLE_FONT)],
            [sg.Text(f'Block: {selected_block}   |   Date: {selected_date}', font=HEADER_FONT)],
            [sg.Text(f'Total Checks: {total_checks}   |   Total Fruit Inspected: {int(total_fruit)}', font=BTN_FONT)],
            [sg.HorizontalSeparator()],
            [sg.Text('OVERALL DEFECT RATES (colour-coded)', font=BTN_FONT)],
            *stat_layout,
            [sg.Text('● GREEN ≤ lower limit   ● YELLOW = watch   ● RED = report', font=("Sans", 11, "bold"))],
            [sg.HorizontalSeparator()],
            [sg.Text('PER-WORKER BREAKDOWN (full day – all blocks)', font=BTN_FONT)],
            [sg.Table(
                values=table_rows,
                headings=headings,
                font=TABLE_FONT,
                auto_size_columns=True,
                num_rows=min(len(table_rows) + 1, 15),
                justification='center',
                key='-WORKER_TABLE-',
                row_colors=[(len(table_rows) - 1, 'darkslategray', 'white')],
            )],
            [sg.Button('VIEW CHECKS DETAIL', **btn_kwargs),
             sg.Button('BACK TO BLOCKS',     **btn_kwargs),
             sg.Button('CHANGE DATE',        **btn_kwargs),
             sg.Button('QUIT',               **back_kwargs)],
        ]
        win = _centred_window(layout, title=f'QA Summary – {selected_block} – {selected_date}')
        ev, _ = win.read()
        win.close()

        if ev == 'VIEW CHECKS DETAIL':
            _show_checks_detail(detail_rows, detail_headings, selected_block, selected_date)
        elif ev == 'BACK TO BLOCKS':
            conn.close()
            AppleQASummary()
            return
        elif ev == 'CHANGE DATE':
            conn.close()
            AppleQASummary()
            return
        else:
            break

    conn.close()


def _show_checks_detail(detail_rows, headings, block, date):
    """Show a scrollable table of every individual check with timestamps."""
    layout = [
        [sg.Text('Individual Checks Detail', font=TITLE_FONT)],
        [sg.Text(f'Block: {block}   |   Date: {date}', font=HEADER_FONT)],
        [sg.Text(f'{len(detail_rows)} check(s) recorded', font=BTN_FONT)],
        [sg.HorizontalSeparator()],
        [sg.Table(
            values=detail_rows,
            headings=headings,
            font=TABLE_FONT,
            auto_size_columns=True,
            num_rows=min(len(detail_rows), 20),
            justification='center',
            key='-DETAIL_TABLE-',
            expand_x=True,
            expand_y=True,
        )],
        [sg.Button('CLOSE', font=BTN_FONT, size=(12, 1), pad=BTN_PAD,
                   button_color=('white', 'firebrick3'), border_width=2)],
    ]
    win = _centred_window(layout, title=f'Checks Detail – {block} – {date}')
    while True:
        ev, _ = win.read()
        if ev in (sg.WIN_CLOSED, 'CLOSE'):
            break
    win.close()


if __name__ == '__main__':
    sg.theme('DarkBlue3')
    AppleQASummary()

