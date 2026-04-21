from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import FreeSimpleGUI as sg
import datetime
import sys
import textwrap
import TimeLog
import RowJob2
import CherryHarvest
import platform
import subprocess
#Start Up Database engines....... Vroom+
SignalDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/SPLITSIGNAL.xlsx')

CompName = platform.node()
print(CompName)
BASE_PATH = '/home/super1/OneDrive/~FARM DATA/Timesheet App/'
DB1 = "sqlite:///" + BASE_PATH + f"{CompName} TimeSheetLocal.db"
DB2 = BASE_PATH + f"{CompName} TimeSheetLocal.db"

#Start Up Database engines....... Vroom
engine = create_engine(DB1) 
sql_connect = sqlite3.connect(DB2)
cursor = sql_connect.cursor()

engine2 = create_engine("sqlite:///" + BASE_PATH + "TimeSheetGlobal.db") 
sql_connect2 = sqlite3.connect(BASE_PATH + 'TimeSheetGlobal.db')
cursor2 = sql_connect.cursor()

engine3 = create_engine("sqlite:///" + BASE_PATH + "RowJobQa.db") 
sql_connect3 = sqlite3.connect(BASE_PATH + 'RowJobQa.db')
cursor3 = sql_connect3.cursor()

sg.theme('DarkBlue3')

# Surface 3: 10.8" at 1920x1280 — scale fonts/buttons for touch on small high-DPI screen
TITLE_FONT = ("Sans", 28, "bold")
SUBTITLE_FONT = ("Sans", 18, "bold")
BTN_FONT = ("Sans", 16, "bold")
BTN_SIZE = (28, 2)
BTN_PAD = (8, 6)

MasterSignal = 0
while MasterSignal < 1:
    btn_kwargs = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
    layoutA = [
        [sg.Text('Field Manager', font=TITLE_FONT, justification='center')],
        [sg.Text('Please Select Supervisor Task', font=SUBTITLE_FONT, justification='center')],
        [sg.Button('Timesheet Log', **btn_kwargs)],
        [sg.Button('Row Job Manager', **btn_kwargs)],
        [sg.Button('Cherry Harvest Manager', **btn_kwargs)],
        [sg.Button('Apple Harvest Manager', **btn_kwargs)],
        [sg.Button('Status Report', **btn_kwargs)],
        [sg.Button('Sync OneDrive', font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD,
                    button_color=('white', 'DarkGreen'), border_width=2)],
        [sg.VPush()],
        [sg.Button('Quit', font=BTN_FONT, size=(12, 1), pad=BTN_PAD,
                    button_color=('white', 'firebrick3'), border_width=2)],
    ]
    layout = [[sg.VPush()],
              [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
              [sg.VPush()]]
    window = sg.Window('Time and Labour', layout, finalize=True,
                       resizable=True, keep_on_top=False)
    window.Maximize()
    event, values = window.read()
    if event == 'Timesheet Log':
        window.close()
        if CompName != "SuperTwo":
            TimeLog.TimeLog()
        else:
            SignalDataFrame['Value'] = SignalDataFrame['Value'].astype(int)
            SIGLIST = SignalDataFrame['Value'].tolist()
            SIG = SIGLIST[0]
            if SIG == 1:
                TimeLog.TimeLog()
    elif event == 'Row Job Manager':
        window.close()
        RowJob2.RowJob()
    elif event == 'Cherry Harvest Manager':
        window.close()
        CherryHarvest.CherryHarvest()
    elif event == 'Sync OneDrive':
        window.close()
        try:
            proc = subprocess.Popen(
                ['onedrive', '--synchronize'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
        except FileNotFoundError:
            sg.popup('onedrive client not found.\nInstall with: sudo apt install onedrive',
                     title='Sync Error', font=BTN_FONT, keep_on_top=True)
            continue

        # ── Progress window ───────────────────────────────────────────────
        SPINNER = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        spin_layout = [
            [sg.Text('Syncing OneDrive…', font=("Sans", 22, "bold"),
                     justification='center', expand_x=True)],
            [sg.Text(SPINNER[0], key='-SPIN-', font=("Sans", 48, "bold"),
                     justification='center', expand_x=True)],
            [sg.Text('Please wait — do not close this window.',
                     font=("Sans", 14), justification='center', expand_x=True)],
            [sg.Text('', key='-STATUS-', font=("Sans", 11), justification='center',
                     size=(60, 2), expand_x=True)],
        ]
        spin_window = sg.Window(
            'Syncing…',
            [[sg.VPush()],
             [sg.Push(), sg.Column(spin_layout, element_justification='c'), sg.Push()],
             [sg.VPush()]],
            finalize=True, resizable=True, keep_on_top=True,
            no_titlebar=False, modal=False
        )
        spin_window.Maximize()

        spin_idx   = 0
        last_line  = ''
        timed_out  = False
        poll_count = 0
        MAX_POLLS  = 1800   # 300 s at 166 ms each

        while proc.poll() is None:
            spin_window.read(timeout=166)           # ~6 frames/sec
            spin_idx = (spin_idx + 1) % len(SPINNER)
            spin_window['-SPIN-'].update(SPINNER[spin_idx])

            # Read any new output without blocking
            try:
                import select
                ready, _, _ = select.select([proc.stdout], [], [], 0)
                if ready:
                    line = proc.stdout.readline().strip()
                    if line:
                        last_line = line[-80:]      # keep last 80 chars
                        spin_window['-STATUS-'].update(last_line)
            except Exception:
                pass

            poll_count += 1
            if poll_count >= MAX_POLLS:
                proc.kill()
                timed_out = True
                break

        spin_window.close()

        if timed_out:
            sg.popup('Sync timed out after 5 minutes.',
                     title='Sync Timeout', font=BTN_FONT, keep_on_top=True)
        elif proc.returncode == 0:
            sg.popup('✔  OneDrive sync completed successfully!',
                     title='Sync Complete', font=BTN_FONT, keep_on_top=True)
        else:
            # Grab any remaining stderr
            remaining = proc.stdout.read()[-500:] if proc.stdout else ''
            sg.popup(f'Sync finished with errors:\n{remaining}',
                     title='Sync Error', font=BTN_FONT, keep_on_top=True)
    elif event == 'Quit':
        #FinalDailyDatabase = cursor.execute("""SELECT * FROM WorkerTimeLog""")
        ##FinalDailyDataFrame.to_csv(CompName + 'FINALDAILY.csv')
        #FinalDailyRowDatabase = cursor.execute("""SELECT * FROM WorkerRowLog""")
        #FinalDailyRowDataFrame = pd.DataFrame(FinalDailyRowDatabase, columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety'])
        #FinalDailyRowDataFrame.to_csv(CompName + 'FINALDAILYROW.csv')
        #FinalDailyRowQADatabase = cursor3.execute("""SELECT * FROM COLUMNS""")
        #FinalDailyRowQADataFrame = pd.DataFrame(FinalDailyRowQADatabase, columns=['Date', 'Text', 'Field', 'Job', 'Worker', 'QA', 'Variety'])
        #FinalDailyRowQADataFrame.to_csv(CompName + 'FINALDAILYROWQA.csv')
        MasterSignal += 1
    else:
        continue
