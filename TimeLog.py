#Window Open Show Supervisor Button and Gerneral Worker Button and machine button
#Supervisor Area has buttons for each supervisor, 
#block, job, and a log in or log out button on the following screen
#databasefile will log an event that contains the workers name, time stamp, the action, a 1 in a column to sigal they are logged in, if a 1 is contained in that column already only a logout button should be available
#if the database file contains a 1 in the logged in column then block and job fields should be auto filled and un editable to prevent mixup mistakes.
#Log out brings to log in screen for super with a back button

#Import Modules
from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import FreeSimpleGUI as sg
import datetime
import sys
import textwrap
import platform
from pathlib import Path
from touch_helpers import make_touch_combo_row, handle_touch_combos
from sqlalchemy import create_engine, text as sa_text

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
DISCLAIMER_FONT = ("Sans", 9, "bold")
WARN_FONT = ("Sans", 22, "bold")

#Start Up Database engines....... Vroom
CompName = platform.node()
print(CompName)
BASE_PATH = str(Path.home() / 'OneDrive' / '~FARM DATA' / 'Timesheet App') + '/'
DB1 = "sqlite:///" + BASE_PATH + f"{CompName} TimeSheetLocal.db"
DB2 = BASE_PATH + f"{CompName} TimeSheetLocal.db"
SignalDataFrame = pd.read_excel(BASE_PATH + 'WORKER DATA/SPLITSIGNAL.xlsx')
WorkerReasonList = ['Worker Sick', 'Worker Late', 'Worker No Longer Employed']
def TimeLog():
    if CompName == "SuperTwo":
        SignalDataFrame['Value'] = SignalDataFrame['Value'].astype(int)
        SIGLIST = SignalDataFrame['Value'].tolist()
        SIG = SIGLIST[0]
        if SIG == 0:
            return    
    engine = create_engine(DB1) 
    sql_connect = sqlite3.connect(DB2)
    cursor = sql_connect.cursor()
    engine2 = create_engine("sqlite:///" + BASE_PATH + "TimeSheetGlobal.db") 
    sql_connect2 = sqlite3.connect(BASE_PATH + 'TimeSheetGlobal.db')
    cursor2 = sql_connect.cursor()
    #Compile DataFrames
    SuperDataFrame = pd.read_excel(BASE_PATH + 'WORKER DATA/SUPERVISORS.xlsx')
    CasualDataFrame = pd.read_excel(BASE_PATH + 'WORKER DATA/CASUAL STAFF.xlsx')
    MachineDataFrame = pd.read_excel(BASE_PATH + 'WORKER DATA/MACHINES.xlsx')
    RatesDataFrame = pd.read_excel(BASE_PATH + 'WORKER DATA/PAYRATES.xlsx')
    #Global Variable, Lists and Dicts
    #JobTypeList = ['Picking', 'Pruning', 'Thinning', 'Establish Planting', 'Tree Training', 'Packing', 'Irrigation Maintinance']
    #JobTypeDict = {'Picking': 'PK', 'Pruning': 'PR', 'Thinning': 'TH', 'Establish Planting': 'EP', 'Tree Training': 'TT', 'Packing': 'PA', 'Irrigation Maintinance': 'IM'}
    #BlockList = ["S-SHED PL", "S-SHED SD", "S-SHED Gala", "Pink Belle", "STK GS", "STK LIR", "Rob Bravo", "Cherry Bravo", "GSPL GS", "GSPL PL", "Total PL", "Modi", "Rainier", "Van", "Lapin", "Chelan", "Merchant", "DWF PL", "DWF GS", "LIR18", "LIR19", "BGGS - Bravo", "BGGS - GS", "BGGS - Gala", "WPL - PL", "WPL - GS"]
    #BlockDict = {"B2": "S-SHED PL", "B3": "S-SHED SD", "B4": "S-SHED Gala", "C2": "Pink Belle", "D3": "STK GS", "D4": "STK LIR", "E1": "Rob Bravo", "F1": "Cherry Bravo", "H2": "GSPL GS", "H3": "GSPL PL", "I1": "Total PL", "J1": "Modi", "N2": "Rainier", "N3": "Van", "N5": "Lapin", "N6": "Chelan", "N7": "Merchant", "Q1": "DWF PL", "Q2": "DWF GS", "R1": "LIR18", "S1": "LIR19", "WC2": "BGGS - Bravo", "WC3": "BGGS - GS", "WC4": "BGGS - Gala", "WD2": "WPL - PL", "WD3": "WPL - GS"}
    WorkerClass = 0
    # Load active worker list from local sr1.db instead of Excel
    _sr1_db_path = '/home/sr1/Documents/sr1.db'
    try:
        _sr1_engine = create_engine(f'sqlite:///{_sr1_db_path}')
        with _sr1_engine.connect() as _sr1_conn:
            _workers_result = _sr1_conn.execute(sa_text('SELECT first_name, last_name FROM workers'))
            CasualStaffList = [f"{r[0]} {r[1]}" for r in _workers_result.fetchall()]
        if not CasualStaffList:
            CasualStaffList = CasualDataFrame['Worker Name'].tolist()
    except Exception:
        CasualStaffList = CasualDataFrame['Worker Name'].tolist()
    Disclaimer1 = """FIT FOR WORK - For my own safety and the safety of others, I agree to present fit for work, not under the influence of alcohol or illicit or illegal drugs. I will not consume/use alcohol, illicit or illegal drugs whilst at work. If I am using prescription or over the counter medication that I have been advised by my GP/Chemist, or it is noted on the medication packaging "not to operate machinery or potential to cause effect to operating impairment/ judgement" or in Safety Sensitive Roles and Positions or if I am in any doubt, I will inform my Supervisor immediately."""
    Disclaimer2 = """FATIGUE - I agree to notify my Supervisor immediately if I am or believe that I am suffering fatigue through Lack of sleep, Illness, Personal Issues or other reasons."""
    Disclaimer3 = """SWMS - I have access to and have read and understand the task specific section in the Safe Work Method Statement (SWMS) for the job/s that I will be undertaking and I agree to work within these guidelines. If I am unable to work within these guidelines, I will contact my Supervisor immediately for instructions."""
    Disclaimer4 = "BY SIGNING IN FOR WORK YOU ARE DECLARING THE ABOVE STATEMENTS"
    Disclaimer1 = textwrap.fill(Disclaimer1, 90)
    Disclaimer2 = textwrap.fill(Disclaimer2, 90)
    Disclaimer3 = textwrap.fill(Disclaimer3, 90)
    Disclaimer4 = textwrap.fill(Disclaimer4, 90)
    Block = 0
    Activity = 0

    def _make_window(layoutA, title='Time and Labour'):
        layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                  [sg.VPush()]]
        win = sg.Window(title, layout, finalize=True, resizable=True)
        win.Maximize()
        return win

    btn_kwargs = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
    back_kwargs = dict(font=BTN_FONT, size=(12, 1), pad=BTN_PAD, button_color=('white', 'firebrick3'), border_width=2)

    #Define Functions for Repetative Tasks
    def SignalChecker(WorkerName):
        global SignalCalc
        WorkerStatusChecker = cursor.execute("""SELECT SUM(Signal) FROM WorkerTimeLog WHERE WorkerName = '%s';""" % WorkerName)
        WorkerStatusDataFrame = pd.DataFrame(WorkerStatusChecker, columns=['Signal'])
        SignalCalc = WorkerStatusDataFrame['Signal'].sum()
        print(SignalCalc)

    def WorkerLogIN(WorkerName):
        global event
        global values
        global Block
        global Activity
        if WorkerClass == 'SUPER':
            layoutA = [ [sg.Text(WorkerName, font=TITLE_FONT)],
                        [sg.Text('PLEASE READ THE FOLLOWING', font=HEADER_FONT)],
                        [sg.Text(Disclaimer1, font=DISCLAIMER_FONT)],
                        [sg.Text(Disclaimer2, font=DISCLAIMER_FONT)],
                        [sg.Text(Disclaimer3, font=DISCLAIMER_FONT)],
                        [sg.Text(Disclaimer4, font=DISCLAIMER_FONT)],
                        [sg.Button('Sign On', **btn_kwargs)],
                        [sg.Button('Back', **back_kwargs)]]
            window = _make_window(layoutA)
            event, values = window.read()

        if WorkerClass == 'CASUAL':
            SignalChecker(WorkerName)
            if int(SignalCalc) != 0 or SignalCalc == None:
                layoutA = [ [sg.Text(WorkerName, font=TITLE_FONT)],
                        [sg.Text('WORKER ALREADY SIGNED IN', font=WARN_FONT)],
                        [sg.Button('Ok', **btn_kwargs)]]
                window = _make_window(layoutA)
                event, values = window.read()
                if event == 'Ok':
                    window.close()
            else:
                layoutA = [ [sg.Text(WorkerName, font=TITLE_FONT)],
                            [sg.Text('PLEASE READ THE FOLLOWING', font=HEADER_FONT)],
                            [sg.Text(Disclaimer1, font=DISCLAIMER_FONT)],
                            [sg.Text(Disclaimer2, font=DISCLAIMER_FONT)],
                            [sg.Text(Disclaimer3, font=DISCLAIMER_FONT)],
                            [sg.Text(Disclaimer4, font=DISCLAIMER_FONT)],
                            [sg.Button('Sign On', **btn_kwargs)],
                            [sg.Button('Back', **back_kwargs)]]
                window = _make_window(layoutA)
                event, values = window.read()

        if WorkerClass == 'MACHINE':
            layoutA = [ [sg.Text(WorkerName, font=TITLE_FONT)],
                        [sg.Text('Please Select Block and Job Type', font=HEADER_FONT)],
                        [sg.Button('Sign On', **btn_kwargs)],
                        [sg.Button('Back', **back_kwargs)]]
            window = _make_window(layoutA)
            event, values = window.read()

        if event == 'Sign On':
            window.close()
            if WorkerClass == 'SUPER':
                WorkerCode = SuperDataFrame.loc[SuperDataFrame['Worker Name'] == WorkerName]
                WorkerCode = WorkerCode['Worker Code'].tolist()
                WorkerCode = WorkerCode[0]
            if WorkerClass == 'CASUAL':
                WorkerCode = CasualDataFrame.loc[CasualDataFrame['Worker Name'] == WorkerName]
                WorkerCode = WorkerCode['Worker Code'].tolist()
                WorkerCode = WorkerCode[0]
            if WorkerClass == 'MACHINE':
                WorkerCode = MachineDataFrame.loc[MachineDataFrame['Worker Name'] == WorkerName]
                WorkerCode = WorkerCode['Worker Code'].tolist()
                WorkerCode = WorkerCode[0]
            Action = 'LOGON'
            TimeStamp = datetime.datetime.now()
            Signal = 1
            EventList = [WorkerName, WorkerCode, Action, TimeStamp, Signal]
            EventDataFrame = pd.DataFrame(columns=['WorkerName', 'WorkerCode', 'Action', 'TimeStamp', 'Signal'])
            EventDataFrame.loc[len(EventDataFrame)] = EventList
            EventDataFrame.to_sql('WorkerTimeLog', con=engine, if_exists='append', index=False)
        if event == 'Back':
            window.close()

    def WorkerLogOUT(WorkerName):
        global event
        global values
        layoutA = [ [sg.Text(WorkerName, font=TITLE_FONT)],
                    [sg.Text('WORKER LOGGED IN', font=HEADER_FONT)],
                    [sg.Button('Sign OFF', **btn_kwargs)],
                    [sg.Button('Back', **back_kwargs)]]
        window = _make_window(layoutA)
        event, values = window.read()
        if event == 'Sign OFF':
            if WorkerClass == 'SUPER':
                WorkerCode = SuperDataFrame.loc[SuperDataFrame['Worker Name'] == WorkerName]
                WorkerCode = WorkerCode['Worker Code'].tolist()
                WorkerCode = WorkerCode[0]
            if WorkerClass == 'CASUAL':
                WorkerCode = CasualDataFrame.loc[CasualDataFrame['Worker Name'] == WorkerName]
                WorkerCode = WorkerCode['Worker Code'].tolist()
                WorkerCode = WorkerCode[0]
            if WorkerClass == 'MACHINE':
                WorkerCode = MachineDataFrame.loc[MachineDataFrame['Worker Name'] == WorkerName]
                WorkerCode = WorkerCode['Worker Code'].tolist()
                WorkerCode = WorkerCode[0]
            Action = 'LOGOFF'
            TimeStamp = datetime.datetime.now()
            Signal = -1
            EventList = [WorkerName, WorkerCode, Action, TimeStamp, Signal]
            EventDataFrame = pd.DataFrame(columns=['WorkerName', 'WorkerCode', 'Action', 'TimeStamp', 'Signal'])
            EventDataFrame.loc[len(EventDataFrame)] = EventList
            EventDataFrame.to_sql('WorkerTimeLog', con=engine, if_exists='append', index=False)
        if event == 'Back':
            window.close()

    def run_role_call():
        """Run role call for all casual staff not signed in and not already recorded today."""
        CurrentWorkingCasualQuery = cursor.execute("""SELECT WorkerName, SUM(Signal) FROM WorkerTimeLog WHERE WorkerCode = 'C2' OR WorkerCode = 'C3' GROUP BY WorkerName;""")
        CurrentWorkingCasualDataFrame = pd.DataFrame(CurrentWorkingCasualQuery, columns=['Name', 'Signal'])
        CurrentWorkingCasualDataFrame = CurrentWorkingCasualDataFrame.drop(CurrentWorkingCasualDataFrame[CurrentWorkingCasualDataFrame.Signal == 0].index)
        print(CurrentWorkingCasualDataFrame)
        CurrentWorkerList = CurrentWorkingCasualDataFrame['Name'].tolist()
        today_str = datetime.date.today().strftime('%Y-%m-%d')
        try:
            already_recorded_query = cursor.execute(
                """SELECT Worker FROM WorkerOff WHERE TimeStamp LIKE ?""",
                (today_str + '%',)
            )
            already_recorded = [row[0] for row in already_recorded_query.fetchall()]
        except Exception:
            already_recorded = []
        for StaffMemeber in CasualStaffList:
            if StaffMemeber not in CurrentWorkerList and StaffMemeber not in already_recorded:
                layoutA = [ [sg.Text(StaffMemeber + ' Not Signed In', font=HEADER_FONT)],
                            [sg.Text('Please Select Reason', font=BODY_FONT)],
                            make_touch_combo_row('Select Reason', 'Name'),
                            [sg.Button('Ok', **btn_kwargs)],
                            [sg.Button('Back', **back_kwargs)]]
                _combos_reason = {'Name': ('Select Reason', WorkerReasonList)}
                rc_window = _make_window(layoutA, 'Role Call')
                while True:
                    rc_event, rc_values = rc_window.read()
                    if handle_touch_combos(rc_event, rc_window, _combos_reason):
                        continue
                    break
                if rc_event == 'Ok':
                    rc_window.close()
                    TimeStamp = datetime.datetime.now()
                    DataList = [TimeStamp, StaffMemeber, rc_values['Name']]
                    cursor.execute("""INSERT INTO WorkerOff (TimeStamp, Worker, Reason) VALUES ('%s', '%s', '%s')""" % (DataList[0], DataList[1], DataList[2]))
                    sql_connect.commit()
                if rc_event == 'Back':
                    rc_window.close()

    #Open First Window
    Signal = 0
    while Signal < 1:
        layoutA = [ [sg.Text('Welcome To SantaRita Orchards', font=TITLE_FONT)],
                    [sg.Text('Please Select Worker Type', font=HEADER_FONT)],
                    [sg.Button('Casual Staff', **btn_kwargs)],
                    [sg.Button('Machine', **btn_kwargs)],
                    [sg.Button('Status Report', **btn_kwargs)],
                    [sg.Button('Close Day', **btn_kwargs)],
                    [sg.Button('Role Call', **btn_kwargs)],
                    [sg.VPush()],
                    [sg.Button('Back', **back_kwargs)]]
        window = _make_window(layoutA)
        event, values = window.read()

        if event == 'Supervisor':
            window.close()
            WorkerClass = 'SUPER'
            layoutA = [ [sg.Text('Supervisor', font=TITLE_FONT)],
                        [sg.Text('Please Select Worker', font=HEADER_FONT)],
                        [sg.Button('AlexR', **btn_kwargs)],
                        [sg.Button('Shaun', **btn_kwargs)],
                        [sg.Button('Back', **back_kwargs)]]
            window = _make_window(layoutA)
            event2, values = window.read()

            if event2 == 'AlexR':
                signal2 = 0
                window.close()
                WorkerName = event2
                SignalChecker(WorkerName)
                if SignalCalc == 0:
                    WorkerLogIN(WorkerName)
                if SignalCalc == 1:
                    WorkerLogOUT(WorkerName)

            if event2 == 'Shaun':
                signal2 = 0
                WorkerName = event2
                SignalChecker(WorkerName)
                if SignalCalc == 0:
                    WorkerLogIN(WorkerName)
                if SignalCalc == 1:
                    WorkerLogOUT(WorkerName)
            
        if event == 'Back':
            window.close()
            Signal += 1

        if event == 'Casual Staff':
            window.close()
            WorkerClass = 'CASUAL'
            signal2 = 0
            while signal2 < 1:
                layoutA = [ [sg.Text('Casual Staff', font=TITLE_FONT)],
                            [sg.Text('Select Worker or Press Finish Workers To Logout', font=BODY_FONT)],
                            make_touch_combo_row('Select Worker', 'Name'),
                            [sg.Button('Start Work', **btn_kwargs)],
                            [sg.Button('Finish Workers', **btn_kwargs)],
                            [sg.Button('Back', **back_kwargs)]]
                _combos_casual = {'Name': ('Select Worker', CasualStaffList)}
                window = _make_window(layoutA)
                while True:
                    event2, values = window.read()
                    if handle_touch_combos(event2, window, _combos_casual):
                        continue
                    break
                if event2 == 'Start Work':
                    window.close()
                    WorkerName = values['Name']
                    WorkerLogIN(WorkerName)
                if event2 == 'Back':
                    window.close()
                    run_role_call()
                    signal2 += 1
                if event2 == 'Finish Workers':
                    window.close()
                    signal3 = 0
                    while signal3 < 1:
                        CurrentWorkingCasualQuery = cursor.execute("""SELECT WorkerName, SUM(Signal) FROM WorkerTimeLog WHERE WorkerCode = 'C2' OR WorkerCode = 'C3' GROUP BY WorkerName;""")
                        CurrentWorkingCasualDataFrame = pd.DataFrame(CurrentWorkingCasualQuery, columns=['Name', 'Signal'])
                        CurrentWorkingCasualDataFrame = CurrentWorkingCasualDataFrame.drop(CurrentWorkingCasualDataFrame[CurrentWorkingCasualDataFrame.Signal == 0].index)
                        print(CurrentWorkingCasualDataFrame)
                        CurrentWorkingCasualList = CurrentWorkingCasualDataFrame['Name'].tolist()
                        layoutA = [ [sg.Text('Finish Workers', font=TITLE_FONT)],
                                    [sg.Text('Please Select Worker', font=HEADER_FONT)],
                                    make_touch_combo_row('Select Worker', 'Name'),
                                    [sg.Button('Finish Job', **btn_kwargs)],
                                    [sg.Button('Back', **back_kwargs)]]
                        _combos_finish = {'Name': ('Select Worker', CurrentWorkingCasualList)}
                        window = _make_window(layoutA)
                        while True:
                            event2, values = window.read()
                            if handle_touch_combos(event2, window, _combos_finish):
                                continue
                            break
                        if event2 == 'Finish Job':
                            window.close
                            WorkerName = values['Name']
                            WorkerLogOUT(WorkerName)
                        if event2 == 'Back':
                            signal3 += 1

        if event == 'Machine':
            window.close()
            WorkerClass = 'MACHINE'
            layoutA = [ [sg.Text('Machine', font=TITLE_FONT)],
                        [sg.Text('Please Select Machine', font=HEADER_FONT)],
                        [sg.Button('Babini', **btn_kwargs)],
                        [sg.Button('Platform', **btn_kwargs)],
                        [sg.Button('Squirrel 1', **btn_kwargs)],
                        [sg.Button('Squirrel 2', **btn_kwargs)],
                        [sg.Button('Back', **back_kwargs)]]
            window = _make_window(layoutA)
            event2, values = window.read()
            if event2 == 'Babini':
                window.close()
                WorkerName = 'Babini'
                SignalChecker(WorkerName)
                if SignalCalc == 0:
                    WorkerLogIN(WorkerName)
                if SignalCalc == 1:
                    WorkerLogOUT(WorkerName)
            if event2 == 'Platform':
                window.close()
                WorkerName = 'Platform'
                SignalChecker(WorkerName)
                if SignalCalc == 0:
                    WorkerLogIN(WorkerName)
                if SignalCalc == 1:
                    WorkerLogOUT(WorkerName)
            if event2 == 'Squirrel 1':
                window.close
                WorkerName = 'Squirrel 1'
                SignalChecker(WorkerName)
                if SignalCalc == 0:
                    WorkerLogIN(WorkerName)
                if SignalCalc == 1:
                    WorkerLogOUT(WorkerName)
            if event2 == 'Squirrel 2':
                window.close()
                WorkerName = 'Squirrel 2'
                SignalChecker(WorkerName)
                if SignalCalc == 0:
                    WorkerLogIN(WorkerName)
                if SignalCalc == 1:
                    WorkerLogOUT(WorkerName)
            if event2 == 'Back':
                window.close()

        if event == 'Close Day':
            window.close()
            CurrentWorkingCasualQuery = cursor.execute("""SELECT WorkerName, SUM(Signal) FROM WorkerTimeLog;""")
            CurrentWorkingCasualDataFrame = pd.DataFrame(CurrentWorkingCasualQuery, columns=['Name', 'Signal'])
            WorkerLogInCheck = CurrentWorkingCasualDataFrame['Signal'].sum()
            if WorkerLogInCheck != 0:
                CurrentWorkingCasualQuery = cursor.execute("""SELECT WorkerName, SUM(Signal) FROM WorkerTimeLog GROUP BY WorkerName;""")
                CurrentWorkingCasualDataFrame = pd.DataFrame(CurrentWorkingCasualQuery, columns=['Name', 'Signal'])
                CurrentWorkingCasualDataFrame = CurrentWorkingCasualDataFrame.drop(CurrentWorkingCasualDataFrame[CurrentWorkingCasualDataFrame.Signal == 0].index)
                headers = {'Name':[], 'Signal':[]}
                headings = list(headers)
                values = CurrentWorkingCasualDataFrame.values.tolist()
                layoutA = [ [sg.Text('Close Day', font=TITLE_FONT)],
                            [sg.Text('NOT ALL WORKERS ARE SIGNED OUT', font=WARN_FONT)],
                            [sg.Table(values=values, headings=headings, font=TABLE_FONT)],
                            [sg.Button('Back', **back_kwargs)]]
                window = _make_window(layoutA)
                event2, values = window.read()
            if WorkerLogInCheck == 0:
                layoutA = [ [sg.Text('Close Day', font=TITLE_FONT)],
                            [sg.Text('WORK DAY CLOSED OFF', font=WARN_FONT)],
                            [sg.Text('THANK YOU, DRIVE SAFE', font=WARN_FONT)],
                            [sg.Button('FINISH', **btn_kwargs)]]
                window = _make_window(layoutA)
                event2, values = window.read()
                if event2 == 'FINSIH':
                    sys.exit()

        if event == 'Status Report':
            window.close()
            CurrentWorkingCasualQuery = cursor.execute("""SELECT WorkerName, SUM(Signal) FROM WorkerTimeLog GROUP BY WorkerName;""")
            CurrentWorkingCasualDataFrame = pd.DataFrame(CurrentWorkingCasualQuery, columns=['Name', 'Signal'])
            CurrentWorkingCasualDataFrame = CurrentWorkingCasualDataFrame.drop(CurrentWorkingCasualDataFrame[CurrentWorkingCasualDataFrame.Signal == 0].index)
            headers = {'Name':[], 'Signal':[]}
            headings = list(headers)
            values = CurrentWorkingCasualDataFrame.values.tolist()
            layoutA = [ [sg.Text('Status Report', font=TITLE_FONT)],
                        [sg.Text('Current Logged In Workers', font=HEADER_FONT)],
                        [sg.Table(values=values, headings=headings, font=TABLE_FONT)],
                        [sg.Button('Back', **back_kwargs)]]
            window = _make_window(layoutA)
            event2, values = window.read()
            if event2 == 'Back':
                window.close()


        if event == 'Role Call':
            run_role_call()
