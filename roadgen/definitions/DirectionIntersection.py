from roadgen.definitions.DirectionQuadrant import DirectionQuadrant



class DirectionIntersection:


    def __init__(self, top, left, bot, right):

        self.top = top
        self.left = left
        self.bot = bot
        self.right = right

    
    def __str__(self):


        return(
            f"top: {self.top}\n"
            f"left: {self.left}\n"
            f"bot: {self.bot}\n"
            f"right: {self.right}"
        )

