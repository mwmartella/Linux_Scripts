from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import PySimpleGUI as sg
import datetime
import sys
import textwrap

FieldList = ['WISHARTS - PL', 'WISHARTS - BRAVO', 'CHERRYS', 'CHERRY BRAVO', 'S-SHED', 'STK', 'P-BELLE', 'LIR', 'ROB BRAVO', 'MODI', 'DWF', 'GSPL', 'TOTAL']
BlockDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/BlockData/BLOCKDATA.xlsx')
SuperDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/SUPERVISORS.xlsx')
CasualDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/CASUAL STAFF.xlsx')
MachinesDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/MACHINES.xlsx')
VarietyDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/BlockData/VARIETY.xlsx')
VarietyList = VarietyDataFrame['VARIETY'].tolist()


QACHECKLIST = ['All Good', 'Missed Work - Sent Back', 'Work Too Heavy', 'Work Too Light', 'Worker Issues']
JobTypeList = ['Picking', 'Pruning', 'Thinning', 'Establish Planting', 'Tree Training', 'Packing', 'Irrigation Maintinance']

engine = create_engine("sqlite:///TimeSheetLocal.db") 
sql_connect = sqlite3.connect('TimeSheetLocal.db')
cursor = sql_connect.cursor()

engine2 = create_engine("sqlite:///RowJobQa.db") 
sql_connect2 = sqlite3.connect('RowJobQa.db')
cursor2 = sql_connect2.cursor()

def StatusRport(Field):
    CurrentRowLog = cursor.execute("""SELECT Field, Row, Worker, Variety, SUM(Signal) FROM WorkerRowLog WHERE Field = '%s' GROUP BY Worker, Row;""" % Field)
    CurrentRowLogFrame = pd.DataFrame(CurrentRowLog, columns=['Field', 'Row', 'Worker', 'Variety', 'Signal'])
    CurrentRowLogFilter = CurrentRowLogFrame.loc[CurrentRowLogFrame['Signal'] == 1]
    headers = {'Field':[], 'Row':[], 'Worker':[], 'Variety':[], 'Signal':[]}
    headings = list(headers)
    values = CurrentRowLogFilter.values.tolist()
    layoutB = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                            [sg.Text('Row Job Status for ' + Field + ' ' + RowNumber, font=("", 30, "bold"))],
                            [sg.Table(values = values, headings = headings, font=("", 25, "bold"))],
                            [sg.Button('Back', font=("", 35, "bold"))]]
    window = sg.Window('Time and Labour', layoutB).Finalize()
    window.Maximize()
    event, values = window.read()
    if event == 'Back':
        window.close()

def ActionLog():
    global JobType
    global Field
    global RowNumber
    TotalWorkerList = []
    RowLogDataFrame = pd.DataFrame(columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety'])
    WorkerLoop = 0
    TotalWorkerListQuery = cursor.execute("""SELECT WorkerName FROM WorkerTimeLog;""" )
    TotalWorkerListDataFrame = pd.DataFrame(TotalWorkerListQuery, columns=['Worker'])
    print(TotalWorkerListDataFrame)
    TotalWorkerList = TotalWorkerListDataFrame['Worker'].tolist()
    TotalWorkerList = list(dict.fromkeys(TotalWorkerList))
    if 'AlexR' not in TotalWorkerList:
        TotalWorkerList.append('AlexR')
    if 'Shaun' not in TotalWorkerList:
        TotalWorkerList.append('Shaun')
    while WorkerLoop < 1:
        layoutB = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                [sg.Text('Select Worker', font=("", 30, "bold"))],
                [sg.Combo(TotalWorkerList, default_value = 'Worker', size = 50, key = 'Worker', font=("", 35, "bold"))],
                [sg.Button('Start', font=("", 35, "bold"))], [sg.Button('End', font=("", 35, "bold"))], [sg.Button('Back', font=("", 35, "bold"))], [sg.Button('Finish Row', font=("", 35, "bold"))]]
        window = sg.Window('Time and Labour', layoutB).Finalize()
        window.Maximize()
        event, values = window.read()
        Worker = values['Worker']
        CurrentWorkingQuery = cursor.execute("""SELECT Worker, Row, SUM(Signal) FROM WorkerRowLog WHERE Worker = '%s' AND Row = '%s';""" % (Worker, RowNumber))
        CurrentWorkingDataFrame = pd.DataFrame(CurrentWorkingQuery, columns=['Name', 'Row', 'Signal'])
        WorkerLogInCheck = CurrentWorkingDataFrame['Signal'].sum()
        if event == 'Start':
            window.close()
            if WorkerLogInCheck == 1:
                CurrentWorkingQuery = cursor.execute("""SELECT Worker, Row FROM WorkerRowLog WHERE Worker = '%s' AND Signal = '1';""" % Worker)
                CurrentWorkingDataFrame = pd.DataFrame(CurrentWorkingQuery, columns=['Worker', 'Row'])
                WorkerBlockFinder = CurrentWorkingDataFrame['Worker'].tolist()
                BlockFinder = CurrentWorkingDataFrame['Row'].tolist()
                indexneeded = len(WorkerBlockFinder) - 1
                Block = BlockFinder[indexneeded]
                layoutZ = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                [sg.Text('WORKER ALREADY LOGGED INTO A ROW', font=("", 30, "bold"))],
                [sg.Text(Worker + ' is in row ' + Block, font=("", 30, "bold"))],
                [sg.Button('Return', font=("", 35, "bold"))], [sg.Button('Log In Anyway', font=("", 35, "bold"))],]
                window = sg.Window('Time and Labour', layoutZ).Finalize()
                window.Maximize()
                event, values = window.read()
                if event == 'Return':
                    window.close()
            if WorkerLogInCheck == 0 or event == 'Log In Anyway':
                Action = 'Start'
                TimeStamp = datetime.datetime.now()
                Signal = 1
                DataList = [Field, RowNumber, Worker, Action, TimeStamp, Signal, Variety]
                RowLogDataFrame.loc[len(RowLogDataFrame)] = DataList
                RowLogDataFrame.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
                RowLogDataFrame = pd.DataFrame(columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety'])
        if event == 'End':
            window.close()
            if WorkerLogInCheck == 0:
                layoutZ = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                [sg.Text('WORKER IS NOT CURRENTLY LOGGED INTO A ROW', font=("", 30, "bold"))],
                [sg.Button('Return', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutZ).Finalize()
                window.Maximize()
                event, values = window.read()
                if event == 'Return':
                    window.close()
            else:
                Worker = values['Worker']
                Action = 'Finish'
                TimeStamp = datetime.datetime.now()
                Signal = -1
                DataList = [Field, RowNumber, Worker, Action, TimeStamp, Signal, Variety]
                RowLogDataFrame.loc[len(RowLogDataFrame)] = DataList
                RowLogDataFrame.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
                RowLogDataFrame = pd.DataFrame(columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety'])
        if event == 'Back':
            window.close()
            WorkerLoop += 1
        if event == 'Finish Row':
            window.close()
            CurrentWorkingQuery = cursor.execute("""SELECT Signal FROM WorkerRowLog WHERE Row = '%s';""" % RowNumber)
            CurrentWorkingDataFrame = pd.DataFrame(CurrentWorkingQuery, columns=['Signal'])
            RowWorkerTest = CurrentWorkingDataFrame['Signal'].sum()
            if RowWorkerTest != 0:
                WorkerList100 = []
                CurrentWorkingQuery = cursor.execute("""SELECT Worker, SUM(Signal) FROM WorkerRowLog WHERE Row = '%s' GROUP BY Worker;""" % RowNumber)
                CurrentWorkingDataFrame = pd.DataFrame(CurrentWorkingQuery, columns=['Worker', "SUM(Signal)"])
                print(CurrentWorkingDataFrame)
                CurrentWorkingDataFrame22 = CurrentWorkingDataFrame['Worker'].tolist()
                CurrentWorkingDataFrame22 = list(dict.fromkeys(CurrentWorkingDataFrame22))
                for Worker300 in CurrentWorkingDataFrame22:
                    print(Worker300)
                    CurrentWorkingDataFrame33 = CurrentWorkingDataFrame.loc[CurrentWorkingDataFrame['Worker'] == Worker300]
                    print(CurrentWorkingDataFrame33)
                    WorkerLogInCount = CurrentWorkingDataFrame33['SUM(Signal)'].sum()
                    print(WorkerLogInCount)
                    if WorkerLogInCount == 1:
                        WorkerList100.append(Worker300)
                workerstring = ''
                for Worker100 in WorkerList100:
                    workerstring = workerstring + ' ' + Worker100 + ','
                layoutZ = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                [sg.Text('ROW STILL HAS WORKERS LOGGED IN', font=("", 30, "bold"))],
                [sg.Text('Workers = ' + workerstring, font=("", 30, "bold"))],
                [sg.Button('Return', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutZ).Finalize()
                window.Maximize()
                event, values = window.read()
                if event == 'Return':
                    window.close()
            elif RowWorkerTest == 0:
                layoutZ = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                [sg.Text('ROW FINISH - QA CHECK', font=("", 30, "bold"))],
                [sg.Text('After Row Has Been Finshed Please Select Quality of Row', font=("", 30, "bold"))],
                [sg.Combo(QACHECKLIST, default_value = 'QA', size = 50, key = 'QA', font=("", 35, "bold"))],
                [sg.Button('Finish', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutZ).Finalize()
                window.Maximize()
                event, values = window.read()
                if event == 'Finish':
                    window.close()
                    RowQADataFrame = pd.DataFrame(columns=['Date', 'Field', 'Row', 'Job', 'Worker', 'QA', 'Variety'])
                    CurrentWorkingQuery = cursor.execute("""SELECT Worker FROM WorkerRowLog WHERE Row = '%s';""" % RowNumber)
                    CurrentWorkingDataFrame = pd.DataFrame(CurrentWorkingQuery, columns=['Worker'])
                    CurrentWorkingDataFrame = CurrentWorkingDataFrame['Worker'].tolist()
                    CurrentWorkingList = list(dict.fromkeys(CurrentWorkingDataFrame))
                    print(CurrentWorkingList)
                    for Worker200 in CurrentWorkingList:
                        TimeStamp = datetime.datetime.now()
                        QA = values['QA']
                        DataList = [TimeStamp, Field, RowNumber, JobType, Worker200, QA, Variety]
                        RowQADataFrame.loc[len(RowQADataFrame)] = DataList
                        print(DataList)
                    RowQADataFrame.to_sql('COLUMNS', con=engine2, if_exists='append', index=False)
def RowJob():
    global JobType
    global Field
    global RowNumber
    global Worker
    global Variety
    layoutA = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                        [sg.Text('Please Select Field', font=("", 35, "bold"))],
                        [sg.Combo(FieldList, default_value = 'Field', size = 50, key = 'Field', font=("", 35, "bold"))],
                        [sg.Combo(JobTypeList, default_value = 'Job', size = 50, key = 'Job', font=("", 35, "bold"))],
                        [sg.Combo(VarietyList, default_value = 'Variety', size = 50, key = 'Variety', font=("", 30, "bold"))],
                        [sg.Button('Start', font=("", 25, "bold"))], [sg.Button('Back', font=("", 25, "bold"))]]
    layout = [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
    window = sg.Window('Time and Labour', layout).Finalize()
    window.Maximize()
    event, values = window.read()
    if event == 'Back':
        window.close()
    if event == 'Start':
        window.close()
        Field = values['Field']
        JobType = values['Job']
        Variety = values['Variety']
        print(Field)
        FieldLoop = 0
        while FieldLoop < 1:
            if Field == 'P-BELLE' or Field == 'TOTAL':
                event == 0
                layoutB = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                            [sg.Text('Welcome To ' + Field, font=("", 30, "bold"))],
                            [sg.Button('R01', font=("", 30, "bold"), key='row'), sg.Button('R02', font=("", 30, "bold"), key='row'), sg.Button('R03', font=("", 30, "bold"), key='row'), sg.Button('R04', font=("", 30, "bold"), key='row'), sg.Button('R05', font=("", 30, "bold"), key='row'),
                            sg.Button('R06', font=("", 30, "bold"), key='row'), sg.Button('R07', font=("", 30, "bold"), key='row'), sg.Button('R08', font=("", 30, "bold"), key='row'), sg.Button('R09', font=("", 30, "bold"), key='row'), sg.Button('R10', font=("", 30, "bold"), key='row')],
                            [sg.Button('Status Report', font=("", 35, "bold"))], [sg.Button('Back', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutB).Finalize()
                window.Maximize()
                event, values = window.read()
                RowNumber = window[event].get_text()
                if event == 'Status Report':
                    window.close()
                    StatusRport(Field)
                if event == "Back":
                    window.close()
                    FieldLoop += 1
                if event != 0:
                    window.close()
                    ActionLog()
            if Field == 'CHERRYS' or Field == 'CHERRY BRAVO' or Field == 'WISHARTS - PL':
                layoutC = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                            [sg.Text('Welcome To ' + Field, font=("", 30, "bold"))],
                            [sg.Button('R01', font=("", 30, "bold")), sg.Button('R02', font=("", 30, "bold")), sg.Button('R03', font=("", 30, "bold")), sg.Button('R04', font=("", 30, "bold")), sg.Button('R05', font=("", 30, "bold")),
                            sg.Button('R06', font=("", 30, "bold")), sg.Button('R07', font=("", 30, "bold")), sg.Button('R08', font=("", 30, "bold")), sg.Button('R09', font=("", 30, "bold")), sg.Button('R10', font=("", 30, "bold"))],
                            [sg.Button('R11', font=("", 30, "bold")), sg.Button('R12', font=("", 30, "bold")), sg.Button('R13', font=("", 30, "bold")), sg.Button('R14', font=("", 30, "bold")), sg.Button('R15', font=("", 30, "bold")),
                            sg.Button('R16', font=("", 30, "bold")), sg.Button('R17', font=("", 30, "bold")), sg.Button('R18', font=("", 30, "bold")), sg.Button('R19', font=("", 30, "bold")), sg.Button('R20', font=("", 30, "bold"))],
                            [sg.Button('Status Report', font=("", 35, "bold"))], [sg.Button('Back', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutC).Finalize()
                window.Maximize()
                event, values = window.read()
                RowNumber = window[event].get_text()
                if event == 'Status Report':
                    window.close()
                    StatusRport(Field)
                if event == "Back":
                    window.close()
                    FieldLoop += 1
                if event != 0:
                    window.close()
                    ActionLog()
            if Field == 'S-SHED':
                layoutD = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                            [sg.Text('Welcome To ' + Field, font=("", 30, "bold"))],
                            [sg.Button('R01', font=("", 30, "bold")), sg.Button('R02', font=("", 30, "bold")), sg.Button('R03', font=("", 30, "bold")), sg.Button('R04', font=("", 30, "bold")), sg.Button('R05', font=("", 30, "bold")),
                            sg.Button('R06', font=("", 30, "bold")), sg.Button('R07', font=("", 30, "bold")), sg.Button('R08', font=("", 30, "bold")), sg.Button('R09', font=("", 30, "bold")), sg.Button('R10', font=("", 30, "bold"))],
                            [sg.Button('R11', font=("", 30, "bold")), sg.Button('R12', font=("", 30, "bold")), sg.Button('R13', font=("", 30, "bold")), sg.Button('R14', font=("", 30, "bold")), sg.Button('R15', font=("", 30, "bold")),
                            sg.Button('R16', font=("", 30, "bold")), sg.Button('R17', font=("", 30, "bold")), sg.Button('R18', font=("", 30, "bold")), sg.Button('R19', font=("", 30, "bold")), sg.Button('R20', font=("", 30, "bold"))],
                            [sg.Button('R21', font=("", 30, "bold")), sg.Button('R22', font=("", 30, "bold")), sg.Button('R23', font=("", 30, "bold")), sg.Button('R24', font=("", 30, "bold")), sg.Button('R25', font=("", 30, "bold")),
                            sg.Button('R26', font=("", 30, "bold")), sg.Button('R27', font=("", 30, "bold")), sg.Button('R28', font=("", 30, "bold")), sg.Button('R29', font=("", 30, "bold")), sg.Button('R30', font=("", 30, "bold"))],
                            [sg.Button('Status Report', font=("", 35, "bold"))], [sg.Button('Back', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutD).Finalize()
                window.Maximize()
                event, values = window.read()
                RowNumber = window[event].get_text()
                if event == 'Status Report':
                    window.close()
                    StatusRport(Field)
                if event == "Back":
                    window.close()
                    FieldLoop += 1
                if event != 0:
                    window.close()
                    ActionLog()
            if Field == 'WISHARTS - BRAVO' or Field == 'ROB BRAVO' or Field =='DWF' or Field == 'GSPL':
                layoutE = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                            [sg.Text('Welcome To ' + Field, font=("", 30, "bold"))],
                            [sg.Button('R01', font=("", 30, "bold")), sg.Button('R02', font=("", 30, "bold")), sg.Button('R03', font=("", 30, "bold")), sg.Button('R04', font=("", 30, "bold")), sg.Button('R05', font=("", 30, "bold")),
                            sg.Button('R06', font=("", 30, "bold")), sg.Button('R07', font=("", 30, "bold")), sg.Button('R08', font=("", 30, "bold")), sg.Button('R09', font=("", 30, "bold")), sg.Button('R10', font=("", 30, "bold"))],
                            [sg.Button('R11', font=("", 30, "bold")), sg.Button('R12', font=("", 30, "bold")), sg.Button('R13', font=("", 30, "bold")), sg.Button('R14', font=("", 30, "bold")), sg.Button('R15', font=("", 30, "bold")),
                            sg.Button('R16', font=("", 30, "bold")), sg.Button('R17', font=("", 30, "bold")), sg.Button('R18', font=("", 30, "bold")), sg.Button('R19', font=("", 30, "bold")), sg.Button('R20', font=("", 30, "bold"))],
                            [sg.Button('R21', font=("", 30, "bold")), sg.Button('R22', font=("", 30, "bold")), sg.Button('R23', font=("", 30, "bold")), sg.Button('R24', font=("", 30, "bold")), sg.Button('R25', font=("", 30, "bold")),
                            sg.Button('R26', font=("", 30, "bold")), sg.Button('R27', font=("", 30, "bold")), sg.Button('R28', font=("", 30, "bold")), sg.Button('R29', font=("", 30, "bold")), sg.Button('R30', font=("", 30, "bold"))],
                            [sg.Button('R31', font=("", 30, "bold")), sg.Button('R32', font=("", 30, "bold")), sg.Button('R33', font=("", 30, "bold")), sg.Button('R34', font=("", 30, "bold")), sg.Button('R35', font=("", 30, "bold")),
                            sg.Button('R36', font=("", 30, "bold")), sg.Button('R37', font=("", 30, "bold")), sg.Button('R38', font=("", 30, "bold")), sg.Button('R39', font=("", 30, "bold")), sg.Button('R40', font=("", 30, "bold"))],
                            [sg.Button('Status Report', font=("", 35, "bold"))], [sg.Button('Back', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutE).Finalize()
                window.Maximize()
                event, values = window.read()
                RowNumber = window[event].get_text()
                if event == 'Status Report':
                    window.close()
                    StatusRport(Field)
                if event == "Back":
                    window.close()
                    FieldLoop += 1
                if event != 0:
                    window.close()
                    ActionLog()
            if Field == 'STK' or Field == 'LIR' or Field == "MODI":
                layoutF = [  [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                                [sg.Text('Welcome To ' + Field, font=("", 30, "bold"))],
                                [sg.Button('R01', font=("", 30, "bold")), sg.Button('R02', font=("", 30, "bold")), sg.Button('R03', font=("", 30, "bold")), sg.Button('R04', font=("", 30, "bold")), sg.Button('R05', font=("", 30, "bold")),
                                sg.Button('R06', font=("", 30, "bold")), sg.Button('R07', font=("", 30, "bold")), sg.Button('R08', font=("", 30, "bold")), sg.Button('R09', font=("", 30, "bold")), sg.Button('R10', font=("", 30, "bold"))],
                                [sg.Button('R11', font=("", 30, "bold")), sg.Button('R12', font=("", 30, "bold")), sg.Button('R13', font=("", 30, "bold")), sg.Button('R14', font=("", 30, "bold")), sg.Button('R15', font=("", 30, "bold")),
                                sg.Button('R16', font=("", 30, "bold")), sg.Button('R17', font=("", 30, "bold")), sg.Button('R18', font=("", 30, "bold")), sg.Button('R19', font=("", 30, "bold")), sg.Button('R20', font=("", 30, "bold"))],
                                [sg.Button('R21', font=("", 30, "bold")), sg.Button('R22', font=("", 30, "bold")), sg.Button('R23', font=("", 30, "bold")), sg.Button('R24', font=("", 30, "bold")), sg.Button('R25', font=("", 30, "bold")),
                                sg.Button('R26', font=("", 30, "bold")), sg.Button('R27', font=("", 30, "bold")), sg.Button('R28', font=("", 30, "bold")), sg.Button('R29', font=("", 30, "bold")), sg.Button('R30', font=("", 30, "bold"))],
                                [sg.Button('R31', font=("", 30, "bold")), sg.Button('R32', font=("", 30, "bold")), sg.Button('R33', font=("", 30, "bold")), sg.Button('R34', font=("", 30, "bold")), sg.Button('R35', font=("", 30, "bold")),
                                sg.Button('R36', font=("", 30, "bold")), sg.Button('R37', font=("", 30, "bold")), sg.Button('R38', font=("", 30, "bold")), sg.Button('R39', font=("", 30, "bold")), sg.Button('R40', font=("", 30, "bold"))],
                                [sg.Button('R41', font=("", 30, "bold")), sg.Button('R42', font=("", 30, "bold")), sg.Button('R43', font=("", 30, "bold")), sg.Button('R44', font=("", 30, "bold")), sg.Button('R45', font=("", 30, "bold")),
                                sg.Button('R46', font=("", 30, "bold")), sg.Button('R47', font=("", 30, "bold")), sg.Button('R48', font=("", 30, "bold")), sg.Button('R49', font=("", 30, "bold")), sg.Button('R50', font=("", 30, "bold"))],
                                [sg.Button('R51', font=("", 30, "bold"))],
                                [sg.Button('Status Report', font=("", 35, "bold"))], [sg.Button('Back', font=("", 35, "bold"))]]
                window = sg.Window('Time and Labour', layoutF).Finalize()
                window.Maximize()
                event, values = window.read()
                RowNumber = window[event].get_text()
                if event == 'Status Report':
                    window.close()
                    StatusRport(Field)
                if event == "Back":
                    window.close()
                    FieldLoop += 1
                if event != 0:
                    window.close()
                    ActionLog()
