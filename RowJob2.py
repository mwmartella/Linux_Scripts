#This whole thing is nested in a function becuase it gets imported into a larger field manager program.
def RowJob():
    from sqlalchemy import create_engine
    import sqlite3
    import pandas as pd
    import PySimpleGUI as sg
    import datetime
    import sys
    import textwrap
    import platform
    import re
    import json
    #Start Up Database engines....... Vroom
    with open('ACTIVITYLOG.json', 'r') as json_file:
        data = json.load(json_file)

    def find_block(data, field, variety):
        for block, attributes in data.items():
            if attributes.get("Field") == field and attributes.get("Variety") == variety:
                return block
        return None
    
    CompName = platform.node() #This is so either of 2 Tablets can access the database but the SQL files are saved seperately
    DB1 = "sqlite:///" + CompName + " TimeSheetLocal.db"
    DB2 = CompName + " TimeSheetLocal.db"
    print(DB1) #My biggest flaw as a programmer is my over use of print statements........
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
    BlockDataFrame = pd.read_excel('BlockData\\BLOCKDATA.xlsx')
    SuperDataFrame = pd.read_excel('Worker Data\\SUPERVISORS.xlsx')
    CasualDataFrame = pd.read_excel('Worker Data\\CASUAL STAFF.xlsx')
    print(CasualDataFrame)
    MachinesDataFrame = pd.read_excel('Worker Data\\MACHINES.xlsx')
    VarietyDataFrame = pd.read_excel('BlockData\\VARIETY.xlsx')
    VarietyList = VarietyDataFrame['VARIETY'].tolist()
    QACHECKLIST = ['All Good', 'Missed Work - Sent Back', 'Work Too Heavy', 'Work Too Light', 'Worker Issues - Distracted', 
                   'Worker Issues - Attitude', 'Worker Issues - Other']
    JobTypeList = ['Picking', 'Pruning', 'Thinning', 'Establish Planting', 'Tree Training', 'Packing', 'Irrigation Maintinance', 
                   "Cherry Packing 1kg", "Cherry Packing 2kg", "Cherry Packing 5kg", "Cherry Packing 10kg"]
    engine = create_engine(DB1) 
    sql_connect = sqlite3.connect(DB2)
    cursor = sql_connect.cursor()
    engine2 = create_engine("sqlite:///RowJobQa.db") 
    sql_connect2 = sqlite3.connect('RowJobQa.db')
    cursor2 = sql_connect2.cursor()
    ####################################################################################################################################################################################################################################
    #Open A Window To Select Field
    ####################################################################################################################################################################################################################################
    layoutB = [ [sg.Text('Row Job Manager', font=("", 25, "bold"))],
                [sg.Text('Select Field', font=("", 30, "bold"))],
                [sg.Combo(FieldList, default_value = 'Field', size = 50, key = 'Field', font=("", 30, "bold"))],
                [sg.Text('Select Variety', font=("", 30, "bold"))],
                [sg.Combo(VarietyList, default_value = 'Variety', size = 50, key = 'Variety', font=("", 30, "bold"))],
                [sg.Text('Select Job Type', font=("", 20, "bold"))],
                [sg.Combo(JobTypeList, default_value = 'Job', size = 50, key = 'Job', font=("", 30, "bold"))],
                [sg.Button('Next', font=("", 30, "bold"))], [sg.Button('Back', font=("", 30, "bold"))]]
    window = sg.Window('Row Job Manager', layoutB).Finalize()
    window.Maximize()
    event, values = window.read()
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
        layoutB = [ [sg.Text('Row Job Manager for %s' % Field, font=("", 25, "bold"))],
                    [sg.Table(values = values, headings = headings, font=("", 15, "bold"), auto_size_columns=True)],
                    [sg.Text('To Sign Worker In Select Worker and Press Sign In', font=("", 10, "bold"))],
                    [sg.Text('To Sign Worker Out Worker and Press Sign Out', font=("", 10, "bold"))],
                    [sg.Text('For End of Block Or End Of Day Bulk Sign Out Press Sign Out All', font=("", 10, "bold"))],
                    [sg.Text('Select Worker', font=("", 10, "bold"))],
                    [sg.Combo(CasualDataFrame["Worker Name"].tolist(), default_value = 'Worker', size = 50, key = 'Worker', font=("", 20, "bold"))],
                    [sg.pin(sg.Button('Sign In', font=("", 20, "bold"))), sg.pin(sg.Button('Sign Out', font=("", 20, "bold"))), sg.pin(sg.Button('Sign Out All', font=("", 20, "bold"))), sg.pin(sg.Button('Back', font=("", 20, "bold"))), sg.pin(sg.Button('QA LOG', font=("", 20, "bold")))]]
        window = sg.Window('Row Job Manager', layoutB).Finalize()
        window.Maximize()
        event, values = window.read()
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
                layoutB = [ [sg.Text('WORKER INVALID', font=("", 50, "bold"))],
                            [sg.Button('BACK', font=("", 50, "bold"))]]
                window = sg.Window('ERROR', layoutB).Finalize()
                window.Maximize()
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
                layoutB = [ [sg.Text('WORKER ALREADY LOGGED IN', font=("", 50, "bold"))],
                            [sg.Button('BACK', font=("", 50, "bold"))]]
                window = sg.Window('ERROR', layoutB).Finalize()
                window.Maximize()
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
                layoutB = [ [sg.Text('WORKER INVALID', font=("", 50, "bold"))],
                            [sg.Button('BACK', font=("", 50, "bold"))]]
                window = sg.Window('ERROR', layoutB).Finalize()
                window.Maximize()
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
                layoutB = [ [sg.Text('WORKER NOT LOGGED INTO ROW', font=("", 50, "bold"))],
                            [sg.Button('BACK', font=("", 50, "bold"))]]
                window = sg.Window('ERROR', layoutB).Finalize()
                window.Maximize()
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
    #Event Groups For Swap - This was in an older version to be able to swap blocks with a single click, could be worth revisiting
    ####################################################################################################################################################################################################################################
    ####################################################################################################################################################################################################################################
    #Event Groups For QA - There was also a QA function for logging worker quality checks
    ####################################################################################################################################################################################################################################
    ####################################################################################################################################################################################################################################
    #Event Groups For End All - This is so at the end of the day you can sign everyone out at once.
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