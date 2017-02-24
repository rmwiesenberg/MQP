#______ _                       ___  ______________
#| ___ \ |                      |  \/  |  _  | ___ \
#| |_/ / |_   _ _ __ ___   ___  | .  . | | | | |_/ /
#|  __/| | | | | '_ ` _ \ / _ \ | |\/| | | | |  __/
#| |   | | |_| | | | | | |  __/ | |  | \ \/' / |
#\_|   |_|\__,_|_| |_| |_|\___| \_|  |_/\_/\_\_|
#
#
#Map.py
#
#Cartography for Robots
#every pixel is a cm
#
#Ryan Wiesenberg
#Eric Fast
#Stepthen Harnais

import sys
import Gas

sys.path.append('libs/')
from libs.graphics import *

class Map:
    MINCON = 600
    MAXCON = 1600
    ROBOT = .35
    def __init__(self, id,  sizeX=600, sizeY=600, scale=100):
        self.win = GraphWin(("Robot"), sizeX, sizeY)

        self.scale = scale

        self.sizeX = sizeX
        self.sizeY = sizeY

        self.centerX = sizeX/2
        self.centerY = sizeY/2

        self.gasses = []

        return

    def addGas(self, gas):
        #don't forget that the axis get rotated with the camera
        con = gas.getCon()
        newgas = [Circle(Point((self.centerX+(gas.getY()*self.scale)),
                                    (self.centerY-(gas.getX()*self.scale))), 1),
                                    con]
        self.gasses.append(newgas)
        newgas[0].draw(self.win)

        #set min and max concentrations
        if con < self.minCon:
            self.minCon = con
        if con > self.maxCon:
            self.maxCon = con

        self.robot = Circle(Point(self.sizeX*2, self.sizeY*2),
                            int(Map.ROBOT*self.scale))
        return

    #convert concentration value to color based on the min and max Cons
    #its just linear interpolation
    def getColor(self, value):
        spanCon = Map.maxCon - Map.minCon

        valueScaled = float(value - Map.minCon) / float(spanCon)

        #return scaled value
        return 0 + (valueScaled * 255)

    #takes in a robot
    #puts robot on the map
    #we made it fam!
    def updateRobot(self, robot):
        self.robot.undraw()
        self.robot = Circle(Point((self.centerX+(robot.getY()*self.scale)),
                                    (self.centerY-(robot.getX()*self.scale))),
                                    int(Map.ROBOT*self.scale))
        self.robot.setFill("white")
        self.robot.draw(self.win)
        return

    #updates gas colors and draws them
    def updateGas(self):
        for gas in self.gasses:
            val = self.getColor(gas[1])
            color = color_rgb(int(val),int(255-val),int(0))
            gas[0].setFill(color)
            gas[0].setOutline(color)
            self.win.update()
        return
