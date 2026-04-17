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
import PySimpleGUI as sg
import datetime
import sys
import textwrap
import platform
#Start Up Database engines....... Vroom
CompName = platform.node()
print(CompName)
DB1 = "sqlite:///" + CompName + " TimeSheetLocal.db"
DB2 = CompName + " TimeSheetLocal.db"
SignalDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/SPLITSIGNAL.xlsx')
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
    engine2 = create_engine("sqlite:///TimeSheetGlobal.db") 
    sql_connect2 = sqlite3.connect('TimeSheetGlobal.db')
    cursor2 = sql_connect.cursor()
    #Compile DataFrames
    SuperDataFrame = pd.read_excel('Worker Data\\SUPERVISORS.xlsx')
    CasualDataFrame = pd.read_excel('Worker Data\\CASUAL STAFF.xlsx')
    MachineDataFrame = pd.read_excel('Worker Data\\MACHINES.xlsx')
    RatesDataFrame = pd.read_excel('Worker Data\\PAYRATES.xlsx')
    #Global Variable, Lists and Dicts
    #JobTypeList = ['Picking', 'Pruning', 'Thinning', 'Establish Planting', 'Tree Training', 'Packing', 'Irrigation Maintinance']
    #JobTypeDict = {'Picking': 'PK', 'Pruning': 'PR', 'Thinning': 'TH', 'Establish Planting': 'EP', 'Tree Training': 'TT', 'Packing': 'PA', 'Irrigation Maintinance': 'IM'}
    #BlockList = ["S-SHED PL", "S-SHED SD", "S-SHED Gala", "Pink Belle", "STK GS", "STK LIR", "Rob Bravo", "Cherry Bravo", "GSPL GS", "GSPL PL", "Total PL", "Modi", "Rainier", "Van", "Lapin", "Chelan", "Merchant", "DWF PL", "DWF GS", "LIR18", "LIR19", "BGGS - Bravo", "BGGS - GS", "BGGS - Gala", "WPL - PL", "WPL - GS"]
    #BlockDict = {"B2": "S-SHED PL", "B3": "S-SHED SD", "B4": "S-SHED Gala", "C2": "Pink Belle", "D3": "STK GS", "D4": "STK LIR", "E1": "Rob Bravo", "F1": "Cherry Bravo", "H2": "GSPL GS", "H3": "GSPL PL", "I1": "Total PL", "J1": "Modi", "N2": "Rainier", "N3": "Van", "N5": "Lapin", "N6": "Chelan", "N7": "Merchant", "Q1": "DWF PL", "Q2": "DWF GS", "R1": "LIR18", "S1": "LIR19", "WC2": "BGGS - Bravo", "WC3": "BGGS - GS", "WC4": "BGGS - Gala", "WD2": "WPL - PL", "WD3": "WPL - GS"}
    WorkerClass = 0
    CasualStaffList = CasualDataFrame['Worker Name'].tolist()
    Disclaimer1 = """FIT FOR WORK - For my own safety and the safety of others, I agree to present fit for work, not under the influence of alcohol or illicit or illegal drugs. I will not consume/use alcohol, illicit or illegal drugs whilst at work. If I am using prescription or over the counter medication that I have been advised by my GP/Chemist, or it is noted on the medication packaging “not to operate machinery or potential to cause effect to operating impairment/ judgement” or in Safety Sensitive Roles and Positions or if I am in any doubt, I will inform my Supervisor immediately."""
    Disclaimer2 = """FATIGUE - I agree to notify my Supervisor immediately if I am or believe that I am suffering fatigue through Lack of sleep, Illness, Personal Issues or other reasons."""
    Disclaimer3 = """SWMS - I have access to and have read and understand the task specific section in the Safe Work Method Statement (SWMS) for the job/s that I will be undertaking and I agree to work within these guidelines. If I am unable to work within these guidelines, I will contact my Supervisor immediately for instructions."""
    Disclaimer4 = "BY SIGNING IN FOR WORK YOU ARE DECLARING THE ABOVE STATEMENTS"
    Disclaimer1 = textwrap.fill(Disclaimer1, 80)
    Disclaimer2 = textwrap.fill(Disclaimer2, 80)
    Disclaimer3 = textwrap.fill(Disclaimer3, 80)
    Disclaimer4 = textwrap.fill(Disclaimer4, 80)
    Block = 0
    Activity = 0
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
            layoutA = [  [sg.Text(WorkerName, font=("", 25, "bold"))],
                        [sg.Text('PLEASE READ THE FOLLOWING', font=("", 30, "bold"))],
                        [sg.Text(Disclaimer1, font=("", 15, "bold"))],
                        [sg.Text(Disclaimer2, font=("", 15, "bold"))],
                        [sg.Text(Disclaimer3, font=("", 15, "bold"))],
                        [sg.Text(Disclaimer4, font=("", 15, "bold"))],
                        [sg.Button('Sign On', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
            layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
            window = sg.Window('Time and Labour', layout).Finalize()
            window.Maximize()
            event, values = window.read()

        if WorkerClass == 'CASUAL':
            SignalChecker(WorkerName)
            if int(SignalCalc) != 0 or SignalCalc == None:
                layoutA = [  [sg.Text(WorkerName, font=("", 25, "bold"))],
                        [sg.Text('WORKER ALREADY SIGNED IN', font=("", 50, "bold"))],
                        [sg.Button('Ok', font=("", 35, "bold"))]]
                layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                window = sg.Window('Time and Labour', layout).Finalize()
                window.Maximize()
                event, values = window.read()
                if event == 'Ok':
                    window.close()
            else:
                layoutA = [  [sg.Text(WorkerName, font=("", 25, "bold"))],
                            [sg.Text('PLEASE READ THE FOLLOWING', font=("", 50, "bold"))],
                            [sg.Text(Disclaimer1, font=("", 15, "bold"))],
                            [sg.Text(Disclaimer2, font=("", 15, "bold"))],
                            [sg.Text(Disclaimer3, font=("", 15, "bold"))],
                            [sg.Text(Disclaimer4, font=("", 15, "bold"))],
                            [sg.Button('Sign On', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
                layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                window = sg.Window('Time and Labour', layout).Finalize()
                window.Maximize()
                event, values = window.read()
        if WorkerClass == 'MACHINE':
            layoutA = [  [sg.Text(WorkerName, font=("", 25, "bold"))],
                        [sg.Text('Please Select Block and Job Type', font=("", 50, "bold"))],
                        [sg.Button('Sign On', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
            layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
            window = sg.Window('Time and Labour', layout).Finalize()
            window.Maximize()
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
        layoutA = [  [sg.Text(WorkerName, font=("", 25, "bold"))],
                    [sg.Text('WORKER LOGGED IN', font=("", 30, "bold"))],
                    [sg.Button('Sign OFF', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
        layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
        window = sg.Window('Time and Labour', layout).Finalize()
        window.Maximize()
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
            EventDataFrame.to_sql('WorkerTimeLog', con=engine, if_exists='append', index=False)#########################################################
        if event == 'Back':
            window.close()
    #Open First Window
    Signal = 0
    while Signal < 1:
        layoutA = [  [sg.Text('Welcome To SantaRita Orchards Time and Labour App', font=("", 25, "bold"))],
                            [sg.Text('Please Select Worker Type', font=("", 50, "bold"))],
                            [sg.Button('Casual Staff', font=("", 25, "bold"))],
                            [sg.Button('Machine', font=("", 25, "bold"))],
                            [sg.Button('Status Report', font=("", 25, "bold"))],
                            [sg.Button('Close Day', font=("", 25, "bold"))],
                            [sg.Button('Role Call', font=("", 25, "bold"))],
                            [sg.Button('Back', font=("", 25, "bold"))]]
        layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
        window = sg.Window('Time and Labour', layout).Finalize()
        window.Maximize()
        event, values = window.read()

        if event == 'Supervisor':
            window.close()
            WorkerClass = 'SUPER'
            layoutA = [  [sg.Text('Supervisor', font=("", 25, "bold"))],
                            [sg.Text('Please Select Worker', font=("", 50, "bold"))],
                            [sg.Button('AlexR', font=("", 25, "bold"))],
                            [sg.Button('Shaun', font=("", 25, "bold"))],
                            [sg.Button('Back', font=("", 25, "bold"))]]
            layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
            window = sg.Window('Time and Labour', layout).Finalize()
            window.Maximize()
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
                layoutA = [  [sg.Text('Supervisor', font=("", 25, "bold"))],
                                [sg.Text('Please Select Worker or Press Finish Workers To Enter LogoutScreen', font=("", 50, "bold"))],
                                [sg.Combo(CasualStaffList, default_value = 'Worker', size = 50, key = 'Name', font=("", 35, "bold"))],
                                [sg.Button('Start Work', font=("", 25, "bold"))], [sg.Button('Finish Workers', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
                layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                window = sg.Window('Time and Labour', layout).Finalize()
                window.Maximize()
                event2, values = window.read()
                if event2 == 'Start Work':
                    window.close()
                    WorkerName = values['Name']
                    WorkerLogIN(WorkerName)
                if event2 == 'Back':
                    window.close()
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
                        layoutA = [  [sg.Text('Supervisor', font=("", 25, "bold"))],
                                    [sg.Text('Please Select Worker', font=("", 50, "bold"))],
                                    [sg.Combo(CurrentWorkingCasualList, default_value = 'Worker', size = 30, key = 'Name', font=("", 30, "bold"))],
                                    [sg.Button('Finish Job', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
                        layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                        window = sg.Window('Time and Labour', layout).Finalize()
                        window.Maximize()
                        event2, values = window.read()
                        if event2 == 'Finish Job':
                            window.close
                            WorkerName = values['Name']
                            WorkerLogOUT(WorkerName)
                        if event2 == 'Back':
                            signal3 += 1
        if event == 'Machine':
            window.close()
            WorkerClass = 'MACHINE'
            layoutA = [  [sg.Text('Machine', font=("", 25, "bold"))],
                            [sg.Text('Please Select Machine', font=("", 50, "bold"))],
                            [sg.Button('Babini', font=("", 25, "bold"))],
                            [sg.Button('Platform', font=("", 25, "bold"))],
                            [sg.Button('Squirrel 1', font=("", 25, "bold"))],
                            [sg.Button('Squirrel 2', font=("", 25, "bold"))],
                            [sg.Button('Back', font=("", 25, "bold"))]]
            layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
            window = sg.Window('Time and Labour', layout).Finalize()
            window.Maximize()
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
                layoutA = [  [sg.Text('Supervisor', font=("", 25, "bold"))],
                                [sg.Text('NOT ALL WORKERS ARE SIGNED OUT', font=("", 48, "bold"))],
                                [sg.Table(values = values, headings = headings, font=("", 25, "bold"))],
                                [sg.Button('Back', font=("", 50, "bold"))]]
                layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                window = sg.Window('Time and Labour', layout).Finalize()
                window.Maximize()
                event2, values = window.read()
            if WorkerLogInCheck == 0:
                layoutA = [  [sg.Text('Supervisor', font=("", 25, "bold"))],
                                [sg.Text('WORK DAY CLOSED OFF', font=("", 48, "bold"))],
                                [sg.Text('THANK YOU, DRIVE SAFE', font=("", 48, "bold"))],
                                [sg.Button('FINISH', font=("", 50, "bold"))]]
                layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                window = sg.Window('Time and Labour', layout).Finalize()
                window.Maximize()
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
            layoutA = [  [sg.Text('Supervisor', font=("", 25, "bold"))],
                            [sg.Text('Current Logged In Workers', font=("", 48, "bold"))],
                            [sg.Table(values = values, headings = headings, font=("", 25, "bold"))],
                            [sg.Button('Back', font=("", 50, "bold"))]]
            layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
            window = sg.Window('Time and Labour', layout).Finalize()
            window.Maximize()
            event2, values = window.read()
            if event2 == 'Back':
                window.close()
        if event == 'Role Call':
            event == 0
            CurrentWorkingCasualQuery = cursor.execute("""SELECT WorkerName, SUM(Signal) FROM WorkerTimeLog WHERE WorkerCode = 'C2' OR WorkerCode = 'C3' GROUP BY WorkerName;""")
            CurrentWorkingCasualDataFrame = pd.DataFrame(CurrentWorkingCasualQuery, columns=['Name', 'Signal'])
            CurrentWorkingCasualDataFrame = CurrentWorkingCasualDataFrame.drop(CurrentWorkingCasualDataFrame[CurrentWorkingCasualDataFrame.Signal == 0].index)
            print(CurrentWorkingCasualDataFrame)
            CurrentWorkerList = CurrentWorkingCasualDataFrame['Name'].tolist()
            for StaffMemeber in CasualStaffList:
                if StaffMemeber not in CurrentWorkerList:
                    layoutA = [  [sg.Text(StaffMemeber + ' Not Signed In', font=("", 50, "bold"))],
                                    [sg.Text('Please Select Reason', font=("", 25, "bold"))],
                                    [sg.Combo(WorkerReasonList, default_value = 'Reason', size = 30, key = 'Name', font=("", 30, "bold"))],
                                    [sg.Button('Ok', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
                    layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                    window = sg.Window('Role Call', layout).Finalize()
                    window.Maximize()
                    event2, values = window.read()
                    if event2 == 'Ok':
                        window.close()
                        TimeStamp = datetime.datetime.now()
                        DataList = [TimeStamp, StaffMemeber, values['Name']]
                        cursor.execute("""INSERT INTO WorkerOff (TimeStamp, Worker, Reason) VALUES ('%s', '%s', '%s')""" % (DataList[0], DataList[1], DataList[2]))
                        sql_connect.commit()
                    if event2 == 'Back':
                        window.close()
