import cv2 as cv
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import queue
import sys


def getAverageGrey(img):
    # Returns: The average grey value of each image pixel

    cellCount = 0
    sum = 0
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            sum = sum + img[i, j]
            cellCount = cellCount + 1

    average = sum // cellCount
    return average

def getThresholdValue(img, averageGrey):
    # Returns: The correct thresholding value for our image

    flag = 1
    lastThreshold = 0
    c1 = [] # Greater than T
    c2 = [] # Less than T

    while flag == 1:
        for i in range(0, img.shape[0]):
            for j in range(0, img.shape[1]):
                if img[i,j] > averageGrey:
                    c1.append(img[i,j])
                else:
                    c2.append(img[i,j])
        c1.clear
        c2.clear

        c1Avg = round(np.mean(c1))
        c2Avg = round(np.mean(c2))

        threshold = (c1Avg + c2Avg) / 2
        if threshold - lastThreshold < 1:
            flag = 0
        else:
            lastThreshold = threshold

    return threshold

def getCentroid(img, label):
    # Returns: The central pixel to our O-ring component
    img = img.copy()

    centroid = (0,0)
    x_sum = 0
    y_sum = 0
    labelCount = 0
    x = 0
    y = 0

    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if(img[x,y] == label):
                x_sum += x
                y_sum += y
                labelCount += 1
            y += 1
        x += 1
    

    x_avg = round(x_sum / labelCount)
    y_avg = round(y_sum / labelCount)


    centroid = [x_avg, y_avg]
    return centroid

def getDistance(x1, y1, x2, y2):
    # Returns: The distance between two points
    xDifference = x1-x2
    yDifference = y1-y2

    return math.sqrt((xDifference*xDifference) + (yDifference * yDifference))

def getCircularity(img, label, centroid, imageNumber):
    # Returns: The circularity value for an O-ring
    img = img.copy()
    distances = []

    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if img[x,y] == label:
                # if img[x+1,y] == 0 or img[x-1,y] == 0 or img[x,y+1] == 0 or img[x,y-1] == 0:
                distance = getDistance(x,y,centroid[0],centroid[1])
                # print(distance)
                distances.append(distance)
    
    meanDistances = np.mean(distances)
    standardDeviation = np.std(distances)
    circularity = meanDistances / standardDeviation
    # print("[" + str(imageNumber) + "] Circularity: "+ str(circularity))
    return circularity

def getRadius(img, centroid):
    # Returns: The inner radius, outer radius, and thickness of an O-ring
    img = img.copy()
    innerRadius = 0
    outerRadius = 0
    thickness = 0

    x = centroid[0]
    y = centroid[1]

    # location:    0:Within O-ring   1: On O-ring   2: Outside Oring
    location = 0

    
    while location != 2:
        if location == 0 and img[x,y] == 1:
            location = 1
            innerRadius = getDistance(x, y, centroid[0], centroid[1])
        elif location == 1 and img[x,y] == 0:
            location = 2
            outerRadius = getDistance(x, y, centroid[0], centroid[1])
        x += 1
    
    thickness = outerRadius - innerRadius
    # print("Outer R: " + str(outerRadius))
    # print("Inner R: " + str(innerRadius))
    # print("Thickness: " + str(thickness))
    return (outerRadius, innerRadius, thickness)

def isInsideCircle(img, centroid, x, y, radius):
    # Returns: Whether or not a point is within a certain radius of the centroid  (1/0)   
    if (x - centroid[0])**2 + (y - centroid[1])**2 < radius**2:
        # print("Point inside circle")
        return 1
    elif (x - centroid[0])**2 + (y - centroid[1])**2 > radius**2:
        # print("Point outside circle")
        return 0

def getBoundsRatio(img, centroid):
    # Returns: The ratio of pixels that are out of bounds (Black inside inner radius, white in the actual ring) to the total amount
    img = img.copy()

    r = getRadius(img, centroid)
    outerRadius = r[0]
    innerRadius = r[1]

    whiteCounter = 0
    totalOutOfBounds = 0
    totalInBounds = 0


    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            insideOuter = isInsideCircle(img, centroid, x, y, outerRadius)
            insideInner = isInsideCircle(img, centroid, x, y, innerRadius)
            if(img[x,y] == 1):
                whiteCounter += 1
            if insideOuter and not isInsideCircle(img, centroid, x, y, innerRadius):
                # Inside outer radius, not inside inner radius
                if img[x,y] == 1:
                    totalInBounds += 1
                elif img[x,y] == 0:
                    totalOutOfBounds += 1
            elif insideInner:
                #Inside inner radius
                if img[x,y] == 1:
                    totalOutOfBounds += 1
            elif not insideOuter and not insideInner:
                # Outside both radius
                if img[x,y] == 1:
                    totalOutOfBounds +=1

    ratio = totalOutOfBounds / totalInBounds
    # print("["+str(imageNumber)+"] Total in bounds: "+str(totalInBounds) + " | "+str(totalOutOfBounds)+" : Total out of bounds \t"+str(round(ratio, 2)) )
    return (ratio)
