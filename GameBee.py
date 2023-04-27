#################################################
# Game Bee
# Tracy Yang, tracyy
# 
# Bee GIF from: https://media.giphy.com/media/ksE4eFvxZM3oyaFEVo/giphy.gif

# Project description: There are two flower types: one that can be pollinated
# and one that is a pollinator. You are a bee trying to pollinate the flowers
# with the pollinator flowers. You have two helper bees who automatically goes
# around trying to pollinate the flowers. There is also a feature where you
# can encounter "bad" flowers whos pollen is polluted. If you gather the pollen
# of the bad flower, you lose your entire pollen inventory.
#################################################


from cmu_graphics import *
from PIL import Image
import random, time, math

class Player:
    # the gif loading, draw method, doStep method was taken from 
    # kibleBirdStarter file that the Professor sent out
    def __init__(self, app, x, y):
        #Load the gif
        myGif = Image.open('giphy-unscreen.gif')
        self.spriteList = []
        self.spriteListFlipped = []
        for frame in range(myGif.n_frames):  #For every frame index...
            #Seek to the frame, convert it, add it to our sprite list
            myGif.seek(frame)
            fr = myGif.resize((myGif.size[0]//2, myGif.size[1]//2))
            frL = fr.transpose(Image.FLIP_LEFT_RIGHT)
            frL = CMUImage(frL)
            fr = CMUImage(fr)
            self.spriteList.append(fr)
            self.spriteListFlipped.append(frL)
        
        #Set sprite counters
        self.stepCounter = 0
        self.spriteCounter = 0

        self.x = x
        self.y = y
        self.pollen = [] 
        self.toRemovePollen = set()
        self.flipped = False

    def draw(self):
        if self.flipped:
            spriteLst = self.spriteListFlipped
        else:
            spriteLst = self.spriteList
        drawImage(spriteLst[self.spriteCounter], 
                  self.x, self.y, align = 'center')
    
    def doStep(self):
        self.stepCounter += 1
        if self.stepCounter >= 0.1: 
            self.spriteCounter = (self.spriteCounter + 1) % len(self.spriteList)
            self.stepCounter = 0


    def playerOnStep(self, app):
        self.x += 10*(app.mouseX - self.x)//50
        self.y += 10*(app.mouseY - self.y)//50

class HelperBee(Player):
    def __init__(self, app, x, y):
        super().__init__(app, x, y)
        self.target = None 

    # overrides method
    def playerOnStep(self, app):
        if self.target != None:
            self.x += 10*(self.target.positionX - self.x)//50
            self.y += 10*(self.target.positionY - self.y)//50

    def findTarget(self, app):
        smallestD = None
        closestFlower = None
        # if there is no target
        if self.target == None:
            for flower in app.flowerLst:
                d = distance(self.x, self.y, flower.positionX, flower.positionY)
                # find the pollinator flowers first, make sure it is not 
                # gathered yet, and see if it is in the bee's pollen list
                if (flower.pollinator and flower.gathered == False and 
                    flower not in self.pollen):
                    if smallestD == None or smallestD > d:
                        smallestD = d
                        closestFlower = flower
                # or if there is pollen in the bee's inventory, find a flower
                # that can be pollinated of the same color
                if len(self.pollen) != 0 and flower.pollinated:
                    for i in range(len(self.pollen)):
                        if self.pollen[i].color == flower.color:
                            if smallestD == None or smallestD > d:
                                smallestD = d
                                closestFlower = flower
            self.target = closestFlower
        # if bees has a target
        elif self.target != None:
            for i in range(len(app.flowerLst)):
                # if the flower is still on screen
                if (app.flowerLst[i].ID == self.target.ID):
                    # and if the flower is gathered or pollinated
                    if ((self.target.pollinator and self.target.gathered) 
                        or (self.target.pollinated)):
                        # set target to None and then break out of the loop
                        self.target = None
                        break
            # if target is not on screen
            if self.target not in app.flowerLst:
                self.target = None
    

class Flower:
    colors = ["lightcoral", "plum", "mediumpurple", "lightseagreen", 
              "lightpink", "lightskyblue"]
    ID = 0
    def __init__(self, x, y, pollinated, pollinator):
        self.ID = Flower.ID
        Flower.ID += 1
        self.positionX = x
        self.positionY = y
        self.color = Flower.colors[random.randint(0,5)]

        # for flowers that can be pollinated (ringed)
        self.pollinated = bool(pollinated)
        self.pollinatedR = 30

        # for flowers that is a pollinator
        self.pollinator = bool(pollinator)
        self.pollinatorR = 30

        # only initalizes this property if the flower type is a pollinator
        if self.pollinator:
            self.gathered = False
        
        # randomizes a bad flower
        self.bad = bool(int(random.randrange(0, 2)))
    
    def __repr__(self):
        return f"{self.ID}"
    
    def draw(self):
        # solid circle
        if self.pollinator:
            drawCircle(self.positionX, self.positionY, self.pollinatorR, 
                       fill = None, border = self.color, borderWidth = 10)
            if self.gathered:
                fill = None
            else:
                fill = self.color
            drawCircle(self.positionX, self.positionY, self.pollinatorR-10,   
                       fill = fill)
        # ringed circle
        elif self.pollinated:
            drawCircle(self.positionX, self.positionY, self.pollinatedR, 
                       fill = None, border = self.color)
            drawCircle(self.positionX, self.positionY, self.pollinatedR-10,   
                       fill = self.color)
    
    def flowerOnStep(self, app):
        for flower in app.flowerLst:
            flower.positionX += math.sin(flower.positionY*0.01)
            flower.positionY -= 1

def removeOldPollen(app, bee):
    if len(bee.pollen) > 6:
        bee.pollen.pop(0)

def badPollen(app, bee):
    for flower in bee.pollen:
        if flower.bad:
            bee.pollen = []
            break

def onAppStart(app):
    app.helperBee1 = HelperBee(app, app.width//2, app.height//2)
    app.helperBee2 = HelperBee(app, 200, 300)
    app.player = Player(app, app.width//2, app.height//2)
    app.mouseX = None
    app.mouseY = None
    app.flowerLst = []
    app.counter = 0
    app.toRemoveFlower = set()

    # opening logistics
    app.welcomeScreen = True
    app.instruction = False


def onMouseMove(app, mouseX, mouseY):
    app.mouseX = mouseX
    app.mouseY = mouseY
    if app.mouseX < app.player.x:
        app.player.flipped = True


def onMousePress(app, mouseX, mouseY):
    if app.welcomeScreen and app.instruction == False:
        # start game
        if (630 >= mouseX >= 360) and (520 >= mouseY >= 440):
            app.welcomeScreen = not app.welcomeScreen
        # instruction screen
        if (630 >= mouseX >= 360) and (620 >= mouseY >= 540):
            app.instruction = not app.instruction
    elif app.instruction:
        if (980 >= mouseX >= 790) and (790 >= mouseY >= 730):
            app.welcomeScreen = True
            app.instruction = not app.instruction

def onKeyPress(app, key):
    if key == "i" and app.welcomeScreen == False and app.instruction == False:
        app.welcomeScreen = not app.welcomeScreen
        app.instruction = not app.instruction

def nearFlowerPollinated(app, bee, flower):
    for pollen in bee.pollen:
        # if there is a color in pollen inventory that matches
        if pollen.color == flower.color:
            bee.toRemovePollen.add(flower)
            # gradual growth of pollinated flower until it reaches 
            # a certain radius
            if flower.pollinatedR <= 50:
                flower.pollinatedR += 5
            # gradual growth of the pollinator flower if still on 
            # screen until it reaches a certain radius
            if pollen in app.flowerLst:
                if pollen.pollinatorR <= 50:
                    pollen.pollinatorR += 5


def nearFlower(app, bee):
    # checks if the player is near a flower
    for flower in app.flowerLst:
        if (distance(bee.x, bee.y, flower.positionX, flower.positionY) <= 50):
            # if is a pollinator and is ungathered
            if flower.pollinator and flower.gathered == False:
                flower.gathered = True
                bee.pollen += [flower]
            # if is a flower that can be pollinated
            elif flower.pollinated:
                nearFlowerPollinated(app, bee, flower)
                removePollen(app, bee)
   

def onStep(app):
    if app.welcomeScreen == False and app.instruction == False:
        app.player.doStep()
        app.helperBee1.doStep()
        app.helperBee2.doStep()

        app.counter += 1
        
        # for the first helper bee
        nearFlower(app, app.helperBee1)

        # for the second helper bee
        nearFlower(app, app.helperBee2)

        # for player bee
        nearFlower(app, app.player)
        
        # makes the first helper bee move
        app.helperBee1.playerOnStep(app)

        # makes the second helper bee move
        app.helperBee2.playerOnStep(app)

        # makes the player bee move
        app.player.playerOnStep(app)

        # makes the flowers move
        for flower in app.flowerLst:
            flower.flowerOnStep(app)

        # generates new flowers
        if app.counter % 10 == 0:
            app.flowerLst += [Flower(random.randrange(10, app.width), 
                              app.height, int(random.randrange(0, 2)), 
                              int(random.randrange(0, 2)))]
            
        # adds flowers that are off screen into a list
        for flower in app.flowerLst:
            if flower.positionY < -30:
                app.toRemoveFlower.add(flower.ID)
            elif (flower.positionX > (app.width + 30) or 
                    flower.positionX < -30):
                app.toRemoveFlower.add(flower.ID)
        
        # removes flowers that are off screen from the toRemoveFlower list
        removeFlower(app)

        # removes old pollen from player bee
        removeOldPollen(app, app.player)

        # removes old pollen from first helper bee
        removeOldPollen(app, app.helperBee1)

        # removes old pollen from second helper bee
        removeOldPollen(app, app.helperBee2)

        # helps the first helper bee choose a target
        app.helperBee1.findTarget(app)

        # helps the second helper bee choose a target
        app.helperBee2.findTarget(app)

        # checks for bad pollen
        badPollen(app, app.player)
        badPollen(app, app.helperBee1)
        badPollen(app, app.helperBee2)

# there was some inspiration from Professor Taylor on how to implement the
# ID part as I was confused on how to call the ID
def removeFlower(app):
    i = 0
    while i < len(app.flowerLst):
        if app.flowerLst[i].ID in app.toRemoveFlower:
            app.flowerLst.pop(i)
        else:
            i += 1

def removePollen(app, bee):
    for flower in bee.toRemovePollen:
        if flower in bee.pollen:
            bee.pollen.remove(flower)

def drawPollenAtFeet(app, bee):
    x = bee.x - 20
    y = bee.y + 50
    
    i = 0
    for pollen in bee.pollen:
        drawCircle(x + i*10, y, 10, fill = pollen.color)
        i = (i + 1) % len(bee.pollen)


def drawInstructions(app):
    if app.welcomeScreen:
        if app.instruction == False:
            drawLabel('Welcome to', app.width//2, 200, size=90, bold = True, 
                    fill = "white", font = "orbitron")
            drawLabel('Game Bee', app.width//2, 320, size=140, bold = True, 
                    fill = "white", font = "orbitron")
            drawRect(360, 440, 270, 80, fill = None, border = "white",
                    borderWidth = 3)
            drawLabel('Click start', 495, 480, size=40, bold = True, fill 
                    = "white", font = "orbitron")
            drawRect(360, 540, 270, 80, fill = None, border = "white",
                    borderWidth = 3)
            drawLabel('Instructions', 495, 580, size=40, bold = 
                    True, fill = "white", font = "orbitron")
            welcomeScreenGraphics(app)
        else:
            s = 25
            c = "white"
            drawLabel('Instructions', app.width//2, 60, size=50, bold = True, 
                    fill = c, font = "orbitron")
            drawLabel('Due to the decrease in natural crop pollinators in ' +
                      'Lolanland, the Queen Bee', app.width//2, 140, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('has issued you, General Bee, to help pollinate the ' +
                      'flowers near the hive. She', app.width//2, 175, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('sent two helper bees to assist you. In this game, t' +
                      'here are two types of', app.width//2, 210, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('flowers: ones that can be pollinated and ones that ' +
                      'are pollinators. Your job is', app.width//2, 245, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('to spread the pollen from the pollinator flowers to' +
                      ' the ones that need to be', app.width//2, 280, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('pollinated. The flowers that are pollinators are th' +
                      'e solid circles which will ', app.width//2, 315, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('become hollow once you gather its pollen. In the co' +
                      'rner, you can see the pollen ', app.width//2, 350, 
                      size=s, bold = True, fill = c, font = "orbitron")
            drawLabel('that is in your possession. You may only have up 6.' +
                      ' If you have gathered more ', app.width//2, 385, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('than 6, the earliest gathered pollen will disappear.' +
                      ' Your goal after you gather ', app.width//2, 420, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('the pollen is to move towards the flowers that need t' +
                      'o be pollinated which is ', app.width//2, 455, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('characterized by the ringed circles. However, only' +
                      " by matching the pollen's ", app.width//2, 490, size=s, 
                      bold = True, fill = c, font = "orbitron")
            drawLabel('color with the flower can the flower be successfully' +
                      " pollinated. Once a flower is", app.width//2, 525, 
                      size=s, bold = True, fill = c, font = "orbitron")
            drawLabel('pollinated, it will grow (gradually). You can gather ' +
                      "pollen or pollinate the flowers", app.width//2, 560, 
                      size=s, bold = True, fill = c, font = "orbitron")
            drawLabel('by moving towards the flowers. Some flowers are po' +
                      "lluted so if you gather it, you", app.width//2, 595, 
                      size=s, bold = True, fill = c, font = "orbitron")
            drawLabel('will have to throw away the pollen in your inve' +
                      "ntory.", 340, 630, size=s, bold = True, 
                      fill = c, font = "orbitron")
            
            drawRect(790, 730, 190, 60, fill = None,  border = "white")
            drawLabel('Back', 885, 760, size=35, bold = True, fill = c, 
                      font = "orbitron")
            drawLabel('Note: Press i to access the instruction screen ', 
                      400, 700, size=22, bold = True, fill = c, 
                      font = "orbitron")
            drawLabel('once the game starts and click back to go back.', 
                      400, 730, size=22, bold = True, fill = c, 
                      font = "orbitron")
            drawCircle(100, 715, 30, fill = None, border = "midnightblue", 
                   borderWidth = 10)
            instructionGraphics(app)
            
def welcomeScreenGraphics(app):
    bee = HelperBee(app, 400, app.height//2)
    bee.draw()

    colors = Flower.colors

    for i in range(len(colors)):
        drawCircle(100 + i*150, 80, 35, fill = None, border = colors[i])
        drawCircle(100 + i*150, 80, 35-10, fill = colors[i])
    
    for i in range(len(colors)-1, -1, -1):
        drawCircle(900 - i*150, 720, 35, fill = None, border = colors[i], 
                   borderWidth = 10)


def instructionGraphics(app):
    bee = HelperBee(app, 805, 690)
    bee.draw()

    colors = Flower.colors

    for i in range(4):
        drawCircle(60 + i*80, 60, 25, fill = None, border = colors[i])
        drawCircle(60 + i*80, 60, 25-10, fill = colors[i])
    
    for i in range(len(colors)-1, 1, -1):
        drawCircle(530 + i*80, 60, 25, fill = None, border = colors[i], 
                   borderWidth = 10)
        

def drawPollen(app):
    i = 0
    for pollen in app.player.pollen:
        drawCircle(40 + i*40, 50, 30, fill = None, border = pollen.color,
                   borderWidth = 10)
        i = (i + 1) % len(app.player.pollen)

def redrawAll(app):
    drawRect(0, 0, app.width, app.height, fill="lightBlue")
    if app.welcomeScreen == False and app.instruction == False:
        # draws the first helper bee
        app.helperBee1.draw()

        # draws the second helper bee
        app.helperBee2.draw()

        # draws the helper bee
        app.player.draw()    

        # draws flowers
        for flower in app.flowerLst:
            flower.draw()

        # draws pollen inventory in corner
        drawPollen(app)
        
        # draws pollen at first helper bee feet
        drawPollenAtFeet(app, app.helperBee1)

        # draws pollen at second helper bee feet
        drawPollenAtFeet(app, app.helperBee2)

        # draws pollen at player feet
        drawPollenAtFeet(app, app.player)
    
    drawInstructions(app)

    if app.welcomeScreen == False and app.instruction:
        drawInstructions(app)

runApp(width=1000, height=800)