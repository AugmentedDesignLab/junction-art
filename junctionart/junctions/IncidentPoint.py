# TODO zarif
# done
class IncidentPoint:
    def __init__(self, x, y, heading, leftLane, rightLane, medianType, skipEndpoint) -> None:
        self.x = x
        self.y = y
        self.heading = heading
        self.leftLane = leftLane
        self.rightLane = rightLane
        self.medianType = medianType
        self.skipEndpoint = skipEndpoint
    
    @staticmethod
    def parseIncidentPoint(ip):
        return IncidentPoint(ip["x"], ip["y"], ip["heading"], ip["leftLane"], ip["rightLane"], ip["medianType"], ip["skipEndpoint"])