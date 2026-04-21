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
    TITLE_FONT   = ("Sans", 20, "bold")
    HEADER_FONT  = ("Sans", 16, "bold")
    BODY_FONT    = ("Sans", 11, "bold")
    BTN_FONT     = ("Sans", 14, "bold")
    BTN_SIZE     = (22, 2)
    BTN_PAD      = (8, 5)
    TABLE_FONT   = ("Sans", 12, "bold")
    WARN_FONT    = ("Sans", 22, "bold")
    SMALL_BTN_FONT = ("Sans", 12, "bold")
    SMALL_BTN_SIZE = (14, 2)

    def _make_window(layoutA, title='Row Job Manager'):
        layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                  [sg.VPush()]]
        win = sg.Window(title, layout, finalize=True, resizable=True)
        win.Maximize()
        return win

    btn_kwargs  = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
    back_kwargs = dict(font=BTN_FONT, size=(12, 1), pad=BTN_PAD,
                       button_color=('white', 'firebrick3'), border_width=2)

    def _show_error(msg):
        layoutE = [[sg.Text(msg, font=WARN_FONT)],
                   [sg.Button('BACK', **btn_kwargs)]]
        win = _make_window(layoutE, 'ERROR')
        while True:
            ev, _ = win.read()
            if ev in (sg.WIN_CLOSED, 'BACK'):
                break
        win.close()

    def _safe_close(win):
        try:
            win.close()
        except Exception:
            pass

    # ── Load JSON config ──────────────────────────────────────────────────
    json_path = '/home/super1/OneDrive/~FARM DATA/Timesheet App/ACTIVITYLOG.json'
    try:
        with open(json_path, 'r') as json_file:
            data = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        sg.popup_error(f'Could not load activity config:\n{e}',
                       title='Startup Error', font=BTN_FONT, keep_on_top=True)
        return

    def find_block(d, field, variety):
        for block, attrs in d.items():
            if attrs.get("Field") == field and attrs.get("Variety") == variety:
                return block
        return None

    # ── Database setup ────────────────────────────────────────────────────
    BASE_PATH = '/home/super1/OneDrive/~FARM DATA/Timesheet App/'
    CompName = platform.node()
    DB1 = "sqlite:///" + BASE_PATH + f"{CompName} TimeSheetLocal.db"
    DB2 = BASE_PATH + f"{CompName} TimeSheetLocal.db"
    Day = datetime.datetime.now().strftime('%Y-%m-%d')

    try:
        FieldList    = sorted({b["Field"]   for b in data.get('BlockDict', {}).values() if "Field"   in b})
        VarietyDF    = pd.read_excel(BASE_PATH + 'BlockData/VARIETY.xlsx')
        VarietyList  = VarietyDF['VARIETY'].tolist()
        BlockDataFrame = pd.read_excel(BASE_PATH + 'BlockData/BLOCKDATA.xlsx')
        CasualDataFrame = pd.read_excel(BASE_PATH + 'WORKER DATA/CASUAL STAFF.xlsx')
    except Exception as e:
        sg.popup_error(f'Could not load reference data:\n{e}',
                       title='Startup Error', font=BTN_FONT, keep_on_top=True)
        return

    JobTypeList = ['Picking', 'Pruning', 'Thinning', 'Establish Planting', 'Tree Training',
                   'Packing', 'Irrigation Maintinance',
                   "Cherry Packing 1kg", "Cherry Packing 2kg", "Cherry Packing 5kg", "Cherry Packing 10kg"]

    try:
        engine      = create_engine(DB1)
        sql_connect = sqlite3.connect(DB2)
        cursor      = sql_connect.cursor()
        engine2     = create_engine("sqlite:///" + BASE_PATH + "RowJobQa.db")
        sql_connect2 = sqlite3.connect(BASE_PATH + 'RowJobQa.db')
        cursor2     = sql_connect2.cursor()
    except Exception as e:
        sg.popup_error(f'Could not connect to database:\n{e}',
                       title='DB Error', font=BTN_FONT, keep_on_top=True)
        return

    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS WorkerRowLog (
            Field TEXT, Row TEXT, Worker TEXT, Action TEXT,
            TimeStamp TEXT, Signal REAL, Variety TEXT, Job_Type TEXT)""")
        sql_connect.commit()
    except Exception:
        pass

    # ── Shared DB helpers ─────────────────────────────────────────────────
    def _get_timesheet_logged_in_workers():
        try:
            query = cursor.execute(
                "SELECT WorkerName, SUM(Signal) FROM WorkerTimeLog GROUP BY WorkerName;")
            df = pd.DataFrame(query, columns=['Name', 'Signal'])
            df = df.drop(df[df.Signal == 0].index)
            logged_in = df['Name'].tolist()
            print(f"[RowJob] Timesheet logged-in workers: {logged_in}")
            return logged_in
        except Exception as e:
            print(f"[RowJob] ERROR querying WorkerTimeLog: {e}")
            return []

    def _get_row_logged_in_workers(field):
        try:
            query = cursor.execute(
                "SELECT Worker, SUM(Signal) as Signal FROM WorkerRowLog "
                "WHERE Field = ? AND TimeStamp LIKE ? GROUP BY Worker;",
                (field, Day + '%'))
            df = pd.DataFrame(query, columns=['Worker', 'Signal'])
            df = df.drop(df[df.Signal == 0].index)
            already = set(df['Worker'].tolist())
            print(f"[RowJob] Already on row for {field}: {already}")
            return already
        except Exception as e:
            print(f"[RowJob] ERROR querying WorkerRowLog: {e}")
            return set()

    def _get_active_row_jobs():
        """
        Return a list of dicts for every row job that has at least one
        worker currently signed in today.
        Each dict: {Field, Variety, Job_Type, Workers (count)}
        """
        try:
            # Get every worker-level signal for today
            query = cursor.execute(
                "SELECT Field, Variety, Job_Type, Worker, SUM(Signal) as Signal "
                "FROM WorkerRowLog WHERE TimeStamp LIKE ? "
                "GROUP BY Field, Variety, Job_Type, Worker;",
                (Day + '%',))
            df = pd.DataFrame(query, columns=['Field', 'Variety', 'Job_Type', 'Worker', 'Signal'])
            if df.empty:
                return []
            # Keep only workers still signed in
            df = df.drop(df[df.Signal == 0].index)
            if df.empty:
                return []
            # Group to get worker count per job
            grouped = df.groupby(['Field', 'Variety', 'Job_Type'])['Worker'].count().reset_index()
            grouped.columns = ['Field', 'Variety', 'Job_Type', 'Workers']
            return grouped.to_dict('records')
        except Exception as e:
            print(f"[RowJob] ERROR querying active jobs: {e}")
            return []

    # ══════════════════════════════════════════════════════════════════════
    #  STEP 2 — Worker management loop (extracted into a function so both
    #           the dashboard path and the new-job path can call it)
    # ══════════════════════════════════════════════════════════════════════
    def _run_row_job(Field, Variety, JobType, Block, block_row):
        Signalq = 0
        while Signalq == 0:
            # Query current row-job status
            try:
                query = cursor.execute(
                    "SELECT Worker, Field, Variety, Job_Type, SUM(Signal) as Signal "
                    "FROM WorkerRowLog WHERE Field = ? AND TimeStamp LIKE ? "
                    "GROUP BY Worker, Field, Variety, Job_Type;",
                    (Field, Day + '%'))
                CurrentRowLogFilter = pd.DataFrame(
                    query, columns=['Worker', 'Field', 'Variety', 'Job_Type', 'Signal'])
                CurrentRowLogFilter = CurrentRowLogFilter.drop(
                    CurrentRowLogFilter[CurrentRowLogFilter.Signal == 0].index)
                print(f"[RowJob] Workers on row: {CurrentRowLogFilter['Worker'].tolist()}")
            except Exception as e:
                print(f"[RowJob] ERROR querying row status: {e}")
                CurrentRowLogFilter = pd.DataFrame(
                    columns=['Worker', 'Field', 'Variety', 'Job_Type', 'Signal'])

            headings    = ['Worker', 'Field', 'Variety', 'Job_Type', 'Signal']
            table_values = CurrentRowLogFilter.values.tolist()

            layoutB = [[sg.Text('Row Job Manager', font=TITLE_FONT)],
                       [sg.Text(f'{Field}  |  {Variety}  |  {JobType}', font=HEADER_FONT)],
                       [sg.Table(values=table_values, headings=headings,
                                 font=TABLE_FONT, auto_size_columns=True,
                                 num_rows=15)],
                       [sg.pin(sg.Button('Add Workers',     font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE,
                                         pad=BTN_PAD, border_width=2, button_color=('white', 'DarkGreen'))),
                        sg.pin(sg.Button('Add All Workers', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE,
                                         pad=BTN_PAD, border_width=2, button_color=('white', 'DarkGreen'))),
                        sg.pin(sg.Button('End Workers',     font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE,
                                         pad=BTN_PAD, border_width=2)),
                        sg.pin(sg.Button('Sign Out All',    font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE,
                                         pad=BTN_PAD, border_width=2)),
                        sg.pin(sg.Button('Back',            **back_kwargs)),
                        sg.pin(sg.Button('QA LOG',          font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE,
                                         pad=BTN_PAD, border_width=2))]]

            window = _make_window(layoutB)
            event, values = window.read()

            if event in (sg.WIN_CLOSED, 'Back'):
                _safe_close(window)
                Signalq = 1
                continue

            # ── Add Workers ───────────────────────────────────────────────
            if event == 'Add Workers':
                _safe_close(window)
                timesheet_workers = _get_timesheet_logged_in_workers()
                if not timesheet_workers:
                    _show_error('NO WORKERS CLOCKED IN\nON THE TIMESHEET')
                    continue
                already_on_row = _get_row_logged_in_workers(Field)
                available = [w for w in timesheet_workers if w not in already_on_row]
                if not available:
                    _show_error('ALL CLOCKED-IN WORKERS\nALREADY ON THIS ROW')
                    continue
                chosen = touch_multi_select('Select Workers to Sign In', sorted(available))
                if not chosen:
                    continue
                try:
                    TimeStamp = datetime.datetime.now()
                    rows_to_write = [[Field, block_row, w, 'Start', TimeStamp, 1, Variety, JobType]
                                     for w in chosen]
                    bulk_df = pd.DataFrame(rows_to_write,
                                           columns=['Field', 'Row', 'Worker', 'Action',
                                                    'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                    bulk_df.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
                except Exception as e:
                    _show_error(f'DB WRITE ERROR:\n{str(e)[:200]}')
                continue

            # ── Add All Workers ───────────────────────────────────────────
            if event == 'Add All Workers':
                _safe_close(window)
                timesheet_workers = _get_timesheet_logged_in_workers()
                if not timesheet_workers:
                    _show_error('NO WORKERS CLOCKED IN\nON THE TIMESHEET')
                    continue
                already_on_row = _get_row_logged_in_workers(Field)
                available = [w for w in timesheet_workers if w not in already_on_row]
                if not available:
                    _show_error('ALL CLOCKED-IN WORKERS\nALREADY ON THIS ROW')
                    continue
                try:
                    TimeStamp = datetime.datetime.now()
                    rows_to_write = [[Field, block_row, w, 'Start', TimeStamp, 1, Variety, JobType]
                                     for w in available]
                    bulk_df = pd.DataFrame(rows_to_write,
                                           columns=['Field', 'Row', 'Worker', 'Action',
                                                    'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                    bulk_df.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
                except Exception as e:
                    _show_error(f'DB WRITE ERROR:\n{str(e)[:200]}')
                continue

            # ── End Workers ───────────────────────────────────────────────
            if event == 'End Workers':
                _safe_close(window)
                if CurrentRowLogFilter.empty:
                    _show_error('NO WORKERS ON THIS ROW')
                    continue
                on_row = sorted(CurrentRowLogFilter['Worker'].tolist())
                chosen = touch_multi_select('Select Workers to Sign Out', on_row)
                if not chosen:
                    continue
                try:
                    TimeStamp = datetime.datetime.now()
                    rows_to_write = [[Field, block_row, w, 'Finish', TimeStamp, -1, Variety, JobType]
                                     for w in chosen]
                    bulk_df = pd.DataFrame(rows_to_write,
                                           columns=['Field', 'Row', 'Worker', 'Action',
                                                    'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                    bulk_df.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
                except Exception as e:
                    _show_error(f'DB WRITE ERROR:\n{str(e)[:200]}')
                continue

            # ── Sign Out All ──────────────────────────────────────────────
            if event == 'Sign Out All':
                _safe_close(window)
                if CurrentRowLogFilter.empty:
                    _show_error('NO WORKERS TO SIGN OUT')
                    continue
                try:
                    TimeStamp = datetime.datetime.now()
                    rows_to_write = [[Field, block_row, row['Worker'], 'Finish',
                                      TimeStamp, -1, Variety, JobType]
                                     for _, row in CurrentRowLogFilter.iterrows()]
                    if rows_to_write:
                        bulk_df = pd.DataFrame(rows_to_write,
                                               columns=['Field', 'Row', 'Worker', 'Action',
                                                        'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                        bulk_df.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
                except Exception as e:
                    _show_error(f'DB WRITE ERROR:\n{str(e)[:200]}')
                continue

            # ── QA LOG ────────────────────────────────────────────────────
            if event == 'QA LOG':
                _safe_close(window)
                _show_error('QA LOG NOT YET IMPLEMENTED')
                continue

            _safe_close(window)

    # ══════════════════════════════════════════════════════════════════════
    #  OUTER LOOP — Dashboard → Setup → Manage
    # ══════════════════════════════════════════════════════════════════════
    while True:

        # ── STEP 0: Dashboard ─────────────────────────────────────────────
        active_jobs = _get_active_row_jobs()
        has_active  = len(active_jobs) > 0

        dash_headings    = ['Field', 'Variety', 'Job Type', 'Workers On Row']
        dash_table_values = [[j['Field'], j['Variety'], j['Job_Type'], j['Workers']]
                              for j in active_jobs]

        layoutD = [[sg.Text('Row Job Manager', font=TITLE_FONT)],
                   [sg.Text('Active Row Jobs Today', font=HEADER_FONT)],
                   [sg.Table(values=dash_table_values,
                              headings=dash_headings,
                              font=TABLE_FONT,
                              auto_size_columns=True,
                              num_rows=7,
                              key='-ACTIVE_TABLE-',
                              enable_events=False,
                              select_mode=sg.TABLE_SELECT_MODE_BROWSE,
                              justification='center')],
                   [sg.Text('Select a job above and press Open, or start a new one.',
                             font=BODY_FONT)],
                   [sg.pin(sg.Button('Open Selected Job', **btn_kwargs,
                                     button_color=('white', 'DarkGreen'))),
                    sg.pin(sg.Button('New Row Job', **btn_kwargs))],
                   [sg.Button('Back', **back_kwargs)]]

        window = _make_window(layoutD, 'Row Job Dashboard')
        event, values = window.read()

        if event in (sg.WIN_CLOSED, 'Back'):
            _safe_close(window)
            return

        # ── Open an existing active job ───────────────────────────────────
        if event == 'Open Selected Job':
            selected_rows = values.get('-ACTIVE_TABLE-', [])
            if not selected_rows or not active_jobs:
                _safe_close(window)
                _show_error('PLEASE SELECT A JOB\nFROM THE TABLE FIRST')
                continue
            idx     = selected_rows[0]
            job     = active_jobs[idx]
            Field   = job['Field']
            Variety = job['Variety']
            JobType = job['Job_Type']
            _safe_close(window)

            Block = find_block(data.get('BlockDict', {}), Field, Variety)
            if Block is None:
                _show_error(f'No block found for\n{Field} / {Variety}')
                continue
            block_row = data['BlockDict'][Block].get("Row", "Unknown")
            _run_row_job(Field, Variety, JobType, Block, block_row)
            continue

        # ── New Row Job setup ─────────────────────────────────────────────
        if event == 'New Row Job':
            _safe_close(window)

            # STEP 1 — Field / Variety / Job selection
            layoutB = [[sg.Text('New Row Job', font=TITLE_FONT)],
                       [sg.Text('Select Field', font=HEADER_FONT)],
                       make_touch_combo_row('Select Field', 'Field'),
                       [sg.Text('Select Variety', font=HEADER_FONT)],
                       make_touch_combo_row('Select Variety', 'Variety'),
                       [sg.Text('Select Job Type', font=BODY_FONT)],
                       make_touch_combo_row('Select Job', 'Job'),
                       [sg.Button('Next', **btn_kwargs)],
                       [sg.Button('Back', **back_kwargs)]]
            _combos_field = {
                'Field':   ('Select Field',    FieldList),
                'Variety': ('Select Variety',  VarietyList),
                'Job':     ('Select Job Type', JobTypeList),
            }
            window = _make_window(layoutB)
            while True:
                event, values = window.read()
                if handle_touch_combos(event, window, _combos_field):
                    continue
                break

            if event in (sg.WIN_CLOSED, 'Back'):
                _safe_close(window)
                continue  # back to dashboard

            Field   = values.get('Field',   '')
            JobType = values.get('Job',     '')
            Variety = values.get('Variety', '')
            _safe_close(window)

            invalid = (not Field   or Field   == '--Select--' or
                       not JobType or JobType == '--Select--' or
                       not Variety or Variety == '--Select--')
            if invalid:
                _show_error('Please select Field, Variety,\nand Job Type')
                continue

            Block = find_block(data.get('BlockDict', {}), Field, Variety)
            if Block is None:
                _show_error(f'No block found for\n{Field} / {Variety}')
                continue
            block_row = data['BlockDict'][Block].get("Row", "Unknown")

            _run_row_job(Field, Variety, JobType, Block, block_row)
            continue

        _safe_close(window)
