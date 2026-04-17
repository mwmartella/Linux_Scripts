from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import PySimpleGUI as sg
import datetime
import sys
import textwrap
import RowJob
import re
import platform

def CherryHarvest():
    CompName = platform.node()
    print(CompName)
    DB1 = "sqlite:///" + CompName + " CherryLog.db"
    DB2 = CompName + " CherryLog.db"
    FieldList = ['WISHARTS - PL', 'WISHARTS - BRAVO' 'CHERRYS', 'CHERRY BRAVO', 'S-SHED', 'STK', 'P-BELLE', 'LIR', 'ROB BRAVO', 'MODI', 'DWF', 'GSPL', 'TOTAL']
    BlockDataFrame = pd.read_excel('BlockData\\BLOCKDATA.xlsx')
    SuperDataFrame = pd.read_excel('Worker Data\\SUPERVISORS.xlsx')
    CasualDataFrame = pd.read_excel('Worker Data\\CASUAL STAFF.xlsx')
    MachinesDataFrame = pd.read_excel('Worker Data\\MACHINES.xlsx')
    VarietyDataFrame = pd.read_excel('BlockData\\VARIETY.xlsx')
    VarietyList = VarietyDataFrame['VARIETY'].tolist()
    Date = datetime.datetime.today()
    Date = Date.strftime('%Y-%m-%d')
    print(Date)
    REDate = re.compile(Date + " [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]")
    QACHECKLIST = ['All Good', 'Not Full', 'No Stems', 'Colour', 'Bruising', 'Exsessive Damage', 'Derbis', 'Worker - Missed Fruit', 'Worker - Distracted', 'Worker - Attitude']

    engine = create_engine(DB1) 
    sql_connect = sqlite3.connect(DB2)
    cursor = sql_connect.cursor()

    superlist = SuperDataFrame['Worker Name'].tolist()
    casuallist = CasualDataFrame['Worker Name'].tolist()
    TotalWorkerList = superlist + casuallist

    def CrateLog():
        Signal = 0
        while Signal < 1:
            CurrentCrateLog = cursor.execute("""SELECT Time, Worker, Crate, QA FROM Crates""")
            CurrentCrateLogFrame = pd.DataFrame(CurrentCrateLog, columns=['Time', 'Worker', 'SUM(Crate)', 'QA'])
            CurrentCrateLog = cursor.execute("""SELECT Time, Worker, Crate, QA FROM Crates""")
            QALOGFRAME = pd.DataFrame(CurrentCrateLog, columns=['Time', 'Worker', 'Crate', 'QA'])
            print(CurrentCrateLogFrame)
            CurrentCrateLogFrame = CurrentCrateLogFrame[CurrentCrateLogFrame['Time'].str.contains(Date)]
            CurrentCrateLogFrame = CurrentCrateLogFrame.groupby(["Worker"], as_index=False)["SUM(Crate)"].count()
            print(QALOGFRAME)
            QALOGFRAME = QALOGFRAME[QALOGFRAME['Time'].str.contains(Date)]
            print(QALOGFRAME)
            QALOGFRAME = QALOGFRAME.loc[QALOGFRAME['QA'] != "All Good"]
            QALOGFRAME = QALOGFRAME.drop(['Crate', 'Time'], axis=1)
            print(CurrentCrateLogFrame)
            print(QALOGFRAME)
            headers = {'Worker':[], 'SUM(Crate)':[], 'QA':[]}
            headings = list(headers)
            values = CurrentCrateLogFrame.values.tolist()
            headers2 = {'Worker':[], 'QA':[]}
            headings2 = list(headers2)
            values2 = QALOGFRAME.values.tolist()
            layoutB = [  [sg.Text('Cherry Crate Logger', font=("", 25, "bold"))],
                    [sg.pin(sg.Table(values = values, headings = headings, col_widths=[60,60], font=("", 15, "bold"))), sg.pin(sg.Table(values = values2, headings = headings2, col_widths=[60,60], font=("", 15, "bold")))],
                    [sg.Text('Select Worker', font=("", 15, "bold"))],
                    [sg.Combo(TotalWorkerList, default_value = 'Worker', size = 50, key = 'W', font=("", 15, "bold"))],
                    [sg.Text('Type Crate ID', font=("", 20, "bold"))],
                    [sg.InputText(key='CrateNum', font=("", 20, "bold"))],
                    [sg.Text('Select QA', font=("", 20, "bold"))],
                    [sg.Combo(QACHECKLIST, default_value = 'QA', size = 50, key = 'QA', font=("", 20, "bold"))],
                    [sg.Button('LOG', font=("", 25, "bold"))], [sg.Button('Quit', font=("", 25, "bold"))]]
            window = sg.Window('Crate Logger', layoutB).Finalize()
            window.Maximize()
            event, values = window.read()
            if event == 'Quit':
                window.close()
                Signal = 1
            if event == 'LOG':
                window.close()
                Worker = values['W']
                #####################
                Crate = values['CrateNum']
                try:
                    Crate = int(Crate)
                except ValueError:
                    layoutB = [  [sg.Text('INVALID CRATE NUMBER', font=("", 50, "bold"))],
                               [sg.Button('BACK', font=("", 50, "bold"))]]
                    window = sg.Window('Crate Logger', layoutB).Finalize()
                    window.Maximize()
                    event, values = window.read()
                    if event == 'BACK':
                        window.close()
                    continue
                if Crate < 0 or Crate > 480:
                    layoutB = [  [sg.Text('INVALID CRATE NUMBER', font=("", 50, "bold"))],
                               [sg.Button('BACK', font=("", 50, "bold"))]]
                    window = sg.Window('Crate Logger', layoutB).Finalize()
                    window.Maximize()
                    event, values = window.read()
                    if event == 'BACK':
                        window.close()
                    continue
                try:
                    Crate_Input_Double_Test = cursor.execute("""SELECT * FROM Crates WHERE Crate = '%s' """ % Crate)
                    Crate_Input_Double_Test = pd.DataFrame(Crate_Input_Double_Test, columns=['Time', 'Worker', 'SUM(Crate)', 'QA'])
                    Crate_Input_Double_Test = Crate_Input_Double_Test.loc[Crate_Input_Double_Test.Time.str.contains(Date), :]
                    print(Crate_Input_Double_Test)
                    Crate_Input_Double_Test = Crate_Input_Double_Test['Time'].tolist()
                    Crate_Input_Double_Test = Crate_Input_Double_Test[0]
                    layoutB = [  [sg.Text('CRATE ALREADY LOGGED', font=("", 50, "bold"))],
                               [sg.Button('BACK', font=("", 50, "bold"))]]
                    window = sg.Window('Crate Logger', layoutB).Finalize()
                    window.Maximize()
                    event, values = window.read()
                    if event == 'BACK':
                        window.close()
                    continue
                except IndexError:
                    pass
                #open window to say Crate Already Logged
                QA = values['QA']
                #################
                Time = datetime.datetime.now()
                DataList = [Time, Worker, Crate, QA]
                CrateLogDF = pd.DataFrame(columns=['Time', 'Worker', 'Crate', 'QA'])
                CrateLogDF.loc[len(CrateLogDF)] = DataList
                CrateLogDF.to_sql('Crates', con=engine, if_exists='append', index=False)
    layoutB = [  [sg.Text('Cherry Harvest Manager', font=("", 25, "bold"))],
                [sg.Button('Crate Log', font=("", 50, "bold"))], [sg.Button('Assign Row', font=("", 50, "bold"))],
                [sg.Button('Cancel', font=("", 50, "bold"))]]
    window = sg.Window('Cherry Harvest Manager', layoutB).Finalize()
    window.Maximize()
    event, values = window.read()
    if event == 'Assign Row':
        window.close()
        RowJob.RowJob()
    elif event == 'Crate Log':
        window.close()
        CrateLog()


