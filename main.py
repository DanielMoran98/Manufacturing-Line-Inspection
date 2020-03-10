import cv2 as cv
import numpy as np
import time
import math
import matplotlib.pyplot as plt
import queue
import sys
import os
from calculations import *

def threshold(img, thresholdValue):
    # Returns: The image with thresholding applied
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if img[x,y] > thresholdValue:
                img[x,y] = 255
            else:
                img[x,y] = 0
    return img

def binaryMorph(img):
    # Returns: The image with binary morphology applied
    imgCopy = img.copy()
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if ( x == 0 or x == img.shape[0]-1) or (y == 0 or y == img.shape[1]-1):
                pass# print("At edge") # At corner of edge of image, do nothing
            elif img[x,y] == 255: #If pixel is white, check surrounding neighbors
                # print(img.shape[1])
                imgCopy[x,y] = checkNeighbors(imgCopy, x, y)
    return imgCopy

def checkNeighbors(img, x, y):
    # Returns: A black pixel if there are more than 4 foreground neighbors, otherwise a white pixel
    backgroundCount = 0
    foregroundCount = 0
    neighbors = [img[x-1,y+1],
    img[x,y+1],
    img[x+1,y+1],
    img[x+1,y],
    img[x+1,y-1],
    img[x,y-1],
    img[x-1,y-1],
    img[x-1,y]
    ]

    for neighbor in neighbors:
        if neighbor == 255:
            backgroundCount += 1
        elif neighbor == 0:
            foregroundCount += 1

    if foregroundCount > 4:
        # print(str(img[x,y])+" Foreground count greater than 4")
        return 0
    else:
        # print(str(img[x,y])+ " Foreground count <= 4")
        return 255

def labelComponenents(img):
    # Returns: An image, with each individual component given its own label (0,1,2...)
    labels = img.copy()
    curLab = 1

    q = queue.Queue()
    
    # Set all vals in new array to 0
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            labels[x,y] = 0
    
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            # For each pixel
            if labels[x,y] == 0 and img[x,y] == 0:
                # If unvisited, and a foreground pixel
                labels[x,y] = curLab
                q.put([x,y])

                # Loop while queue isnt empty, when it is empty we increment curLab
                while q.qsize() != 0:
                    element = q.get()
                    neighbors = [
                        [element[0]+1, element[1]],
                        [element[0]-1, element[1]],
                        [element[0], element[1]+1],
                        [element[0], element[1]-1]
                    ]

                    #For each neighbor
                    for neighbor in neighbors:
                        if img[neighbor[0],neighbor[1]] == 0 and labels[neighbor[0], neighbor[1]] == 0:
                            labels[neighbor[0], [neighbor[1]]] = curLab
                            q.put(neighbor)  
                curLab += 1   

   
    return labels
    
def classify(img, centroid):
    # Returns: A verdict of whether the image should pass or fail

    boundsRatio = round(getBoundsRatio(img, centroid), 2)
    circularity = round(getCircularity(img, 1, centroid, imageNumber), 2)
    verdict = "UNSURE"
    verdictColor = '\033[92m'

    if(boundsRatio > 0.18):
        verdict = "FAIL (SNAPPED)"
        verdictColor = "\033[91m"
    elif(circularity > 11.0):
        verdict = "PASSED"
    
    if(verdict == "UNSURE"):
        if boundsRatio < 0.1:
            verdict = "PASSED"            
        else:
            verdict = "FAIL (FAULTY) "
            verdictColor = "\033[91m"
    
    print(verdictColor + str(imageNumber)+" - "+str(verdict)+" | "+str(boundsRatio)+" | "+ str(circularity)+'\033[0m')
    return verdict

def displayLabelled(img, centroid, verdict, originalImg):
    # Returns: An image with labelling/text applied
    img = img.copy()
    r = getRadius(img, centroid)

    mostFrequent = 0
    freq = [0,0,0,0]

    # Get the amount of different labels
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if img[x,y] > 0:
                freq[img[x,y]] += 1
    # Set the most frequent label so we can identify the O-ring over broken pieces
    mostFrequent = np.argmax(freq)
    
    for x in range(0, img.shape[0]):
        for y in range(0, img.shape[1]):
            if img[x,y] > 0 and img[x,y] != mostFrequent:
                img[x,y] = 100
            elif img[x,y] == mostFrequent:
                img[x,y] = 255

    font = cv.FONT_HERSHEY_SIMPLEX

    img = cv.cvtColor(img,cv.COLOR_GRAY2RGB)
    if verdict == "PASSED":
        cv.putText(img, str(verdict), (5,20), font, 0.4, (0,255,0), 1, cv.LINE_AA)
    else:
        cv.putText(img, str(verdict), (5,20), font, 0.4, (0,0,255), 1, cv.LINE_AA)

    cv.putText(img, 'Time: ' +str(timeTaken)+" sec", (5,210), font, 0.4, (255,255,255), 1, cv.LINE_AA)
    cv.circle(img, (centroid[1], centroid[0]), round(r[0]), (50,50,255), 1)
    cv.circle(img, (centroid[1], centroid[0]), round(r[1]), (20,20,255), 1)
    cv.circle(img, (centroid[1], centroid[0]), 1, (0,0,255), 2)


    # cv.imshow('Original', originalImg)
    cv.imshow('Final', img)
    cv.waitKey(0)
    cv.destroyAllWindows()

    return img

def outputToFile(img, imageNumber):
    cv.imwrite( "./example_output/Oring"+str(imageNumber)+".jpg", img )

def imhist(img):
    # Returns: A histogram of pixel values of an image
    hist = np.zeros(256)
    for i in range(0, img.shape[0]):
        for j in range(0, img.shape[1]):
            hist[img[i,j]]+=1
    return hist




###### BEGIN #####
# Pass in an argument to view specific image, otherwise it will loop through them all
# E.g if you want to view O-ring 5:     'python main.py 5' 
 
imageNumber = 1
imageCount = 14


if len(sys.argv) > 1:
    imageNumber = int(sys.argv[1])
    imageCount = int(sys.argv[1])

while imageNumber <= imageCount:
    # Read in an image
    cwd = os.getcwd()
    img = cv.imread(r'.\images\Oring'+ str(imageNumber) +'.jpg',0)
    originalImg = img.copy()
    before = time.time()

    # plt.plot(imhist(img))
    # plt.show()

    # Get the average grey value of the image, then use that to get the correct threshold value
    averageGrey = getAverageGrey(img)
    thresholdValue = getThresholdValue(img, averageGrey)

    # Threshold the image into black and white, with the foreground being white pixels, and the background being black
    img = threshold(img, thresholdValue)
    img = binaryMorph(img)

    # Perform component labelling, gives all background pixels val 0, then each component afterwards gets a unique value
    # the most frequent component is considered the O-ring
    labelledArray = labelComponenents(img)



    # Gets the center value of the O-ring
    centroid = getCentroid(labelledArray, 1)
    
    # Classifies the o-ring as a pass or fail
    verdict = classify(labelledArray, centroid)
    after = time.time()
    timeTaken = round(after-before, 2)

    # Display the final image
    finalImg = displayLabelled(labelledArray, centroid, verdict, originalImg)
    
    outputToFile(finalImg, imageNumber)
    imageNumber += 1


cv.destroyAllWindows()
