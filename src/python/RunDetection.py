import os
import sys
import ctypes
import VideoTrimmer

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main(inputVideo):
    if is_admin():
        curDir = os.getcwd()
  
        #   Relative path to input folder from the current working directory (often the root of the repo).
        repoRootToBinary = ""
        pathToBinary = os.path.join(curDir, repoRootToBinary)
        os.chdir(pathToBinary)

        #   Creates input/output folders for videofiles.
        if "output" not in os.listdir():
            os.mkdir("output")
        if "input" not in os.listdir():
            os.mkdir("input")
            # Log instead of print
            print("No input folder found. Creating it now. Place input video files in that folder.")
            return
        print("Processing file {file}".format(file=inputVideo))

        #   Classical algorithm, C++ binary
        #os.system("opencvtest.exe {input}".format(input="input/{file}".format(file=inputVideo)))



        prefix, ext = os.path.splitext(inputVideo)
        print("\nVideo processed and outputted to {csv}.".format(csv=prefix+".csv"))
        print("Starting trimming now...")
        VideoTrimmer.readForCSV(inputVideo)

main("test.mp4")