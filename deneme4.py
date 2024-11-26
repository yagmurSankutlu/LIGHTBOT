from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, TransparencyAttrib, TextNode
from direct.task import Task
from direct.gui.DirectGui import (
    DirectButton, 
    DGG  # DirectGUI Globals for style configuration
)
from math import pi, sin, cos

from panda3d.core import loadPrcFile
from panda3d.core import DirectionalLight, AmbientLight
from panda3d.core import TransparencyAttrib
from panda3d.core import WindowProperties
from panda3d.core import CollisionTraverser, CollisionNode, CollisionBox, CollisionRay, CollisionHandlerQueue
from direct.gui.OnscreenImage import OnscreenImage

class ChessboardGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()  # Disable the default camera controls
        # Adjust camera to view the board from an angle that leaves space for controls
        self.camera.setPos(-18, -12, 15)  # Moved further left
        self.camera.lookAt(0, 3, 0)  # Look at the left side of the playing area

        # Setup the skybox
        self.setupSkybox()  # Ensure the skybox is set up during initialization

        # Create the chessboard further to the left
        self.chessboard = []
        for x in range(8):
            row = []
            for y in range(8):
                cube = self.loader.loadModel("models/box")
                cube.setScale(1, 1, 1)
                cube.setPos(x - 8, y, 0)  # Shifted left by 8 units
                cube.setColor(0, 0, 0 if (x + y) % 2 == 0 else 1)
                cube.reparentTo(self.render)
                row.append(cube)
            self.chessboard.append(row)

        # Create the player sphere
        self.player = self.loader.loadModel("models/smiley")
        self.player.setScale(0.5)
        self.player.setPos(-7.5, 0.5, 1.5)  # Adjusted for new board position
        self.player.reparentTo(self.render)

        self.player_pos = [0, 0]
        self.player_direction = 0
        self.color_changed = False

        # Create side-by-side screen controls
        self.createScreenControls()

        # Keyboard controls
        self.accept("arrow_up", self.move_player, ["forward"])
        self.accept("arrow_left", self.turn_player, ["left"])
        self.accept("arrow_right", self.turn_player, ["right"])
        self.accept("space", self.jump_player)
        self.accept("enter", self.change_color)

    def createScreenControls(self):
        # Create a control panel on the right side
        # Buttons are now vertically arranged on the right side
        button_base_x = 0.8  # Moved base x position for all buttons to the right
        
        # Forward Button
        self.forwardButton = DirectButton(
            text="Forward",
            pos=(button_base_x, 0, 0.2),  # Raised position
            scale=0.1,
            command=self.move_player,
            extraArgs=["forward"],
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )

        # Turn Left Button
        self.turnLeftButton = DirectButton(
            text="Turn Left",
            pos=(button_base_x, 0, 0),  # Middle position
            scale=0.1,
            command=self.turn_player,
            extraArgs=["left"],
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )

        # Turn Right Button
        self.turnRightButton = DirectButton(
            text="Turn Right",
            pos=(button_base_x, 0, -0.2),  # Lower position
            scale=0.1,
            command=self.turn_player,
            extraArgs=["right"],
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )

        # Jump Button
        self.jumpButton = DirectButton(
            text="Jump",
            pos=(button_base_x, 0, -0.4),  # Lowest position
            scale=0.1,
            command=self.jump_player,
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )

    def move_player(self, direction):
        x, y = self.player_pos

        if direction == "forward":
            if self.player_direction == 180 and y < 7:  # Facing up
                y += 1
            elif self.player_direction == 90 and x < 7:  # Facing right
                x += 1
            elif self.player_direction == 0 and y > 0:  # Facing down
                y -= 1
            elif self.player_direction == 270 and x > 0:  # Facing left
                x -= 1

        self.player_pos = [x, y]
        # Adjust the position calculation for the shifted board
        self.player.setPos(x - 7.5, y + 0.5, 1.5)

    def turn_player(self, direction):
        if direction == "left":
            self.player_direction = (self.player_direction - 90) % 360
        elif direction == "right":
            self.player_direction = (self.player_direction + 90) % 360

        self.player.setH(self.player_direction)

    def jump_player(self):
        self.taskMgr.add(self.jump_task)

    def jump_task(self, task):
        t = task.time

        if t < 0.1:
            z = 1.5 + 2 * t
        elif t < 0.5:
            z = 1.5 - 2 * (t - 1.5)
        else:
            self.player.setZ(1.5)
            return Task.done

        self.player.setZ(z)
        return Task.cont

    def change_color(self):
        x, y = self.player_pos
        if not self.color_changed:
            self.chessboard[x][y].setColor(1, 0, 0)
            self.color_changed = True
        else:
            self.chessboard[x][y].setColor(0, 0, 0 if (x + y) % 2 == 0 else 1)
            self.color_changed = False

    def setupSkybox(self):
        skybox = self.loader.loadModel('skybox/skybox.egg')  # Use self.loader to load the model
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(self.render) 


game = ChessboardGame()
game.run()