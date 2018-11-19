#Louis Ye
#Block 5
from graphics3d import *

makeGraphicsWindow(1024, 600)
mapAdventure = open("map.txt", "r")
loadTexture("scary-wall.jpg")
#http://smg.photobucket.com/user/totorojonathan/media/brick01_zps778348bb.jpg.html
loadTexture("XxhFVCZ.jpg")
#http://i.imgur.com/XxhFVCZ.jpg
loadTexture("character_217_demonuvwmap.jpg")
#https://kevinwtaylor.files.wordpress.com/2011/09/character_217_demonuvwmap.jpg
scare = loadImage("scare.png")
#https://i.ytimg.com/vi/b8qolupfhkQ/maxresdefault.jpg
breath = loadSound("breathing.wav")
#https://www.youtube.com/watch?v=jSyIGm7dNb4
fun = loadSound("scare.wav", 1.0)
#https://www.youtube.com/watch?v=Uufq_PFXbpA
player = loadImage("triangle.png")
#http://etc.usf.edu/clipart/36900/36972/isoc_tri_040_36972_lg.gif

class Place:
    def __init__ (self, x, z):
        self.x = x
        self.z = z
    
    def distance (self, newpoint):
        newdeltax = self.x - newpoint.x
        newdeltaz = self.z - newpoint.z
        distance = (newdeltax**2 + newdeltaz**2)**0.5
        return distance    
        
    def move (self, avgVector):
        self.x += avgVector.vecX
        self.z += avgVector.vecZ
    
    def makeVectorTo (self, otherpoint):
        otherdeltax = otherpoint.x - self.x
        otherdeltaz = otherpoint.z - self.z
        return Vector(otherdeltax, otherdeltaz)
    
    def add (self, newpoint):
        self.x += newpoint.x
        self.z += newpoint.z
        
    def multiply (self, factor):
        self.x *= factor
        self.z *= factor
        
class Vector:
    def __init__ (self, vectorX, vectorZ):
        self.vecX = vectorX
        self.vecZ = vectorZ
        
    def add (self, vector2):
        self.vecX += vector2.vecX
        self.vecZ += vector2.vecZ
        
    def multiply (self, factor):
        self.vecX *= factor
        self.vecZ *= factor
        
    def length (self):
        magnitude = float((self.vecX**2 + self.vecZ**2)**0.5)
        return magnitude
    
    def normalize (self):
        magnitude = self.length()
        if magnitude != 0:
            self.vecX /= magnitude
            self.vecZ /= magnitude
        
class Monster:
    def __init__ (self, x, z):
        self.velocity = Vector(0.4, 0.4)
        self.location = Place(x, z)
        self.model = ObjModel3D("Models/marionette.obj", stats=True)
        
    def update(self, characterx, characterz, world):
        character = Place(characterx, characterz)
        characterVector = self.location.makeVectorTo(character)
        characterVector.multiply(0.15)
        self.velocity.add(characterVector)
        speed = 0.15
        volume = 1.0 - (self.location.distance(character) / 60.0)
        breath.set_volume(volume)                    
        if self.location.distance(character) > 50:
            speed = 1
        if self.velocity.length() > speed:
            self.velocity.normalize()
            self.velocity.multiply(speed)
        self.location.move(self.velocity)
        # theta around the y is the arc tangent of y/x
        newCharacterVector = self.location.makeVectorTo(character)
        self.angle = cartesianToPolarAngle(newCharacterVector.vecX, newCharacterVector.vecZ)
        world.monsterx = self.location.x 
        world.monsterz = self.location.z
       
    
    def draw(self):
        draw3D(self.model, self.location.x, -1, self.location.z, angley = self.angle - 195, scale = 0.035)        
        
        
def startWorld(world):
    world.run = True
    world.stamina = 0
    world.screen = Canvas2D(1200, 600, 1.0)
    world.minimap = Canvas2D(140, 140, 1.0)
    world.kill = False
    world.wall = Box3D(1, 5, 1, texture = "scary-wall.jpg")
    world.floor = Rect3D(500, 500, texture="character_217_demonuvwmap.jpg", textureRepeat = 70)
    world.sky = Hemisphere3D(500, 24, texture="XxhFVCZ.jpg")
    counterz = 0
    world.goal = Sphere3D(1, colors=["gray", "black"])
    world.wallList = []
    world.win = False
    world.wallRadar = []
    
    setWindowTitle("The Maze")
    for mapLine in mapAdventure:
        counterz += 1
        counterx = 0
        for character in mapLine:
            counterx += 1
            if character =='X':
                world.wallList.append((counterx, counterz))
            if character == 'S':
                setCameraPosition(counterx, 1, counterz)
            if character == 'M':
                world.monster = Monster(counterx, counterz)
            if character == 'W':
                world.winx = counterx
                world.winz = counterz


def updateWorld(world):
    (mouseX, mouseY) = getMousePosition()    
    (cameraHeading, cameraPitch, cameraRoll) = getCameraRotation()
    moveMouse(getWindowWidth()/2, getWindowHeight()/2)
    (oldx, oldy, oldz) = getCameraPosition()
    hideMouse()
    speed = 0.2    

    if isKeyPressed("left shift") and world.run == True:
        speed = 0.3
        world.stamina += 1
    if world.stamina >= 70:
        world.run = False
        world.stamina -= 1
    if isKeyPressed("left shift") == False:
        world.stamina -= 1
    if world.stamina < 60:
        world.run = True
    if world.stamina < 0:
        world.stamina += 1
        
    if isKeyPressed('w'):
        moveCameraForward(speed, flat=True)
    if isKeyPressed('s'):
        moveCameraBackward(0.2, flat=True)
    if isKeyPressed('a'):
        strafeCameraLeft(0.2, flat=True)
    if isKeyPressed('d'):
        strafeCameraRight(0.2, flat=True)
        
    if (getWindowHeight()/2 - mouseY)/5 + cameraPitch > 90:
        setCameraRotation(cameraHeading, 90, cameraRoll)
    elif (getWindowHeight()/2 - mouseY)/5 + cameraPitch < -90:
        setCameraRotation(cameraHeading, -90, cameraRoll)
    else:
        adjustCameraRotation(0, (getWindowHeight()/2 - mouseY)/5, 0)
    adjustCameraRotation((getWindowWidth()/2 - mouseX)/5, 0, 0)
        
    (newx, newy, newz) = getCameraPosition()
    
    def inWall(x, y, z):
        for wall in world.wallList:
            (xcoord, zcoord) = wall
            upperBoundx = xcoord - 0.7
            lowerBoundx = xcoord + 0.7
            upperBoundz = zcoord - 0.7
            lowerBoundz = zcoord + 0.7
            if x > upperBoundx and x < lowerBoundx and z > upperBoundz and z < lowerBoundz:
                return True
        return False
    
    if inWall(newx, oldy, newz) == True:
        if inWall(oldx, oldy, newz) == True:
            if inWall(newx, oldy, oldz) == True:
                setCameraPosition(oldx, oldy, oldz)
            else:
                setCameraPosition(newx, oldy, oldz)
        else:
            setCameraPosition(oldx, oldy, newz)
    (finalx, finaly, finalz) = getCameraPosition()
            
    world.monster.update(finalx, finalz, world)
    
    def kill(x, z, otherx, otherz):
        upperBoundx = otherx - 1
        lowerBoundx = otherx + 1
        upperBoundz = otherz - 1
        lowerBoundz = otherz + 1
        if x > upperBoundx and x < lowerBoundx and z > upperBoundz and z < lowerBoundz:
            return True
        return False
    
    def radar(x, z, otherx, otherz):
        upperBoundx = otherx - 10
        lowerBoundx = otherx + 10
        upperBoundz = otherz - 10
        lowerBoundz = otherz + 10
        if x > upperBoundx and x < lowerBoundx and z > upperBoundz and z < lowerBoundz:
            return True
        return False    
    
    if kill(finalx, finalz, world.monster.location.x, world.monster.location.z) == True:
        setCameraPosition(oldx, oldy, oldz)
        world.kill = True
    
    if kill(finalx, finalz, world.winx, world.winz) == True:
        setCameraPosition(oldx, oldy, oldz)
        world.win = True
        
    (x, y, z) = getCameraPosition()
    world.monsterx -= x
    world.monsterz -= z
    world.wallRadar = []
    for walls in world.wallList:
        (xcoord, zcoord) = walls
        if radar(x, z ,xcoord, zcoord) == True:
            world.wallRadar.append((xcoord - x, zcoord - z))
            
    
                    

# Return boolean
def inRange(camX, camZ, wallX, wallZ):
    deltax = camX - wallX
    deltaz = camZ - wallZ
    distance = (deltax**2 + deltaz**2)**0.5
    if distance < 30:
        return True
    else:
        return False

def drawWorld(world):
    playSound(breath, True)
    makeFog(0.1, (0, 0, 0), 1)
    (camX, camY, camZ) = getCameraPosition()    
    for wall in world.wallList:
        (wallX, wallZ) = wall
        if inRange(camX, camZ, wallX, wallZ) == True:       
            draw3D(world.wall, wallX, 1, wallZ)
    draw3D(world.floor, 0, -1, 0, 90)
    removeFog()
    makeFog(0.002, (0, 0, 0), 1)
    draw3D(world.sky, 0, 0, 0)    
    world.monster.draw()
    draw3D(world.goal, world.winx, 1, world.winz)
    
    clearCanvas2D(world.minimap, 'black')
    for wall in world.wallRadar:
        (wallx, wally) = wall
        minix = 70 + 7*wallx
        miniy = 70 + 7*wally
        drawRectangle2D(world.minimap, minix, miniy, 7, 7, "white")
    (cameraHeading, cameraPitch, cameraRoll) = getCameraRotation()    
    drawImage2D(world.minimap, player, 70, 70, rotate = cameraHeading, scale = 0.02)
    minimonsterx = 70 + 7*world.monsterx
    minimonsterz = 70 + 7*world.monsterz
    fillCircle2D(world.minimap, minimonsterx, minimonsterz, 4,"white")
    draw2D(world.minimap, 0, 460)
    
    if world.kill == True:
        clearCanvas2D(world.screen, 'black')
        drawImage2D(world.screen, scare, 600, 300)
        drawString2D(world.screen, "You Lose", 400, 200, size=100, color="red")
        draw2D(world.screen, 0, 0)
        stopSound(breath)
        playSound(fun, False)
        
    if world.kill == False:
        drawString2D(world.screen, "Run Away from the Monster", 400, 10, size=40, color="red")
        drawString2D(world.screen, "Shift to Run, WASD to move", 450, 35, size=20, color="red")
        draw2D(world.screen, 0, 0)
    if world.win == True:
        clearCanvas2D(world.screen, 'gray')
        drawString2D(world.screen, "You Win!", 400, 200, size=100, color="white")
    
        
runGraphics(startWorld, updateWorld, drawWorld)