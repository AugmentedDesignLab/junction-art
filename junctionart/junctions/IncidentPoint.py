# TODO zarif
# done
class IncidentPoint:
    def __init__(self, x, y, heading) -> None:
        self.x = x
        self.y = y
        self.heading = heading
    
    @staticmethod
    def parseIncidentPoint(ip):
        return IncidentPoint(ip["x"], ip["y"], ip["heading"])

    def __str__(self):
        return f"x : {self.x} y : {self.y} heading : {self.heading}"