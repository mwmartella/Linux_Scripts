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

MasterSignal = 0
while MasterSignal < 1:
    layoutA = [  [sg.Text('Field Manager', font=("", 50, "bold"))],
                        [sg.Text('Please Select Supervisor Task', font=("", 35, "bold"))],
                        [sg.Button('Timesheet Log', font=("", 25, "bold"))],
                        [sg.Button('Row Job Manager', font=("", 25, "bold"))],
                        [sg.Button('Cherry Harvest Manager', font=("", 25, "bold"))],
                        [sg.Button('Apple Harvest Manager', font=("", 25, "bold"))],
                        [sg.Button('Status Report', font=("", 25, "bold"))],
                        [sg.Button('Quit', font=("", 25, "bold"))]]
    layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
    window = sg.Window('Time and Labour', layout).Finalize()
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
