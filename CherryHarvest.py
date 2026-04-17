from sqlalchemy import create_engine
import sqlite3
import pandas as pd
import FreeSimpleGUI as sg
import datetime
import sys
import textwrap
import RowJob
import re
import platform
from touch_helpers import make_touch_combo_row, handle_touch_combos

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
INPUT_FONT = ("Sans", 14, "bold")

def _make_window(layoutA, title='Cherry Harvest Manager'):
    layout = [[sg.VPush()],
              [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
              [sg.VPush()]]
    win = sg.Window(title, layout, finalize=True, resizable=True)
    win.Maximize()
    return win

btn_kwargs = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
back_kwargs = dict(font=BTN_FONT, size=(12, 1), pad=BTN_PAD, button_color=('white', 'firebrick3'), border_width=2)

def CherryHarvest():
    BASE_PATH = '/home/super1/OneDrive/~FARM DATA/Timesheet App/'
    CompName = platform.node()
    print(CompName)
    DB1 = "sqlite:///" + BASE_PATH + "SUPER2 CherryLog.db"
    DB2 = BASE_PATH + "SUPER2 CherryLog.db"
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
            layoutB = [ [sg.Text('Cherry Crate Logger', font=TITLE_FONT)],
                    [sg.pin(sg.Table(values=values, headings=headings, col_widths=[30,30], font=TABLE_FONT)),
                     sg.pin(sg.Table(values=values2, headings=headings2, col_widths=[30,30], font=TABLE_FONT))],
                    [sg.Text('Select Worker', font=BODY_FONT)],
                    make_touch_combo_row('Select Worker', 'W'),
                    [sg.Text('Type Crate ID', font=HEADER_FONT)],
                    [sg.InputText(key='CrateNum', font=INPUT_FONT)],
                    [sg.Text('Select QA', font=HEADER_FONT)],
                    make_touch_combo_row('Select QA', 'QA'),
                    [sg.Button('LOG', **btn_kwargs)],
                    [sg.Button('Quit', **back_kwargs)]]
            _combos_crate = {
                'W': ('Select Worker', TotalWorkerList),
                'QA': ('Select QA', QACHECKLIST),
            }
            window = _make_window(layoutB, 'Crate Logger')
            while True:
                event, values = window.read()
                if handle_touch_combos(event, window, _combos_crate):
                    continue
                break
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
                    layoutB = [ [sg.Text('INVALID CRATE NUMBER', font=WARN_FONT)],
                               [sg.Button('BACK', **btn_kwargs)]]
                    window = _make_window(layoutB, 'Crate Logger')
                    event, values = window.read()
                    if event == 'BACK':
                        window.close()
                    continue
                if Crate < 0 or Crate > 480:
                    layoutB = [ [sg.Text('INVALID CRATE NUMBER', font=WARN_FONT)],
                               [sg.Button('BACK', **btn_kwargs)]]
                    window = _make_window(layoutB, 'Crate Logger')
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
                    layoutB = [ [sg.Text('CRATE ALREADY LOGGED', font=WARN_FONT)],
                               [sg.Button('BACK', **btn_kwargs)]]
                    window = _make_window(layoutB, 'Crate Logger')
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

    layoutB = [ [sg.Text('Cherry Harvest Manager', font=TITLE_FONT)],
                [sg.Button('Crate Log', **btn_kwargs)],
                [sg.Button('Assign Row', **btn_kwargs)],
                [sg.VPush()],
                [sg.Button('Cancel', **back_kwargs)]]
    window = _make_window(layoutB)
    event, values = window.read()
    if event == 'Assign Row':
        window.close()
        RowJob.RowJob()
    elif event == 'Crate Log':
        window.close()
        CrateLog()
