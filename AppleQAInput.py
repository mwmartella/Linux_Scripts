import platform
import datetime
import sqlite3
import numpy as np
import pandas as pd
import FreeSimpleGUI as sg
from sqlalchemy import create_engine
from pathlib import Path


def _colour_for(value, lower, upper):
    if value <= lower:   return 'lime green'
    if value <= upper:   return 'yellow'
    return 'tomato2'


def _compute_stats(df, total_fruit, defect_lower, defect_upper):
    stats = {}
    for col, key in [('BruiseNew','BN'),('BruiseOld','BO'),('Sunburn','SB'),
                     ('Colour','CL'),('Hail','HL'),('Insect','IN'),('MiscDamage','MD')]:
        try:    pct = df[col].sum() / total_fruit * 100
        except: pct = 0
        stats[key] = (pct, _colour_for(pct, defect_lower, defect_upper))
    return stats


QA_COLS = [
    "Super_ID","TimeStamp","CheckID","FruitChecked",
    "BruiseOld","BruiseNew","Sunburn","Colour","Hail","Insect","MiscDamage",
    "Variety","Block"
]


def AppleQAInput():
    BASE_PATH  = str(Path.home() / 'OneDrive' / '~FARM DATA' / 'Timesheet App') + '/'
    CompName   = platform.node()
    Date       = datetime.datetime.today().strftime('%Y-%m-%d')

    TITLE_FONT = ("Sans", 20, "bold")
    HEADER_FONT= ("Sans", 16, "bold")
    BTN_FONT   = ("Sans", 14, "bold")
    BTN_SIZE   = (22, 2)
    BTN_PAD    = (8, 5)
    TABLE_FONT = ("Sans", 12, "bold")
    COMBO_FONT = ("Sans", 14, "bold")
    STAT_FONT  = ("Sans", 18, "bold")
    WARN_FONT  = ("Sans", 22, "bold")
    btn_kwargs  = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
    back_kwargs = dict(font=BTN_FONT, size=(12, 1), pad=BTN_PAD,
                       button_color=('white', 'firebrick3'), border_width=2)

    def _win(inner, title='Apple QA'):
        layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(inner, element_justification='c'), sg.Push()],
                  [sg.VPush()]]
        w = sg.Window(title, layout, finalize=True, resizable=True)
        w.Maximize()
        return w

    # ── Load QA variables ─────────────────────────────────────────────────
    try:
        vars_df = pd.read_excel(BASE_PATH + 'WORKER DATA/HarvestQAVariables.xlsx')
    except Exception as e:
        sg.popup_error(f'Could not load HarvestQAVariables.xlsx:\n{e}', title='Apple QA Error', font=WARN_FONT)
        return

    def _var(cls):
        row = vars_df.loc[vars_df['Class'] == cls]
        return float(row['Variable'].tolist()[0]) if len(row) else 0.0

    defect_lower = _var('Defect Lower Limit')
    defect_upper = _var('Defect Upper Limit')

    # ── Timesheet DB (source of active jobs + workers) ────────────────────
    ts_db_path = BASE_PATH + f'{CompName} TimeSheetLocal.db'
    try:
        ts_connect = sqlite3.connect(ts_db_path)
        ts_cursor  = ts_connect.cursor()
    except Exception as e:
        sg.popup_error(f'Could not connect to timesheet database:\n{e}', title='Apple QA Error', font=WARN_FONT)
        return

    def _get_active_jobs():
        """Return list of dicts {Field, Variety, Job_Type, Workers} with at least 1 signed-in worker today."""
        try:
            q = ts_cursor.execute(
                "SELECT Field, Variety, Job_Type, Worker, SUM(Signal) as Signal "
                "FROM WorkerRowLog WHERE TimeStamp LIKE ? "
                "GROUP BY Field, Variety, Job_Type, Worker;",
                (Date + '%',))
            df = pd.DataFrame(q, columns=['Field', 'Variety', 'Job_Type', 'Worker', 'Signal'])
            if df.empty:
                return []
            df = df[df['Signal'] > 0]
            if df.empty:
                return []
            grouped = df.groupby(['Field', 'Variety', 'Job_Type'])['Worker'].count().reset_index()
            grouped.columns = ['Field', 'Variety', 'Job_Type', 'Workers']
            return grouped.to_dict('records')
        except Exception:
            return []

    def _get_active_workers(field, variety):
        """Return list of worker names currently signed in on a specific field/variety today."""
        try:
            q = ts_cursor.execute(
                "SELECT Worker, SUM(Signal) as Signal FROM WorkerRowLog "
                "WHERE Field = ? AND Variety = ? AND TimeStamp LIKE ? "
                "GROUP BY Worker;",
                (field, variety, Date + '%'))
            df = pd.DataFrame(q, columns=['Worker', 'Signal'])
            df = df[df['Signal'] > 0]
            return df['Worker'].tolist()
        except Exception:
            return []

    # ── Apple QA DB ───────────────────────────────────────────────────────
    qa_db_path = BASE_PATH + f'{CompName} AppleLog.db'
    try:
        engine      = create_engine("sqlite:///" + qa_db_path)
        sql_connect = sqlite3.connect(qa_db_path)
        cursor      = sql_connect.cursor()
        cursor.execute(f"CREATE TABLE IF NOT EXISTS QA ({', '.join([c + ' TEXT' for c in QA_COLS])})")
        sql_connect.commit()
    except Exception as e:
        sg.popup_error(f'Could not connect to Apple QA database:\n{e}', title='Apple QA Error', font=WARN_FONT)
        return

    # ── SCREEN 1: Select active job ───────────────────────────────────────
    while True:
        active_jobs = _get_active_jobs()
        if not active_jobs:
            sg.popup('No active row jobs found for today.\nStart a row job first.', title='Apple QA', font=WARN_FONT)
            return

        table_rows = [[j['Field'], j['Variety'], j['Job_Type'], j['Workers']] for j in active_jobs]
        layout = [
            [sg.Text('Apple QA', font=TITLE_FONT)],
            [sg.Text('Select Active Job', font=HEADER_FONT)],
            [sg.Table(values=table_rows,
                      headings=['Field', 'Variety', 'Job Type', 'Workers'],
                      font=TABLE_FONT, auto_size_columns=True, num_rows=7,
                      key='-JOB_TABLE-', select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                      justification='center')],
            [sg.Button('SELECT', **btn_kwargs), sg.Button('BACK', **back_kwargs)],
        ]
        win = _win(layout)
        ev, vals = win.read()
        win.close()
        if ev in (sg.WIN_CLOSED, 'BACK'):
            return

        selected_rows = vals.get('-JOB_TABLE-', [])
        if not selected_rows:
            sg.popup('Please select a job from the table.', title='Apple QA', font=BTN_FONT)
            continue

        job = active_jobs[selected_rows[0]]
        selected_field   = job['Field']
        selected_variety = job['Variety']
        break

    # ── WORKER LOOP ───────────────────────────────────────────────────────
    while True:
        worker_list = _get_active_workers(selected_field, selected_variety)
        if not worker_list:
            sg.popup(f'No active workers found on\n{selected_field} / {selected_variety}', title='Apple QA', font=WARN_FONT)
            return

        worker_buttons = [sg.Button(w, **btn_kwargs) for w in worker_list]
        # Split into rows of 3 for readability
        worker_rows = [worker_buttons[i:i+3] for i in range(0, len(worker_buttons), 3)]

        layout = [[sg.Text('SELECT WORKER', font=TITLE_FONT)],
                  [sg.Text(f'{selected_field}  |  {selected_variety}', font=HEADER_FONT)],
                  *worker_rows,
                  [sg.Button('BACK', **back_kwargs)]]
        win = _win(layout)
        ev, _ = win.read()
        win.close()
        if ev in (sg.WIN_CLOSED, 'BACK'):
            return
        worker = ev

        # Load today's QA stats for this worker
        try:
            raw   = cursor.execute("SELECT * FROM QA")
            qa_df = pd.DataFrame(raw, columns=QA_COLS)
            qa_df = qa_df[qa_df['TimeStamp'].str.contains(Date, na=False)]
            qa_df = qa_df[qa_df['CheckID'].str.contains(worker, na=False)]
            for col in QA_COLS[3:]:
                qa_df[col] = pd.to_numeric(qa_df[col], errors='coerce')
            total_fruit = qa_df['FruitChecked'].sum() or 1
        except Exception:
            qa_df = pd.DataFrame(columns=QA_COLS)
            total_fruit = 1

        stats = _compute_stats(qa_df, total_fruit, defect_lower, defect_upper)

        defects1 = ['Bruise-Old', 'Bruise-New', 'Sunburn']
        defects2 = ['Colour', 'Misc Damage', 'Hail']
        row1 = [sg.Combo([d]+list(range(1,11)), default_value=d, size=18, key=d, font=COMBO_FONT) for d in defects1]
        row2 = [sg.Combo([d]+list(range(1,11)), default_value=d, size=18, key=d, font=COMBO_FONT) for d in defects2]

        BN, BN_C = stats['BN'];   BO, BO_C = stats['BO'];   SB, SB_C = stats['SB']
        CL, CL_C = stats['CL'];   HL, HL_C = stats['HL'];   IN_, IN_C = stats['IN']
        MD, MD_C = stats['MD']

        layout = [
            [sg.Text(f'{worker}  —  Apple QA', font=TITLE_FONT)],
            [sg.Text(f'{selected_field}  |  {selected_variety}', font=HEADER_FONT)],
            [sg.Combo(['Bin #']+list(range(1,26)), default_value='Bin #', size=15, key='BinLog', font=COMBO_FONT),
             sg.Combo(['Fruit Checked',5,10,15,20], default_value='Fruit Checked', size=22, key='AMT', font=COMBO_FONT)],
            row1, row2,
            [sg.Combo(['Insect']+list(range(1,11)), default_value='Insect', size=15, key='Insect', font=COMBO_FONT)],
            [sg.Button('LOG', **btn_kwargs), sg.Button('BACK', **back_kwargs)],
            [sg.HorizontalSeparator()],
            [sg.Text("TODAY'S STATS FOR THIS WORKER", font=BTN_FONT)],
            [sg.Text(f'Bruise New={int(BN)}%', font=STAT_FONT, text_color=BN_C),
             sg.Text(f'Bruise Old={int(BO)}%', font=STAT_FONT, text_color=BO_C)],
            [sg.Text(f'Sunburn={int(SB)}%',    font=STAT_FONT, text_color=SB_C),
             sg.Text(f'Colour={int(CL)}%',     font=STAT_FONT, text_color=CL_C)],
            [sg.Text(f'Misc Damage={int(MD)}%',font=STAT_FONT, text_color=MD_C),
             sg.Text(f'Hail={int(HL)}%',       font=STAT_FONT, text_color=HL_C)],
            [sg.Text(f'Insect={int(IN_)}%',    font=STAT_FONT, text_color=IN_C)],
            [sg.Text('● GREEN=Good  ● YELLOW=Watch  ● RED=Report to Super', font=("Sans",11,"bold"))],
        ]
        win = _win(layout)
        ev, vals = win.read()
        win.close()

        if ev in (sg.WIN_CLOSED, 'BACK'):
            continue  # back to worker selection

        if ev == 'LOG':
            def _iv(k):
                try:    return int(vals[k])
                except: return 0

            bin_code = f"{worker}{Date.replace('-','')}{vals['BinLog']}"
            amt      = _iv('AMT') or 10
            bo, bn, sb = _iv('Bruise-Old'), _iv('Bruise-New'), _iv('Sunburn')
            cl, md, hl = _iv('Colour'), _iv('Misc Damage'), _iv('Hail')
            ic         = _iv('Insect')

            data_row = [CompName, datetime.datetime.now(), bin_code, amt,
                        bo, bn, sb, cl, hl, ic, md, selected_variety, selected_field]
            new_df = pd.DataFrame([data_row], columns=QA_COLS)
            try:
                new_df.to_sql('QA', con=engine, if_exists='append', index=False)
            except Exception as e:
                sg.popup_error(f'Failed to save QA record:\n{e}', title='Apple QA Error', font=WARN_FONT)
                continue

            # Post-log summary for this single check
            for col in QA_COLS[3:]:
                new_df[col] = pd.to_numeric(new_df[col], errors='coerce')
            s = _compute_stats(new_df, amt, defect_lower, defect_upper)
            layout = [
                [sg.Text('THIS CHECK — STATS', font=TITLE_FONT)],
                [sg.Text(f'{worker}  |  {selected_field}  |  {selected_variety}', font=HEADER_FONT)],
                [sg.Text(f'Bruise New={int(s["BN"][0])}%',    font=STAT_FONT, text_color=s['BN'][1])],
                [sg.Text(f'Bruise Old={int(s["BO"][0])}%',    font=STAT_FONT, text_color=s['BO'][1])],
                [sg.Text(f'Sunburn={int(s["SB"][0])}%',       font=STAT_FONT, text_color=s['SB'][1])],
                [sg.Text(f'Colour={int(s["CL"][0])}%',        font=STAT_FONT, text_color=s['CL'][1])],
                [sg.Text(f'Misc Damage={int(s["MD"][0])}%',   font=STAT_FONT, text_color=s['MD'][1])],
                [sg.Text(f'Hail={int(s["HL"][0])}%',          font=STAT_FONT, text_color=s['HL'][1])],
                [sg.Text(f'Insect={int(s["IN"][0])}%',        font=STAT_FONT, text_color=s['IN'][1])],
                [sg.Button('DONE', **btn_kwargs)],
            ]
            win = _win(layout)
            win.read()
            win.close()
            # Loop back to worker selection for next check
