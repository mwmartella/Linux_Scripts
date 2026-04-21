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

def AppleSize(SizeList):
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
    FileList = ['APG6.jpeg']
    for file in FileList:
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
        image = cv2.imread(file)
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
