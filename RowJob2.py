#This whole thing is nested in a function becuase it gets imported into a larger field manager program.
def RowJob():
    from sqlalchemy import create_engine, text
    import sqlite3
    import pandas as pd
    import FreeSimpleGUI as sg
    import datetime
    import sys
    import textwrap
    import platform
    import re
    import json
    from touch_helpers import make_touch_combo_row, handle_touch_combos, touch_multi_select

    sg.theme('DarkBlue3')
    TITLE_FONT = ("Sans", 20, "bold")
    HEADER_FONT = ("Sans", 16, "bold")
    BODY_FONT = ("Sans", 11, "bold")
    BTN_FONT = ("Sans", 14, "bold")
    BTN_SIZE = (22, 2)
    BTN_PAD = (8, 5)
    COMBO_FONT = ("Sans", 14, "bold")
    COMBO_SIZE = 35
    TABLE_FONT = ("Sans", 12, "bold")
    WARN_FONT = ("Sans", 22, "bold")
    SMALL_BTN_FONT = ("Sans", 12, "bold")
    SMALL_BTN_SIZE = (14, 2)

    def _make_window(layoutA, title='Row Job Manager'):
        layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                  [sg.VPush()]]
        win = sg.Window(title, layout, finalize=True, resizable=True)
        win.Maximize()
        return win

    def _show_error(msg):
        """Show a blocking error popup and return when user dismisses it."""
        layoutB = [[sg.Text(msg, font=WARN_FONT)],
                   [sg.Button('BACK', **btn_kwargs)]]
        win = _make_window(layoutB, 'ERROR')
        while True:
            ev, _ = win.read()
            if ev in (sg.WIN_CLOSED, 'BACK'):
                break
        win.close()

    def _safe_close(win):
        """Close a window safely, ignoring errors if already closed."""
        try:
            win.close()
        except Exception:
            pass

    btn_kwargs = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
    back_kwargs = dict(font=BTN_FONT, size=(12, 1), pad=BTN_PAD, button_color=('white', 'firebrick3'), border_width=2)

    # ── Load JSON config ──────────────────────────────────────────────────
    json_path = '/home/super1/OneDrive/~FARM DATA/Timesheet App/ACTIVITYLOG.json'
    try:
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        sg.popup_error(f'Could not load activity config:\n{e}',
                       title='Startup Error', font=BTN_FONT, keep_on_top=True)
        return

    def find_block(data, field, variety):
        for block, attributes in data.items():
            if attributes.get("Field") == field and attributes.get("Variety") == variety:
                return block
        return None

    # ── Database setup ────────────────────────────────────────────────────
    BASE_PATH = '/home/super1/OneDrive/~FARM DATA/Timesheet App/'
    CompName = platform.node()
    DB1 = "sqlite:///" + BASE_PATH + "SUPER2 TimeSheetLocal.db"
    DB2 = BASE_PATH + "SUPER2 TimeSheetLocal.db"

    Day = datetime.datetime.now().strftime('%Y-%m-%d')
    RE = re.compile(Day + r" \d{2}:\d{2}:\d{2}\.\d{6}")

    # ── Load reference data with error handling ───────────────────────────
    try:
        FieldList = sorted({block["Field"] for block in data.get('BlockDict', {}).values() if "Field" in block})
        VarietyDataFrame = pd.read_excel(BASE_PATH + 'BlockData/VARIETY.xlsx')
        VarietyList = VarietyDataFrame['VARIETY'].tolist()
        BlockDataFrame = pd.read_excel(BASE_PATH + 'BlockData/BLOCKDATA.xlsx')
        CasualDataFrame = pd.read_excel(BASE_PATH + 'WORKER DATA/CASUAL STAFF.xlsx')
    except Exception as e:
        sg.popup_error(f'Could not load reference data:\n{e}',
                       title='Startup Error', font=BTN_FONT, keep_on_top=True)
        return

    QACHECKLIST = ['All Good', 'Missed Work - Sent Back', 'Work Too Heavy', 'Work Too Light',
                   'Worker Issues - Distracted', 'Worker Issues - Attitude', 'Worker Issues - Other']
    JobTypeList = ['Picking', 'Pruning', 'Thinning', 'Establish Planting', 'Tree Training',
                   'Packing', 'Irrigation Maintinance',
                   "Cherry Packing 1kg", "Cherry Packing 2kg", "Cherry Packing 5kg", "Cherry Packing 10kg"]

    try:
        engine = create_engine(DB1)
        sql_connect = sqlite3.connect(DB2)
        cursor = sql_connect.cursor()
        engine2 = create_engine("sqlite:///" + BASE_PATH + "RowJobQa.db")
        sql_connect2 = sqlite3.connect(BASE_PATH + 'RowJobQa.db')
        cursor2 = sql_connect2.cursor()
    except Exception as e:
        sg.popup_error(f'Could not connect to database:\n{e}',
                       title='DB Error', font=BTN_FONT, keep_on_top=True)
        return

    # Ensure required tables exist
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS WorkerRowLog (
            Field TEXT, Row TEXT, Worker TEXT, Action TEXT,
            TimeStamp TEXT, Signal REAL, Variety TEXT, Job_Type TEXT)""")
        sql_connect.commit()
    except Exception:
        pass

    # ══════════════════════════════════════════════════════════════════════
    #  STEP 1 — Select Field / Variety / Job
    # ══════════════════════════════════════════════════════════════════════
    layoutB = [[sg.Text('Row Job Manager', font=TITLE_FONT)],
               [sg.Text('Select Field', font=HEADER_FONT)],
               make_touch_combo_row('Select Field', 'Field'),
               [sg.Text('Select Variety', font=HEADER_FONT)],
               make_touch_combo_row('Select Variety', 'Variety'),
               [sg.Text('Select Job Type', font=BODY_FONT)],
               make_touch_combo_row('Select Job', 'Job'),
               [sg.Button('Next', **btn_kwargs)],
               [sg.Button('Back', **back_kwargs)]]
    _combos_field = {
        'Field': ('Select Field', FieldList),
        'Variety': ('Select Variety', VarietyList),
        'Job': ('Select Job Type', JobTypeList),
    }
    window = _make_window(layoutB)
    while True:
        event, values = window.read()
        if handle_touch_combos(event, window, _combos_field):
            continue
        break

    if event in (sg.WIN_CLOSED, 'Back'):
        _safe_close(window)
        return

    # event == 'Next'
    Field = values.get('Field', '')
    JobType = values.get('Job', '')
    Variety = values.get('Variety', '')
    _safe_close(window)

    # Validate selections
    if not Field or Field == '--Select--' or not JobType or JobType == '--Select--' or not Variety or Variety == '--Select--':
        _show_error('Please select Field, Variety, and Job Type')
        return

    # ══════════════════════════════════════════════════════════════════════
    #  STEP 2 — Main row management loop
    # ══════════════════════════════════════════════════════════════════════
    Block = find_block(data.get('BlockDict', {}), Field, Variety)
    if Block is None:
        _show_error(f'No block found for\n{Field} / {Variety}')
        return

    block_info = data.get('BlockDict', {}).get(Block, {})
    block_row = block_info.get("Row", "Unknown")

    def _get_timesheet_logged_in_workers():
        """Query the timesheet log and return a list of worker names currently clocked in."""
        try:
            result = cursor.execute(
                "SELECT WorkerName, SUM(Signal) as total FROM WorkerTimeLog GROUP BY WorkerName")
            rows = result.fetchall()
            return [name for name, sig in rows if sig and float(sig) > 0]
        except Exception:
            return []

    def _get_row_logged_in_workers(field):
        """Return set of worker names already signed into this row job today."""
        try:
            result = cursor.execute(
                "SELECT * FROM WorkerRowLog WHERE Field = ?", (field,))
            df = pd.DataFrame(
                result.fetchall(),
                columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
            df = df[df['TimeStamp'].astype(str).str.contains(RE, regex=True, na=False)]
            if df.empty:
                return set()
            df['Signal'] = pd.to_numeric(df['Signal'], errors='coerce').fillna(0)
            grouped = df.groupby('Worker')['Signal'].sum().reset_index()
            return set(grouped.loc[grouped['Signal'] >= 1, 'Worker'].tolist())
        except Exception:
            return set()

    Signalq = 0
    while Signalq == 0:
        # Query current row-job status safely
        try:
            CurrentRowLog = cursor.execute(
                "SELECT * FROM WorkerRowLog WHERE Field = ?", (Field,))
            CurrentRowLogFrame = pd.DataFrame(
                CurrentRowLog.fetchall(),
                columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
        except Exception:
            CurrentRowLogFrame = pd.DataFrame(
                columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])

        CurrentRowLogFrame = CurrentRowLogFrame[
            CurrentRowLogFrame['TimeStamp'].astype(str).str.contains(RE, regex=True, na=False)]

        if not CurrentRowLogFrame.empty:
            CurrentRowLogFrame['Signal'] = pd.to_numeric(CurrentRowLogFrame['Signal'], errors='coerce').fillna(0)
            CurrentRowLogFrame = CurrentRowLogFrame.groupby(
                ['Worker', 'Field', 'Variety', 'Job_Type'])['Signal'].sum().reset_index()
            CurrentRowLogFilter = CurrentRowLogFrame.loc[CurrentRowLogFrame['Signal'] == 1].copy()
        else:
            CurrentRowLogFilter = pd.DataFrame(columns=['Worker', 'Field', 'Variety', 'Job_Type', 'Signal'])

        headers = {'Worker': [], 'Field': [], 'Variety': [], 'Job_Type': [], 'Signal': []}
        headings = list(headers)
        table_values = CurrentRowLogFilter.values.tolist()

        # Build list of workers currently signed into this row (for Sign Out combo)
        row_signed_in = CurrentRowLogFilter['Worker'].tolist() if not CurrentRowLogFilter.empty else []

        layoutB = [[sg.Text('Row Job Manager for %s' % Field, font=TITLE_FONT)],
                   [sg.Table(values=table_values, headings=headings, font=TABLE_FONT, auto_size_columns=True)],
                   [sg.Text('Add Workers: bulk sign-in from timesheet', font=BODY_FONT)],
                   [sg.Text('Sign Out: select worker & press Sign Out', font=BODY_FONT)],
                   [sg.Text('Select Worker (for sign out)', font=BODY_FONT)],
                   make_touch_combo_row('Select Worker', 'Worker'),
                   [sg.pin(sg.Button('Add Workers', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD,
                                     border_width=2, button_color=('white', 'DarkGreen'))),
                    sg.pin(sg.Button('Sign Out', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD, border_width=2)),
                    sg.pin(sg.Button('Sign Out All', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD, border_width=2)),
                    sg.pin(sg.Button('Back', **back_kwargs)),
                    sg.pin(sg.Button('QA LOG', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD, border_width=2))]]

        # The combo is only used for sign-out, so populate with workers on this row
        _combos_worker = {
            'Worker': ('Select Worker', row_signed_in if row_signed_in else ['(no workers signed in)']),
        }
        window = _make_window(layoutB)
        while True:
            event, values = window.read()
            if handle_touch_combos(event, window, _combos_worker):
                continue
            break

        # ── Back / Close ──────────────────────────────────────────────────
        if event in (sg.WIN_CLOSED, 'Back'):
            _safe_close(window)
            Signalq = 1
            continue

        # ── Add Workers (bulk sign-in) ────────────────────────────────────
        if event == 'Add Workers':
            _safe_close(window)

            # Get workers clocked into the timesheet today
            timesheet_workers = _get_timesheet_logged_in_workers()
            if not timesheet_workers:
                _show_error('NO WORKERS CLOCKED IN\nON THE TIMESHEET')
                continue

            # Remove workers already signed into this row job
            already_on_row = _get_row_logged_in_workers(Field)
            available = [w for w in timesheet_workers if w not in already_on_row]

            if not available:
                _show_error('ALL CLOCKED-IN WORKERS\nALREADY ON THIS ROW')
                continue

            # Open multi-select popup
            chosen = touch_multi_select('Select Workers to Sign In', sorted(available))
            if not chosen:
                continue  # user cancelled or selected nothing

            # Write all chosen workers into the row log
            try:
                TimeStamp = datetime.datetime.now()
                rows_to_write = []
                for w in chosen:
                    rows_to_write.append(
                        [Field, block_row, w, 'Start', TimeStamp, 1, Variety, JobType])
                bulk_df = pd.DataFrame(
                    rows_to_write,
                    columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                bulk_df.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
            except Exception as e:
                _show_error(f'DB WRITE ERROR:\n{str(e)[:200]}')
            continue

        # ── Helper: validate worker selection for sign out ────────────────
        Worker = values.get('Worker', '--Select--') if values else '--Select--'

        # ── Sign Out ──────────────────────────────────────────────────────
        if event == 'Sign Out':
            _safe_close(window)
            if Worker in ('--Select--', '', None, '(no workers signed in)'):
                _show_error('PLEASE SELECT A WORKER')
                continue
            try:
                WorkerCheckLog = cursor.execute(
                    "SELECT * FROM WorkerRowLog WHERE Field = ? AND Worker = ?",
                    (Field, Worker))
                WorkerCheckLog = pd.DataFrame(
                    WorkerCheckLog.fetchall(),
                    columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                WorkerCheckLog = WorkerCheckLog[
                    WorkerCheckLog['TimeStamp'].astype(str).str.contains(RE, regex=True, na=False)]
                WorkerCheckLog['Signal'] = pd.to_numeric(WorkerCheckLog['Signal'], errors='coerce').fillna(0)
                WorkerCheckSignal = WorkerCheckLog['Signal'].sum()
            except Exception:
                WorkerCheckSignal = 0

            if WorkerCheckSignal <= 0:
                _show_error('WORKER NOT LOGGED INTO ROW')
                continue

            try:
                TimeStamp = datetime.datetime.now()
                RowLogDataFrame = pd.DataFrame(
                    [[Field, block_row, Worker, 'Finish', TimeStamp, -1, Variety, JobType]],
                    columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                RowLogDataFrame.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
            except Exception as e:
                _show_error(f'DB WRITE ERROR:\n{str(e)[:200]}')
            continue

        # ── Sign Out All ──────────────────────────────────────────────────
        if event == 'Sign Out All':
            _safe_close(window)
            if CurrentRowLogFilter.empty:
                _show_error('NO WORKERS TO SIGN OUT')
                continue
            try:
                rows_to_write = []
                TimeStamp = datetime.datetime.now()
                for _, row in CurrentRowLogFilter.iterrows():
                    rows_to_write.append(
                        [Field, block_row, row['Worker'], 'Finish', TimeStamp, -1, Variety, JobType])
                if rows_to_write:
                    bulk_df = pd.DataFrame(
                        rows_to_write,
                        columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                    bulk_df.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
            except Exception as e:
                _show_error(f'DB WRITE ERROR:\n{str(e)[:200]}')
            continue

        # ── QA LOG (placeholder) ──────────────────────────────────────────
        if event == 'QA LOG':
            _safe_close(window)
            _show_error('QA LOG NOT YET IMPLEMENTED')
            continue

        # Fallback — unknown event, just close and loop
        _safe_close(window)
