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
from random import randrange
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import numpy as np
import argparse
import imutils
import cv2
import numpy as np
from matplotlib import pyplot as plt
import os
import shutil
import AppleQA
global SizeList
CompName = platform.node()
print(CompName)
DB1 = "sqlite:///%sAppleLog.db" % CompName
DB2 = "%sAppleLog.db" % CompName
engine = create_engine(DB1) 
sql_connect = sqlite3.connect(DB2)
cursor = sql_connect.cursor()
FieldList = ['WISHARTS - PL', 'WISHARTS - BRAVO', 'CHERRYS', 'CHERRY BRAVO', 'S-SHED', 'STK', 'P-BELLE', 'LIR', 'ROB BRAVO', 'MODI', 'DWF', 'GSPL', 'TOTAL']
CrewList = ['SR1', 'SR2', 'SR3', 'SR4', 'SR5', 'SR6', 'Mark']
BlockDataFrame = pd.read_excel('BlockData\\BLOCKDATA.xlsx')
SuperDataFrame = pd.read_excel('Worker Data\\SUPERVISORS.xlsx')
CasualDataFrame = pd.read_excel('Worker Data\\CASUAL STAFF.xlsx')
MachinesDataFrame = pd.read_excel('Worker Data\\MACHINES.xlsx')
VarietyDataFrame = pd.read_excel('BlockData\\VARIETY.xlsx')
FixedTimes = pd.read_excel('Worker Data\\FIXEDTIMES.xlsx')
WorkerList = CasualDataFrame['Worker Name'].tolist()
VarietyList = VarietyDataFrame['VARIETY'].tolist()
Date2 = datetime.datetime.today()
Date = Date2.strftime('%Y-%m-%d')
DefectCountList = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
DefectList = ['Bruise-Old', 'Bruise-New', 'Sunburn']
DefectList2 = ['Colour', 'Misc Damage', 'Hail']
print(Date)
VariableTimes = pd.read_excel('Worker Data\\HarvestQAVariables.xlsx')
DefectUpperLimit = VariableTimes.loc[VariableTimes['Class'] == 'Defect Upper Limit']
DefectUpperLimit = float(DefectUpperLimit['Variable'].tolist()[0])
DefectLowerLimit = VariableTimes.loc[VariableTimes['Class'] == 'Defect Lower Limit']
DefectLowerLimit = float(DefectLowerLimit['Variable'].tolist()[0])
SizeUpperLimit = VariableTimes.loc[VariableTimes['Class'] == 'Size Upper Limit']
SizeUpperLimit = float(SizeUpperLimit['Variable'].tolist()[0])
SizeLowerLimit = VariableTimes.loc[VariableTimes['Class'] == 'Size Lower Limit']
SizeLowerLimit = float(SizeLowerLimit['Variable'].tolist()[0])
CameraURL = VariableTimes.loc[VariableTimes['Class'] == CompName]
CameraURL = CameraURL['Variable'].tolist()[0]
print(CameraURL)


def AppleSize():
    global SizeList
    print('InLoop')
    CompName = platform.node()
    print(CompName)
    DB1 = "sqlite:///%sAppleLog.db" % CompName
    DB2 = "%sAppleLog.db" % CompName
    engine = create_engine(DB1) 
    sql_connect = sqlite3.connect(DB2)
    cursor = sql_connect.cursor()
    FieldList = ['WISHARTS - PL', 'WISHARTS - BRAVO', 'CHERRYS', 'CHERRY BRAVO', 'S-SHED', 'STK', 'P-BELLE', 'LIR', 'ROB BRAVO', 'MODI', 'DWF', 'GSPL', 'TOTAL']
    BlockDataFrame = pd.read_excel('BlockData\\BLOCKDATA.xlsx')
    SuperDataFrame = pd.read_excel('Worker Data\\SUPERVISORS.xlsx')
    CasualDataFrame = pd.read_excel('Worker Data\\CASUAL STAFF.xlsx')
    MachinesDataFrame = pd.read_excel('Worker Data\\MACHINES.xlsx')
    VarietyDataFrame = pd.read_excel('BlockData\\VARIETY.xlsx')
    FixedTimes = pd.read_excel('Worker Data\\FIXEDTIMES.xlsx')
    WorkerList = CasualDataFrame['Worker Name'].tolist()
    VarietyList = VarietyDataFrame['VARIETY'].tolist()
    Date2 = datetime.datetime.today()
    Date = Date2.strftime('%Y-%m-%d')
    print(Date)
    REDate = re.compile(Date + " [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]")
    maxval = 255
    thresh = 128
    totalsizelists = []
    PhotoDir = CameraURL
    DirList = os.listdir(PhotoDir)
    print(DirList)
    DirList.remove('desktop.ini')
    PhotoDir = DirList[-1]
    PhotoDir = CameraURL + PhotoDir
    print(PhotoDir)
    def convert_binary(image_matrix, thresh_val):
        white = 255
        black = 0

        initial_conv = np.where((image_matrix <= thresh_val), image_matrix, white)
        final_conv = np.where((initial_conv > thresh_val), initial_conv, black)

        return final_conv


    def midpoint(ptA, ptB):
        return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)
        # construct the argument parse and parse the arguments
    ap = argparse.ArgumentParser()
    args = vars(ap.parse_args())
    # load the image, convert it to grayscale, and blur it slightly
    image = cv2.imread(PhotoDir)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    (thresh, im_bw) = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    smooth = cv2.GaussianBlur(im_bw, (205, 205), 0)
    #divison = cv2.divide(im_bw, smooth, scale=100)
    #ReSize = cv2.resize(divison, (1920, 1080))
    #cv2.imshow("Image", ReSize)
    #cv2.waitKey(0)
    (thresh, im_bw) = cv2.threshold(smooth, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    # perform edge detection, then perform a dilation + erosion to
    # close gaps in between object edges
    edged = cv2.Canny(im_bw, 0, 100)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)
    # find contours in the edge map
    cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    # sort the contours from left-to-right and initialize the
    # 'pixels per metric' calibration variable
    (cnts, _) = contours.sort_contours(cnts)
    pixelsPerMetric = None

    # loop over the contours individually
    SizeList = []
    for c in cnts:
        # if the contour is not sufficiently large, ignore it
        if cv2.contourArea(c) < 10000:
            continue
        # compute the rotated bounding box of the contour
        orig = image.copy()
        box = cv2.minAreaRect(c)
        box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
        box = np.array(box, dtype="int")
        # order the points in the contour such that they appear
        # in top-left, top-right, bottom-right, and bottom-left
        # order, then draw the outline of the rotated bounding
        # box
        box = perspective.order_points(box)
        cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2)
        # loop over the original points and draw them
        for (x, y) in box:
            cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

        # unpack the ordered bounding box, then compute the midpoint
        # between the top-left and top-right coordinates, followed by
        # the midpoint between bottom-left and bottom-right coordinates
        (tl, tr, br, bl) = box
        (tltrX, tltrY) = midpoint(tl, tr)
        (blbrX, blbrY) = midpoint(bl, br)
        # compute the midpoint between the top-left and top-right points,
        # followed by the midpoint between the top-righ and bottom-right
        (tlblX, tlblY) = midpoint(tl, bl)
        (trbrX, trbrY) = midpoint(tr, br)
        # draw the midpoints on the image
        cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
        cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
        # draw lines between the midpoints
        cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
            (255, 0, 255), 2)
        cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
            (255, 0, 255), 2)
        # compute the Euclidean distance between the midpoints
        dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
        dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
        # if the pixels per metric has not been initialized, then
        # compute it as the ratio of pixels to supplied metric
        # (in this case, inches)
        if pixelsPerMetric is None:
            pixelsPerMetric = dB / 63
            # compute the size of the object
        dimA = dA / pixelsPerMetric
        dimB = dB / pixelsPerMetric
        # draw the object sizes on the image
        cv2.putText(orig, "{:.1f}in".format(dimA),
            (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (255, 255, 255), 2)
        cv2.putText(orig, "{:.1f}in".format(dimB),
            (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
            0.65, (255, 255, 255), 2)
        dimA = dimA * 1.15
        dimB = dimB * 1.15
        if dimA < 25 or dimA > 100:
            continue
        if dimB < 25 or dimB > 100:
            continue
        if dimA > dimB:
            SizeList.append(int(dimA))
        if dimB > dimA:
            SizeList.append(int(dimB))
        print(SizeList)

REDate = re.compile(Date + " [0-9][0-9]:[0-9][0-9]:[0-9][0-9].[0-9][0-9][0-9][0-9][0-9][0-9]")

CurrentBinLog = cursor.execute("""SELECT * FROM QA""")
CurrentBinLogFrame = pd.DataFrame(CurrentBinLog, columns=["Super_ID", "TimeStamp", "CheckID", "FruitChecked", "BruiseOld", "BruiseNew", "Sunburn", "Colour", "Hail", "Insect", "MiscDamage", "Size_1", "Size_2", "Size_3", "Size_4", 
                                                          "Size_5", "Size_6", "Size_7", "Size_8", "Size_9", "Size_10", "Size_11", "Size_12", "Size_13", "Size_14", "Size_15", "Size_16", "Size_17", "Size_18", "Size_19", "Size_20",
                                                          "Variety", "Block"])
CurrentBinLogFrame = CurrentBinLogFrame[CurrentBinLogFrame['TimeStamp'].str.contains(Date)]

layoutB = [ [sg.Text('Apple QA', font=("", 45, "bold"))],
            [sg.Text('Select Field', font=("", 30, "bold"))],
            [sg.Combo(FieldList, default_value = 'Field', size = 50, key = 'Field', font=("", 30, "bold"))],
            [sg.Text('Select Variety', font=("", 30, "bold"))],
            [sg.Combo(VarietyList, default_value = 'Job', size = 50, key = 'Job', font=("", 30, "bold"))],
            [sg.Button('Next', font=("", 30, "bold"))], [sg.Button('Back', font=("", 30, "bold"))]]
window = sg.Window('Row Job Manager', layoutB).Finalize()
window.Maximize()
event, values = window.read()
if event == "Back":
    window.close()
if event == "Next":
    window.close()
    Block = values['Field']
    Variety = values['Job']
CrewLoop = 0
while CrewLoop < 1:
    CrewButtonList = []
    for activeCrew in CrewList:
        CrewButton = sg.pin(sg.Button(activeCrew, font=("", 50, "bold")))
        CrewButtonList.append(CrewButton)
    layoutB = [ [sg.Text('SELECT CREW', font=("", 45, "bold"))],
                CrewButtonList,
                [sg.Button('Back', font=("", 30, "bold"))]]
    window = sg.Window('Row Job Manager', layoutB).Finalize()
    window.Maximize()
    event, values = window.read()
    if event == "Back":
        window.close()
        layoutB = [ [sg.Text('EXITING FOR END OF DAY?', font=("", 45, "bold"))],
                    [sg.Button('YES', font=("", 30, "bold"))], [sg.Button('NO', font=("", 30, "bold"))]]
        window = sg.Window('Row Job Manager', layoutB).Finalize()
        window.Maximize()
        event, values = window.read()
        if event == 'YES':
            window.close()
            PhotoDir = CameraURL
            DirList = os.listdir(PhotoDir)
            for file in DirList:
                file_path = os.path.join(PhotoDir, file)
                print(file_path)
                os.unlink(file_path)
            CrewLoop = 1
        else:
            window.close()
            CrewLoop = 1
    else:
        window.close()
        layoutB = [ [sg.Text('TAKE PHOTO NOW AND PRESS OK', font=("", 45, "bold"))],
                    [sg.Button('OK', font=("", 30, "bold"))]]
        window = sg.Window('Row Job Manager', layoutB).Finalize()
        window.Maximize()
        DummyVar = window.read()
        window.close()
        Crew = event
        DefectComboList = []
        for Defect in DefectList:
            DefectCombo = sg.pin(sg.Combo([Defect, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value = Defect, size = 20, key = Defect, font=("", 30, "bold")))
            DefectComboList.append(DefectCombo)
        DefectComboList2 = []
        for Defect in DefectList2:
            DefectCombo = sg.pin(sg.Combo([Defect, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value = Defect, size = 20, key = Defect, font=("", 30, "bold")))
            DefectComboList2.append(DefectCombo)
        QASTATSLOG = cursor.execute("""SELECT * FROM QA""")
        QASTATSLOGFRAME = pd.DataFrame(QASTATSLOG, columns=["Super_ID", "TimeStamp", "CheckID", "FruitChecked", "BruiseOld", "BruiseNew", "Sunburn", "Colour", "Hail", "Insect", "MiscDamage", "Size_1", "Size_2", "Size_3", "Size_4", 
                                                                "Size_5", "Size_6", "Size_7", "Size_8", "Size_9", "Size_10", "Size_11", "Size_12", "Size_13", "Size_14", "Size_15", "Size_16", "Size_17", "Size_18", "Size_19", "Size_20",
                                                                "Variety", "Block"])
        QASTATSLOGFRAME = QASTATSLOGFRAME[QASTATSLOGFRAME['TimeStamp'].str.contains(Date)]
        QASTATSLOGFRAME = QASTATSLOGFRAME[QASTATSLOGFRAME['CheckID'].str.contains(Crew)]
        print(QASTATSLOGFRAME)
        TotalFruitChecked = QASTATSLOGFRAME['FruitChecked'].sum()
        if len(QASTATSLOGFRAME) < 1:
            TotalFruitChecked = 1
        try:
            BNPCT = QASTATSLOGFRAME['BruiseNew'].sum() / TotalFruitChecked * 100
            print('BNCT FOUND')
        except ZeroDivisionError:
            BNPCT = 0
        if BNPCT <= DefectLowerLimit:
            BNPCTCOLOUR = 'lime green'
        if BNPCT > DefectLowerLimit and BNPCT <= DefectUpperLimit:
            BNPCTCOLOUR = 'yellow'
        if BNPCT > DefectUpperLimit:
            BNPCTCOLOUR = 'tomato2'
        print(BNPCT)
        try:
            BOPCT = QASTATSLOGFRAME['BruiseOld'].sum() / TotalFruitChecked * 100
        except ZeroDivisionError:
            BOPCT = 0
        if BOPCT <= DefectLowerLimit:
            BOPCTCOLOUR = 'lime green'
        if BOPCT > DefectLowerLimit and BOPCT <= DefectUpperLimit:
            BOPCTCOLOUR = 'yellow'
        if BOPCT > DefectUpperLimit:
            BOPCTCOLOUR = 'tomato2'
        try:
            SBPCT = QASTATSLOGFRAME['Sunburn'].sum() / TotalFruitChecked * 100
        except ZeroDivisionError:
            SBPCT = 0
        if SBPCT <= DefectLowerLimit:
            SBPCTCOLOUR = 'lime green'
        if SBPCT > DefectLowerLimit and SBPCT <= DefectUpperLimit:
            SBPCTCOLOUR = 'yellow'
        if SBPCT > DefectUpperLimit:
            SBPCTCOLOUR = 'tomato2'
        try:
            CLPCT = QASTATSLOGFRAME['Colour'].sum() / TotalFruitChecked * 100
        except ZeroDivisionError:
            CLPCT = 0
        if CLPCT <= DefectLowerLimit:
            CLPCTCOLOUR = 'lime green'
        if CLPCT > DefectLowerLimit and CLPCT <= DefectUpperLimit:
            CLPCTCOLOUR = 'yellow'
        if CLPCT > DefectUpperLimit:
            CLPCTCOLOUR = 'tomato2'
        try:
            HLPCT = QASTATSLOGFRAME['Hail'].sum() / TotalFruitChecked * 100
        except ZeroDivisionError:
            HLPCT = 0
        if HLPCT <= DefectLowerLimit:
            HLPCTCOLOUR = 'lime green'
        if HLPCT > DefectLowerLimit and HLPCT <= DefectUpperLimit:
            HLPCTCOLOUR = 'yellow'
        if HLPCT > DefectUpperLimit:
            HLPCTCOLOUR = 'tomato2'
        try:
            INPCT = QASTATSLOGFRAME['Insect'].sum() / TotalFruitChecked * 100
        except ZeroDivisionError:
            INPCT = 0
        if INPCT <= DefectLowerLimit:
            INPCTCOLOUR = 'lime green'
        if INPCT > DefectLowerLimit and INPCT <= DefectUpperLimit:
            INPCTCOLOUR = 'yellow'
        if INPCT > DefectUpperLimit:
            INPCTCOLOUR = 'tomato2'
        try:
            MDPCT = QASTATSLOGFRAME['MiscDamage'].sum() / TotalFruitChecked * 100
        except ZeroDivisionError:
            MDPCT = 0
        if MDPCT <= DefectLowerLimit:
            MDPCTCOLOUR = 'lime green'
        if MDPCT > DefectLowerLimit and MDPCT <= DefectUpperLimit:
            MDPCTCOLOUR = 'yellow'
        if MDPCT > DefectUpperLimit:
            MDPCTCOLOUR = 'tomato2'
        SizeListRange = ["Size_1", "Size_2", "Size_3", "Size_4", "Size_5", "Size_6", "Size_7", "Size_8", "Size_9", "Size_10", "Size_11", "Size_12", "Size_13", "Size_14", "Size_15", "Size_16", "Size_17", "Size_18", "Size_19", "Size_20"]
        AllSizesList = []
        for column in SizeListRange:
            print(QASTATSLOGFRAME)
            columnslist = QASTATSLOGFRAME[column].tolist()
            for idvsize in columnslist:
                AllSizesList.append(idvsize)
        print(AllSizesList)
        AllSizesList = [x for x in AllSizesList if x is not None]
        AllSizesList = [x for x in AllSizesList if not np.isnan(x)]
        print(AllSizesList)
        try:
            AVGSZ = sum(AllSizesList) / len(AllSizesList)
        except ZeroDivisionError:
            AVGSZ = 0
        if AVGSZ <= SizeLowerLimit:
            AVGSZCOLOUR = 'tomato2'
        if AVGSZ > SizeLowerLimit and AVGSZ <= SizeUpperLimit:
            AVGSZCOLOUR = 'lime green'
        if AVGSZ > SizeUpperLimit:
            AVGSZCOLOUR = 'tomato2'
        print(QASTATSLOGFRAME)
        layoutB = [ [sg.Text(Crew + ' Apple QA', font=("", 45, "bold"))],
                    [sg.Combo(['BinNumber', 1, 2, 3, 4 ,5, 6, 7, 8, 9, 10, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25], default_value = 'BinNumber', size = 20, key = 'BinLog', font=("", 30, "bold"))],
                    [sg.Combo(['Amount of Fruit Checked', 5, 10, 15, 20], default_value = 'Amount of Fruit Checked', size = 20, key = 'AMT', font=("", 30, "bold"))],
                    DefectComboList,
                    DefectComboList2,
                    [sg.Combo(['Insect', 1, 2, 3, 4, 5, 6, 7, 8, 9, 10], default_value = 'Insect', size = 15, key = 'Insect', font=("", 20, "bold"))],
                    [sg.pin(sg.Button('Log', font=("", 20, "bold"))), sg.pin(sg.Button('Back', font=("", 20, "bold")))],
                    [sg.Text('CREWS CURRENT STATS', font=("", 25, "bold"))],
                    [sg.pin(sg.Text('Bruise New = ' + str(int(BNPCT)) + '%', font=("", 25, "bold"), text_color=BNPCTCOLOUR)), sg.pin(sg.Text('Bruise Old = ' + str(int(BOPCT)) + '%', font=("", 25, "bold"), text_color=BOPCTCOLOUR))],
                    [sg.pin(sg.Text('Sunburn = ' + str(int(SBPCT)) + '%', font=("", 25, "bold"), text_color=SBPCTCOLOUR)), sg.pin(sg.Text('Colour = ' + str(int(CLPCT)) + '%', font=("", 25, "bold"), text_color=CLPCTCOLOUR))],
                    [sg.pin(sg.Text('Misc Damage = ' + str(int(MDPCT)) + '%', font=("", 25, "bold"), text_color=MDPCTCOLOUR)), sg.pin(sg.Text('Hail = ' + str(int(HLPCT)) + '%', font=("", 25, "bold"), text_color=HLPCTCOLOUR))],
                    [sg.pin(sg.Text('Insect = ' + str(int(INPCT)) + '%', font=("", 25, "bold"), text_color=INPCTCOLOUR)), sg.pin(sg.Text('AVG Size = ' + str(int(AVGSZ)) + 'mm', font=("", 25, "bold"), text_color=AVGSZCOLOUR))],
                    [sg.Text('GREEN  - ALL GOOD', font=("", 25, "bold"), text_color="lime green")],
                    [sg.Text('YELLOW - KEEP AN EYE ON IT', font=("", 25, "bold"), text_color="yellow")],
                    [sg.Text('RED - REPORT TO SUPER', font=("", 25, "bold"), text_color="tomato2")]]
        window = sg.Window('Row Job Manager', layoutB).Finalize()
        window.Maximize()
        event, values = window.read()
        if event == 'Log':
            window.close()
            QADATAFRAME = pd.DataFrame(columns=["Super_ID", "TimeStamp", "CheckID", "FruitChecked", "BruiseOld", "BruiseNew", "Sunburn", "Colour", "Hail", "Insect", "MiscDamage", "Size_1", "Size_2", "Size_3", "Size_4", 
                                                            "Size_5", "Size_6", "Size_7", "Size_8", "Size_9", "Size_10", "Size_11", "Size_12", "Size_13", "Size_14", "Size_15", "Size_16", "Size_17", "Size_18", "Size_19", "Size_20",
                                                            "Variety", "Block"])
            BinID = values['BinLog']
            DateCode = Date.replace('-', '')
            print(DateCode)
            BinCode = str(Crew) + str(DateCode) + str(BinID)
            AMT = values['AMT']
            try:
                BO = int(values['Bruise-Old'])
            except ValueError:
                BO = 0
            try:
                BN = int(values['Bruise-New'])
            except ValueError:
                BN = 0 
            try:
                SB = int(values['Sunburn'])
            except ValueError:
                SB = 0
            try:
                CL = int(values['Colour'])
            except ValueError:
                CL = 0
            try:
                MD = int(values['Misc Damage'])
            except ValueError:
                MD = 0
            try:
                HL = int(values['Hail'])
            except ValueError:
                HL = 0
            try:
                IC = int(values['Insect'])
            except ValueError:
                IC = 0
            try:
                AMT = int(AMT)
            except ValueError:
                AMT = 10
            SizeList = []
            AppleSize()
            if SizeList == []:
                SizeList = [None, None]
            SizeList.pop(0)
            print(SizeList)
            TimeStamp = datetime.datetime.now()
            DataList = [CompName, TimeStamp, BinCode, AMT, BO, BN, SB, CL, HL, IC, MD]
            for i in SizeList:
                DataList.append(i)
            ReaminingNoneAdder = 32 - len(DataList)
            RangeList = list(range(1, ReaminingNoneAdder))
            for i in RangeList:
                DataList.append(None)
            DataList.append(Variety)
            DataList.append(Block)
            print(DataList)
            QADATAFRAME.loc[len(QADATAFRAME)]=DataList
            QADATAFRAME.to_sql('QA', con=engine, if_exists='append', index=False)
            TotalFruitChecked = QADATAFRAME['FruitChecked'].sum()
            BNPCT = QADATAFRAME['BruiseNew'].sum() / TotalFruitChecked * 100
            if BNPCT <= DefectLowerLimit:
                BNPCTCOLOUR = 'lime green'
            if BNPCT > DefectLowerLimit and BNPCT <= DefectUpperLimit:
                BNPCTCOLOUR = 'yellow'
            if BNPCT > DefectUpperLimit:
                BNPCTCOLOUR = 'tomato2'
            BOPCT = QADATAFRAME['BruiseOld'].sum() / TotalFruitChecked * 100
            if BOPCT <= DefectLowerLimit:
                BOPCTCOLOUR = 'lime green'
            if BOPCT > DefectLowerLimit and BOPCT <= DefectUpperLimit:
                BOPCTCOLOUR = 'yellow'
            if BOPCT > DefectUpperLimit:
                BOPCTCOLOUR = 'tomato2'
            SBPCT = QADATAFRAME['Sunburn'].sum() / TotalFruitChecked * 100
            if SBPCT <= DefectLowerLimit:
                SBPCTCOLOUR = 'lime green'
            if SBPCT > DefectLowerLimit and SBPCT <= DefectUpperLimit:
                SBPCTCOLOUR = 'yellow'
            if SBPCT > DefectUpperLimit:
                SBPCTCOLOUR = 'tomato2'
            CLPCT = QADATAFRAME['Colour'].sum() / TotalFruitChecked * 100
            if CLPCT <= DefectLowerLimit:
                CLPCTCOLOUR = 'lime green'
            if CLPCT > DefectLowerLimit and CLPCT <= DefectUpperLimit:
                CLPCTCOLOUR = 'yellow'
            if CLPCT > DefectUpperLimit:
                CLPCTCOLOUR = 'tomato2'
            HLPCT = QADATAFRAME['Hail'].sum() / TotalFruitChecked * 100
            if HLPCT <= DefectLowerLimit:
                HLPCTCOLOUR = 'lime green'
            if HLPCT > DefectLowerLimit and HLPCT <= DefectUpperLimit:
                HLPCTCOLOUR = 'yellow'
            if HLPCT > DefectUpperLimit:
                HLPCTCOLOUR = 'tomato2'
            INPCT = QADATAFRAME['Insect'].sum() / TotalFruitChecked * 100
            if INPCT <= DefectLowerLimit:
                INPCTCOLOUR = 'lime green'
            if INPCT > DefectLowerLimit and INPCT <= DefectUpperLimit:
                INPCTCOLOUR = 'yellow'
            if INPCT > DefectUpperLimit:
                INPCTCOLOUR = 'tomato2'
            MDPCT = QADATAFRAME['MiscDamage'].sum() / TotalFruitChecked * 100
            if MDPCT <= DefectLowerLimit:
                MDPCTCOLOUR = 'lime green'
            if MDPCT > DefectLowerLimit and MDPCT <= DefectUpperLimit:
                MDPCTCOLOUR = 'yellow'
            if MDPCT > DefectUpperLimit:
                MDPCTCOLOUR = 'tomato2'
            SizeListRange = ["Size_1", "Size_2", "Size_3", "Size_4", "Size_5", "Size_6", "Size_7", "Size_8", "Size_9", "Size_10", "Size_11", "Size_12", "Size_13", "Size_14", "Size_15", "Size_16", "Size_17", "Size_18", "Size_19", "Size_20"]
            AllSizesList = []
            for column in SizeListRange:
                columnslist = QADATAFRAME[column].tolist()
                for idvsize in columnslist:
                    AllSizesList.append(idvsize)
            AllSizesList = [x for x in AllSizesList if x is not None]
            try:
                AVGSZ = sum(AllSizesList) / len(AllSizesList)
            except ZeroDivisionError:
                AVGSZ = 0
            if AVGSZ <= SizeLowerLimit:
                AVGSZCOLOUR = 'tomato2'
            if AVGSZ > SizeLowerLimit and AVGSZ <= SizeUpperLimit:
                AVGSZCOLOUR = 'lime green'
            if AVGSZ > SizeUpperLimit:
                AVGSZCOLOUR = 'tomato2'
            layoutB = [ [sg.Text('CHECK STATS', font=("", 25, "bold"))],
                        [sg.Text('Bruise New = ' + str(int(BNPCT)) + '%', font=("", 35, "bold"), text_color=BNPCTCOLOUR)],
                        [sg.Text('Bruise Old = ' + str(int(BOPCT)) + '%', font=("", 35, "bold"), text_color=BOPCTCOLOUR)],
                        [sg.Text('Sunburn = ' + str(int(SBPCT)) + '%', font=("", 35, "bold"), text_color=SBPCTCOLOUR)],
                        [sg.Text('Colour = ' + str(int(CLPCT)) + '%', font=("", 35, "bold"), text_color=CLPCTCOLOUR)],
                        [sg.Text('Misc Damage = ' + str(int(MDPCT)) + '%', font=("", 35, "bold"), text_color=MDPCTCOLOUR)],
                        [sg.Text('Hail = ' + str(int(HLPCT)) + '%', font=("", 35, "bold"), text_color=HLPCTCOLOUR)],
                        [sg.Text('Insect = ' + str(int(INPCT)) + '%', font=("", 35, "bold"), text_color=INPCTCOLOUR)],
                        [sg.Text('AVG Size = ' + str(int(AVGSZ)) + 'mm', font=("", 35, "bold"), text_color=AVGSZCOLOUR)],
                        [sg.Button('Done', font=("", 30, "bold"))], [sg.Button('Back', font=("", 30, "bold"))]]
            window = sg.Window('Row Job Manager', layoutB).Finalize()
            window.Maximize()
            event, values = window.read()
            if event == 'Done':
                window.close()
            else:
                window.close()
        else:
            window.close()