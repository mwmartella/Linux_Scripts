from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import PySimpleGUI as sg
import datetime
import sys
import textwrap
import TimeLog
import RowJob2
import CherryHarvest
import platform
#Start Up Database engines....... Vroom+
SignalDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/SPLITSIGNAL.xlsx')

CompName = platform.node()
print(CompName)
DB1 = "sqlite:///" + CompName + " TimeSheetLocal.db"
DB2 = CompName + " TimeSheetLocal.db"

#Start Up Database engines....... Vroom
engine = create_engine(DB1) 
sql_connect = sqlite3.connect(DB2)
cursor = sql_connect.cursor()

engine2 = create_engine("sqlite:///TimeSheetGlobal.db") 
sql_connect2 = sqlite3.connect('TimeSheetGlobal.db')
cursor2 = sql_connect.cursor()

engine3 = create_engine("sqlite:///RowJobQa.db") 
sql_connect3 = sqlite3.connect('RowJobQa.db')
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
