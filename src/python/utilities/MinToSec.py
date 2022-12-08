# Programm that takes a csv with timestamps from videofiles in formats hr.min.sec 
# or min.sec or sec entrys  and converts them to only seconds.
# It needs a groundTruth.csv file as an input. This file should have a header
# with the videofilename
# Example of csv file that will work: 
# Myggbukta-101
# 40, 58
# 1.49, 3.56
# 1.10.30, 1.13.45  
# The header makes it so in this example you get an outputfile named groundTruthMyggbukta-101.csv


import csv
delimiter = "."
file = open('groundTruth.csv')
csvreader = csv.reader(file)
header = []
header = next(csvreader)
secs = []
for row in csvreader:
    newRow = []
    for item in row:
        newRow.append(sum(int(x) * 60 ** i for i, x in enumerate(reversed(item.split(delimiter)))))  #Stack overflow https://stackoverflow.com/questions/6402812/how-to-convert-an-hmmss-time-string-to-seconds-in-python
    secs.append(newRow)    
file.close
for name in header:
    filename = "groundTruth" + name + ".csv"
with open(filename, 'w', newline="") as newFile:
    csvwriter = csv.writer(newFile)
    #csvwriter.writerow(header)
    for row in secs:
        csvwriter.writerow(row)