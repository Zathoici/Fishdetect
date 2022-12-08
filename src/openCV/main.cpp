#include <cstddef>
#include <ctime>
#include <iostream>
#include <stdlib.h>
#include <filesystem>
#include <fstream>
#include <chrono>
#include <math.h>

#include <opencv2/opencv.hpp>
#include <opencv2/bgsegm.hpp>

using namespace std;
using namespace cv;

// Creates a new csv file based on a filepath with name videofilename.csv
ofstream createCSV(filesystem::path videoFilePath);

//  Defines change between frames as XOR bitwise operation between pixel pairs mapped to same position,
//    and returns true for when the ratio of the sum of those changes is sufficiently large.
bool detectChange(Mat firstFrame, Mat secFrame);

double percentChangeThreshold = 0.001;
double avg = 0;

int main(int argc, char** argv) {
  if (argc != 2) {
    cerr << "Have to pass 1 and only 1 argument.";
    cerr << endl;
    return -1;
  }

  filesystem::path videoPath(argv[1]);
  if(videoPath.extension() != ".mp4") {
    cerr << "Failed to read input; make sure it is a valid .mp4 video file." << endl;
    cerr << "Current input: " << argv[1];
    return -1;
  }

  ofstream csv = createCSV(videoPath);

  VideoCapture decoder(videoPath.string());
  auto start = chrono::steady_clock::now();

  int detectionsPerSec = 3;

  // Amount of extra time each detection interval will be padded with.
  double paddingTime_s = 1;

  /*    Parameters on CNT background subtractor:
    minPixelStability	number of frames with same pixel color to consider stable
    useHistory	determines if we're giving a pixel credit for being stable for a long time
    maxPixelStability	maximum allowed credit for a pixel in history
    isParallel	determines if we're parallelizing the algorithm
  */
  //Ptr<BackgroundSubtractor> p_bgSub = bgsegm::createBackgroundSubtractorCNT(detectionsPerSec, true, 4*detectionsPerSec, true);
  Ptr<BackgroundSubtractor> p_bgSub = bgsegm::createBackgroundSubtractorGSOC( 0,20,0.003f,0.01f,32,0.01f,0.0022f,0.1f,0.1f,0.0004f,0.0008f );	


  // Pre-allocation of variables
  vector<bool> motionVec;
  double simFPS = decoder.get(CAP_PROP_FPS) / detectionsPerSec;
  int simFrameTime = decoder.get(CAP_PROP_FRAME_COUNT) / simFPS;
  motionVec.reserve(simFrameTime);

  Mat frame;    
  Mat nextFrame;   
  Mat binaryFrame;
  Mat binaryNextFrame;
  Mat medianBlurFrame;    
  Mat medianBlurNextFrame;
  int blurRadius = 5;

  int32_t height = decoder.get(CAP_PROP_FRAME_HEIGHT);
  int32_t width  = decoder.get(CAP_PROP_FRAME_WIDTH);

  int32_t newHeight = height/2;
  int32_t newWidth = width/2;

  bool gotFrame, gotNextFrame;
  while (gotFrame = decoder.read(frame)) {
    // Skips some amount of "real" frames to reach desired "simulated fps".
    for(int i = 0; i < simFPS-1; i++) {
      decoder.grab();
    }
    gotNextFrame = decoder.read(nextFrame);

    // Applies bg segmentation, median filter to reduce noise, and pushes the change detection result to output vector.
    // The frame count might be inaccurate at the moment, such that real frame 24 at time 1s, might be declared as being at time 0.9s. Needs testing.
    if (gotFrame && gotNextFrame) {
      resize(frame, frame, Size(newWidth, newHeight), 0, 0, INTER_CUBIC);
      resize(nextFrame, nextFrame, Size(newWidth, newHeight), 0, 0, INTER_CUBIC);

      p_bgSub->apply(frame, binaryFrame, -1);
      p_bgSub->apply(nextFrame, binaryNextFrame, -1);

      // Code runs 30min input file in ~9 minutes. Reducing this median blur value from 7 -> 5, yields run time of ~2 minutes, but more noisy output.
      medianBlur(binaryFrame, medianBlurFrame, blurRadius);
      medianBlur(binaryNextFrame, medianBlurNextFrame, blurRadius);
      
      motionVec.push_back(detectChange(medianBlurFrame, medianBlurNextFrame));
    } else { break; }
  }

  decoder.release();
  double test = avg / (double)simFrameTime;
  cout << test << "\n";

  // Detection interval padding logic; essentially applies 1D dilation (morphological operation).
  int framesPaddedEachSide = ceil((paddingTime_s/2)*detectionsPerSec + 0.5);
  vector<bool> dilated = motionVec;
  /*for(int i=0; i<motionVec.size(); i++) {
    if (motionVec.at(i) == 1) {
      for(int k = -framesPaddedEachSide; k <= framesPaddedEachSide; k++) {
        int index = i+k;
        if (index < 0 || index >= motionVec.size()) { continue; }
        dilated.at(index) = 1;
      }
    }
  }*/

  // Timestamp generator logic; converts simulated frame index to real time in input file. As mentioned above, the math might be inaccurate.
  double timePerSimFrame_s = 1/(double)detectionsPerSec;
  double runStart_s, runEnd_s;
  for(int i=0; i<dilated.size(); i++) {
    runStart_s = i*timePerSimFrame_s;
    int runCounter = 0;
    bool nextIsWithinBounds = i+runCounter < dilated.size();
      while(nextIsWithinBounds) {
        if(dilated[i+runCounter] == 1) { runCounter++; } 
        else { break; }
        nextIsWithinBounds = i+runCounter < dilated.size();
      }
    runEnd_s = runStart_s + timePerSimFrame_s*runCounter;
    i += runCounter;
    if (runCounter>0) {
      csv << floor(runStart_s) << "," << ceil(runEnd_s) << "\n";
    }
  }
  
  csv.close();

  auto end = chrono::steady_clock::now();
  auto elapsed = chrono::duration_cast<chrono::seconds>(end - start).count();
  int minutes = floor(elapsed/60);
  int seconds = floor(elapsed-(minutes*60));
  cout << "Elapsed(mm:ss)=" << minutes << ":" << seconds << endl;
  return 0;
}

ofstream createCSV(filesystem::path videoFilePath) {
  filesystem::path csvPath(videoFilePath.string());
  ofstream csv(csvPath.replace_extension(".csv").string());
  return csv;
}

bool detectChange(Mat firstFrame, Mat secFrame) {
  Mat xorMapMat = Mat::zeros(firstFrame.rows, firstFrame.cols, CV_8U);

  uint8_t* xorMapArr = (uint8_t*)xorMapMat.data;
  uint8_t* firstFrameArr = (uint8_t*)firstFrame.data;
  uint8_t* secFrameArr = (uint8_t*)secFrame.data;

  long sum = 0;
  for(int i = 0; i < firstFrame.rows; i++)
  {
    for(int j = 0; j < firstFrame.cols; j++)
    {
        int pos = i*j + j;
        sum += firstFrameArr[pos] | secFrameArr[pos];
    }
  }
  double ratio = (double)sum/(255*firstFrame.rows*firstFrame.cols);
  avg += ratio;
  return ratio > percentChangeThreshold;
}