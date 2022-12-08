import cv2
import csv
import os
import numpy as np
import sys
from pathlib import Path

#   Skips every 1/n frames, according to this ratio. 
#   Maybe do random frame n*frameCount instead?
percentExtractedPerVideo = 0.3
firstNvideos = 6
resizeWidth = 480
resizeHeight = 270

groundsPath = "src/python/groundTruth/"

###     Generates a dataset of labelled images from one video (soon a whole folder) by comparing to ground truth.
###         Takes about 5 minutes for a 30 minute input.
def generateDatasetFromFrames(inputVideosPath, extractionRatio):
    for i in range(firstNvideos):
        curVideo = os.listdir(inputVideosPath)[i]
        decoder = cv2.VideoCapture(inputVideosPath + curVideo)

        desiredFPS = int(cv2.CAP_PROP_FPS * extractionRatio)

        sourceNoExt = os.path.splitext(curVideo)[0]
        groundTruthName = "groundTruth_" + sourceNoExt + ".csv"
   
        # Looks for ground truth csv.
        groundFound = False
        for file in os.listdir(groundsPath):
            if file == groundTruthName:
                groundTruthCSV = open(groundsPath+file)
                groundFound = True
                break

        if groundFound == False:
            print("No ground truth file found to label from, for file {file}.\n".format(file = curVideo))
            continue

        step = int(decoder.get(cv2.CAP_PROP_FPS) / desiredFPS)
        try:
            # Frame reading loop
            while True:
                ret, frame = decoder.read()
                if not ret:
                    break

                #   Frame index is one less because .read() gives index of next frame, not current.
                #   Also does modulo step to simulate lower FPS.    
                frameNo = int(decoder.get(cv2.CAP_PROP_POS_FRAMES)-1)
                if frameNo % step == 0:
                    frame = cv2.resize(frame, (resizeWidth, resizeHeight), cv2.INTER_CUBIC)
                    curTime_s = int(decoder.get(cv2.CAP_PROP_POS_MSEC)/1000)

                    found = False
                    truthReader = csv.reader(groundTruthCSV)
                    for row in truthReader:
                        #   Checks that the time, in seconds, of the current frame, is between an interval in the ground truth
                        if (int(row[0]) <= curTime_s) and (int(row[1]) >= curTime_s):
                            cv2.imwrite("dataset/fish/" + "frame{number}{source}.jpg".format(number=frameNo, source=sourceNoExt), frame)
                            found = True
                            break
                
                    #   Resets csv iterator
                    groundTruthCSV.seek(0)
                    if found == False:
                        cv2.imwrite("dataset/noFish/" + "frame{number}{source}.jpg".format(number=frameNo, source=sourceNoExt), frame)
            print("Frames saved as labelled images in dataset folder.\n")
        except:
            print("Something went wrong in reading file {file}".format(file = curVideo))

        finally:
            decoder.release()
            groundTruthCSV.close()  

def main(video,fps):
    generateDatasetFromFrames(video,fps)

if __name__ == "__main__":
    main("sourceVideos/", percentExtractedPerVideo) 