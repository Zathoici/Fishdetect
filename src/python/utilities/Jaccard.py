# Expecting two lists of several pairs representing the start and end of each interval.
# EXAMPLE: 
#   Observed: [ (3, 4), (5, 9), (6, 11) ]
#   True: [ (2, 4), (5, 10), (10, 12) ]
def calculateSuccess(observedIntervalsList, trueIntervalsList):
    cumulativeIntersection = 0
    cumulativeObs = 0
    cumulativeTrue = 0
    for obsInt in observedIntervalsList:
        cumulativeObs += obsInt[1]-obsInt[0]

        # Calculates the similarity index by considering the index of each observed interval with respect to how many true intervals are overlapping it.
        for i in range(len(trueIntervalsList)):
            # Checks if true interval overlaps with observed. No bias in direction, meaning observed interval too low has same error as too high.
            # Can be changed by adding more if statements based on the condition, so that having observed intervals too high is punished less than too low.
            if not (obsInt[0] > trueIntervalsList[i][1] or obsInt[1] < trueIntervalsList[i][0]):
                cumulativeIntersection += min(obsInt[1], trueIntervalsList[i][1]) - max(obsInt[0], trueIntervalsList[i][0])

    # Both lists of intervals are assumed to be SORTED.
    for trueInt in trueIntervalsList:
        cumulativeTrue += trueInt[1]-trueInt[0]

    union = cumulativeObs + cumulativeTrue
    index = cumulativeIntersection / union
    ratioObsToReal = cumulativeObs / cumulativeTrue
    print("    Correctness: {:.4f}".format(index) + ", or {:.1f}%".format(index*100))
    print("    Observed-to-expected ratio: {:.2f}".format(ratioObsToReal) + " --> {sensitivity}".format(sensitivity=("Too sensitive" if ratioObsToReal>1 else "Not sensitive enough")))