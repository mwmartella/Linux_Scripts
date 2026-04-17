#This whole thing is nested in a function becuase it gets imported into a larger field manager program.
def RowJob():
    from sqlalchemy import create_engine
    import sqlite3
    import pandas as pd
    import FreeSimpleGUI as sg
    import datetime
    import sys
    import textwrap
    import platform
    import re
    import json
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
    SMALL_BTN_FONT = ("Sans", 12, "bold")
    SMALL_BTN_SIZE = (14, 2)

    def _make_window(layoutA, title='Row Job Manager'):
        layout = [[sg.VPush()],
                  [sg.Push(), sg.Column(layoutA, element_justification='c'), sg.Push()],
                  [sg.VPush()]]
        win = sg.Window(title, layout, finalize=True, resizable=True)
        win.Maximize()
        return win

    btn_kwargs = dict(font=BTN_FONT, size=BTN_SIZE, pad=BTN_PAD, border_width=2)
    back_kwargs = dict(font=BTN_FONT, size=(12, 1), pad=BTN_PAD, button_color=('white', 'firebrick3'), border_width=2)

    #Start Up Database engines....... Vroom
    with open('/home/super1/OneDrive/~FARM DATA/Timesheet App/ACTIVITYLOG.json', 'r') as json_file:
        data = json.load(json_file)

    def find_block(data, field, variety):
        for block, attributes in data.items():
            if attributes.get("Field") == field and attributes.get("Variety") == variety:
                return block
        return None
    
    BASE_PATH = '/home/super1/OneDrive/~FARM DATA/Timesheet App/'
    CompName = platform.node()
    DB1 = "sqlite:///" + BASE_PATH + "SUPER2 TimeSheetLocal.db"
    DB2 = BASE_PATH + "SUPER2 TimeSheetLocal.db"
    print(DB1)
    print(DB2)
    Day = datetime.datetime.now()
    Day = Day.strftime('%Y-%m-%d')
    print(Day)
    RE = re.compile(Day + " [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]")
    ####################################################################################################################################################################################################################################
    #Here Is All The Lists, Ditcionaries and Links to DataBases that the program needs.
    ####################################################################################################################################################################################################################################
    FieldList = list({block["Field"] for block in data['BlockDict'].values() if "Field" in block})
    VarietyList = list({block["Variety"] for block in data['BlockDict'].values() if "Variety" in block})
    BlockDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/BlockData/BLOCKDATA.xlsx')
    SuperDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/SUPERVISORS.xlsx')
    CasualDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/CASUAL STAFF.xlsx')
    print(CasualDataFrame)
    MachinesDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/WORKER DATA/MACHINES.xlsx')
    VarietyDataFrame = pd.read_excel('/home/super1/OneDrive/~FARM DATA/Timesheet App/BlockData/VARIETY.xlsx')
    VarietyList = VarietyDataFrame['VARIETY'].tolist()
    QACHECKLIST = ['All Good', 'Missed Work - Sent Back', 'Work Too Heavy', 'Work Too Light', 'Worker Issues - Distracted', 
                   'Worker Issues - Attitude', 'Worker Issues - Other']
    JobTypeList = ['Picking', 'Pruning', 'Thinning', 'Establish Planting', 'Tree Training', 'Packing', 'Irrigation Maintinance', 
                   "Cherry Packing 1kg", "Cherry Packing 2kg", "Cherry Packing 5kg", "Cherry Packing 10kg"]
    engine = create_engine(DB1) 
    sql_connect = sqlite3.connect(DB2)
    cursor = sql_connect.cursor()
    engine2 = create_engine("sqlite:///" + BASE_PATH + "RowJobQa.db") 
    sql_connect2 = sqlite3.connect(BASE_PATH + 'RowJobQa.db')
    cursor2 = sql_connect2.cursor()
    ####################################################################################################################################################################################################################################
    #Open A Window To Select Field
    ####################################################################################################################################################################################################################################
    layoutB = [ [sg.Text('Row Job Manager', font=TITLE_FONT)],
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
    if event == 'Back':
        window.close()
    if event == 'Next':
        Field = values['Field']
        JobType = values['Job']
        Variety = values['Variety']
        window.close()
    ####################################################################################################################################################################################################################################
    #Pull The Current Status of The Field Selected
    ####################################################################################################################################################################################################################################
    Signalq = 0
    Block = find_block(data['BlockDict'], Field, Variety)
    print(Block)
    while Signalq == 0:
        RowLogDataFrame = pd.DataFrame(columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
        CurrentRowLog = cursor.execute("""SELECT * FROM WorkerRowLog WHERE Field = '%s';""" % Field)
        CurrentRowLogFrame = pd.DataFrame(CurrentRowLog, columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
        print(CurrentRowLogFrame)
        CurrentRowLogFrame = CurrentRowLogFrame[CurrentRowLogFrame.TimeStamp.str.contains(RE, regex=True, na=False)]
        CurrentRowLogFrame = CurrentRowLogFrame.groupby(['Worker', 'Field', 'Variety', 'Job_Type'])['Signal'].sum().reset_index()
        print(CurrentRowLogFrame)
        CurrentRowLogFilter = CurrentRowLogFrame.loc[CurrentRowLogFrame['Signal'] == 1]
        VarietyFinder = BlockDataFrame.loc[BlockDataFrame['Field'] == Field]
        VarietyList = VarietyFinder['Variety'].tolist()
        VarietyList = list(dict.fromkeys(VarietyList))
        RowList = VarietyFinder['Row'].tolist()
        RowList = list(dict.fromkeys(RowList))
        headers = {'Worker':[], 'Field':[], 'Variety':[], 'Job_Type':[], 'Signal':[]}
        headings = list(headers)
        values = CurrentRowLogFilter.values.tolist()
        layoutB = [ [sg.Text('Row Job Manager for %s' % Field, font=TITLE_FONT)],
                    [sg.Table(values=values, headings=headings, font=TABLE_FONT, auto_size_columns=True)],
                    [sg.Text('Sign In: select worker & press Sign In', font=BODY_FONT)],
                    [sg.Text('Sign Out: select worker & press Sign Out', font=BODY_FONT)],
                    [sg.Text('Bulk Sign Out: press Sign Out All', font=BODY_FONT)],
                    [sg.Text('Select Worker', font=BODY_FONT)],
                    make_touch_combo_row('Select Worker', 'Worker'),
                    [sg.pin(sg.Button('Sign In', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD, border_width=2)),
                     sg.pin(sg.Button('Sign Out', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD, border_width=2)),
                     sg.pin(sg.Button('Sign Out All', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD, border_width=2)),
                     sg.pin(sg.Button('Back', **back_kwargs)),
                     sg.pin(sg.Button('QA LOG', font=SMALL_BTN_FONT, size=SMALL_BTN_SIZE, pad=BTN_PAD, border_width=2))]]
        _combos_worker = {
            'Worker': ('Select Worker', CasualDataFrame["Worker Name"].tolist()),
        }
        window = _make_window(layoutB)
        while True:
            event, values = window.read()
            if handle_touch_combos(event, window, _combos_worker):
                continue
            break
    ####################################################################################################################################################################################################################################
    #Event Groups For Close Window
    ####################################################################################################################################################################################################################################    
        if event == 'Back':
            Signalq = 1
            window.close()
    ####################################################################################################################################################################################################################################
    #Event Groups For Sign In
    ####################################################################################################################################################################################################################################
        if event == 'Sign In':
            Worker = values['Worker']
            if Worker == "Worker":
                window.close()
                layoutB = [ [sg.Text('WORKER INVALID', font=WARN_FONT)],
                            [sg.Button('BACK', **btn_kwargs)]]
                window = _make_window(layoutB, 'ERROR')
                event, values = window.read()
                if event == "BACK":
                    window.close()
                    continue
            Action = 'Start'
            TimeStamp = datetime.datetime.now()
            Signal = 1
            WorkerCheckLog = cursor.execute("""SELECT * FROM WorkerRowLog WHERE Field = '%s' AND Worker = '%s';""" % (Block, Worker))
            WorkerCheckLog = pd.DataFrame(WorkerCheckLog, columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
            WorkerCheckLog = WorkerCheckLog[WorkerCheckLog.TimeStamp.str.contains(RE, regex=True, na=False)]
            WorkerCheckLog['Signal'] = WorkerCheckLog['Signal'].astype(float)
            WorkerCheckSignal = WorkerCheckLog['Signal'].sum()
            if WorkerCheckSignal == 1:
                window.close()
                layoutB = [ [sg.Text('WORKER ALREADY LOGGED IN', font=WARN_FONT)],
                            [sg.Button('BACK', **btn_kwargs)]]
                window = _make_window(layoutB, 'ERROR')
                event, values = window.read()
                if event == "BACK":
                    window.close()
                    continue
            DataList = [Field, data['BlockDict'][Block]["Row"], Worker, Action, TimeStamp, Signal, Variety, JobType]
            RowLogDataFrame.loc[len(RowLogDataFrame)] = DataList
            RowLogDataFrame.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
            RowLogDataFrame = pd.DataFrame(columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
            window.close()
    ####################################################################################################################################################################################################################################
    #Event Groups For Sign Out
    ####################################################################################################################################################################################################################################
        if event == 'Sign Out':
            Worker = values['Worker']
            Action = 'Finish'
            if Worker == "Worker":
                window.close()
                layoutB = [ [sg.Text('WORKER INVALID', font=WARN_FONT)],
                            [sg.Button('BACK', **btn_kwargs)]]
                window = _make_window(layoutB, 'ERROR')
                event, values = window.read()
                if event == "BACK":
                    window.close()
                    continue
            TimeStamp = datetime.datetime.now()
            Signal = -1
            WorkerCheckLog = cursor.execute("""SELECT * FROM WorkerRowLog WHERE Field = '%s' AND Worker = '%s';""" % (Field, Worker))
            WorkerCheckLog = pd.DataFrame(WorkerCheckLog, columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
            print(WorkerCheckLog)
            WorkerCheckLog = WorkerCheckLog[WorkerCheckLog.TimeStamp.str.contains(RE, regex=True, na=False)]
            WorkerCheckLog = WorkerCheckLog.drop(columns=['TimeStamp'])
            WorkerCheckLog['Signal'] = WorkerCheckLog['Signal'].astype(float)
            WorkerCheckSignal = WorkerCheckLog['Signal'].sum()
            if WorkerCheckSignal == 0:
                window.close()
                layoutB = [ [sg.Text('WORKER NOT LOGGED INTO ROW', font=WARN_FONT)],
                            [sg.Button('BACK', **btn_kwargs)]]
                window = _make_window(layoutB, 'ERROR')
                event, values = window.read()
                if event == "BACK":
                    window.close()
                    continue
            DataList = [Field, data['BlockDict'][Block]["Row"], Worker, Action, TimeStamp, Signal, Variety, JobType]
            RowLogDataFrame.loc[len(RowLogDataFrame)] = DataList
            RowLogDataFrame.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
            RowLogDataFrame = pd.DataFrame(columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
            window.close()
    ####################################################################################################################################################################################################################################
    #Event Groups For Swap
    ####################################################################################################################################################################################################################################
    ####################################################################################################################################################################################################################################
    #Event Groups For QA
    ####################################################################################################################################################################################################################################
    ####################################################################################################################################################################################################################################
    #Event Groups For End All
    ####################################################################################################################################################################################################################################
        if event == 'Sign Out All':
            for index, row in CurrentRowLogFilter.iterrows():
                Worker = row['Worker']
                Action = 'Finish'
                TimeStamp = datetime.datetime.now()
                Signal = -1
                DataList = [Field, data['BlockDict'][Block]["Row"], Worker, Action, TimeStamp, Signal, Variety, JobType]
                RowLogDataFrame.loc[len(RowLogDataFrame)] = DataList
                RowLogDataFrame.to_sql('WorkerRowLog', con=engine, if_exists='append', index=False)
                RowLogDataFrame = pd.DataFrame(columns=['Field', 'Row', 'Worker', 'Action', 'TimeStamp', 'Signal', 'Variety', 'Job_Type'])
                window.close()