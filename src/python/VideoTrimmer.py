from time import sleep
import os
import csv
import logging
import sys
import ffmpeg
import subprocess
import Jaccard from utilities

# Logger for logging purposes (seeing which file is currently being processed)
logFormat = "%(levelname)s %(asctime)s - %(message)s"

logging.basicConfig(stream = sys.stdout, 
                    filemode = "w",
                    format = logFormat, 
                    level = logging.INFO)

#   Trims input video file according to interval of timestamps given in CSV.
#   Uses ffmpeg-python, which builds a command-line call to ffmpeg that trims parts and finally concatenates them.
#   Does NOT delete input video file yet.
def trim(inputVideo, csvTimestamps):
    os.chdir("..")
    inputPath = os.path.join(os.getcwd(), "input\\{inputVid}".format(inputVid=inputVideo))
    outputPath = os.path.join(os.getcwd(), "output\\{outputVid}".format(outputVid=inputVideo))
    paddingSecs = 1
    trims = []

    # Removes duplicate intervals (start==end)
    dupeClean = []
    for timestampNo in range(len(csvTimestamps)):
        if csvTimestamps[timestampNo][0] != csvTimestamps[timestampNo][1]:
             dupeClean.append(csvTimestamps[timestampNo])
    
    print(dupeClean)
    for i in range(len(dupeClean)):
        # Trims the source video for each interval. 'setpts' filter is used so timestamps are handled correctly; without it,
        #       still frames will appear in the final video, as it trims based on closest keyframes and fills the gap with stills.
        trims.append(ffmpeg.input(inputPath).trim(start=dupeClean[i][0], end=dupeClean[i][1]).filter('setpts', expr='PTS-STARTPTS'))
    
    #(
    #    ffmpeg
    #    .concat(*trims)
    #    .filter('setpts', expr='PTS-STARTPTS')
    #    .output(outputPath)
    #    .run(quiet=True)
    #)

def doesGroundTruthExist(groundTruthInput):
    for file in os.listdir():
        if file == groundTruthInput:
            return True
    return False

def readForCSV(inputVideoName):
    inputNoExt = os.path.splitext(inputVideoName)[0]
    os.chdir("input")
    if inputVideoName in os.listdir():
        #   Checks if there is a .csv in the directory. If there is, tries to trim according to timestamps.
        #   Expects even-sized appropriately timed timestamps in seconds of the input video.
        #   Example: {5, 33, 106, 180} -> Two intervals of length 28 and 74 seconds respectively.
        videoFound = False
        groundTruthName = "groundTruth_" + inputNoExt + ".csv"
 
        for file in os.listdir():
            if os.path.splitext(file)[0] == inputNoExt and file.endswith(".csv"):
                videoFound = True
                print(".csv file with same name as input video found")

                with open(file) as csvFile:
                    reader = csv.reader(csvFile, delimiter=",")

                    # Calculates Jaccard index if ground truth file exists.
                    if doesGroundTruthExist(groundTruthName):
                        # Log instead of print
                        print("Ground truth file found for video {video}, calculating success rate:".format(video=inputVideoName))

                        with open(groundTruthName) as truthFile:
                            truthReader = csv.reader(truthFile, delimiter=",")
                            # Cast whole csv input as a list of integers.
                            obsList = [[int(i) for i in interval] for interval in list(reader)]
                            trueList = [[int(i) for i in interval] for interval in list(truthReader)]
                            Jaccard.calculateSuccess( obsList, trueList )
                    
                    #trim(inputVideoName, list(reader))
                    print("Done, trimmed file in output folder.")
                    break

        if not videoFound:
            # Log instead of print.
            print("Input video file found, but no .csv file generated or found.")
    else:
        # Log instead of print.
        print("Input video file not found.")
               