from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, TransparencyAttrib, TextNode
from direct.task import Task
from direct.gui.DirectGui import DirectButton, DGG
from math import pi, sin, cos

from panda3d.core import (
    loadPrcFile,
    DirectionalLight,
    AmbientLight,
    TransparencyAttrib,
    WindowProperties,
    CollisionTraverser,
    CollisionNode,
    CollisionBox,
    CollisionRay,
    CollisionHandlerQueue,
)
from direct.gui.OnscreenImage import OnscreenImage


class ChessboardGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()
        self.camera.setPos(-18, -12, 15)
        self.camera.lookAt(0, 3, 0)

        # Setup the skybox
        self.setupSkybox()

        # Initialize terrain heights matrix
        self.terrain_heights = [[1 for y in range(8)] for x in range(8)]
        self.terrain_heights[2][3] = 2
        self.terrain_heights[2][4] = 3
        self.terrain_heights[5][5] = 2

        # Create the chessboard with varying heights
        self.chessboard = []
        for x in range(8):
            row = []
            for y in range(8):
                height = self.terrain_heights[x][y]
                cube = self.loader.loadModel("models/box")
                cube.setScale(1, 1, height)
                cube.setPos(x - 8, y, height / 2)
                cube.setColor(0, 0, 0 if (x + y) % 2 == 0 else 1)
                cube.reparentTo(self.render)
                row.append(cube)
            self.chessboard.append(row)

        # Create the player sphere
        self.player = self.loader.loadModel("models/smiley")
        self.player.setScale(0.5)
        self.player_pos = [0, 0]
        self.player_z = 1.5
        self.updatePlayerPosition()
        self.player.reparentTo(self.render)

        self.player_direction = 0
        self.color_changed = False
        self.is_jumping = False
        self.jump_target = None

        # Create screen controls
        self.createScreenControls()

        # Keyboard controls
        self.accept("arrow_up", self.move_player, ["forward"])
        self.accept("arrow_left", self.turn_player, ["left"])
        self.accept("arrow_right", self.turn_player, ["right"])
        self.accept("space", self.jump_player)
        self.accept("enter", self.change_color)

    def updatePlayerPosition(self):
        x, y = self.player_pos
        self.player.setPos(x - 7.5, y + 0.5, self.player_z + 0.5)

    def getNextPosition(self):
        x, y = self.player_pos
        next_x, next_y = x, y

        if self.player_direction == 180 and y < 7:  # Facing up
            next_y = y + 1
        elif self.player_direction == 90 and x < 7:  # Facing right
            next_x = x + 1
        elif self.player_direction == 0 and y > 0:  # Facing down
            next_y = y - 1
        elif self.player_direction == 270 and x > 0:  # Facing left
            next_x = x - 1

        return next_x, next_y

    def move_player(self, direction):
        if self.is_jumping:
            return

        if direction == "forward":
            next_x, next_y = self.getNextPosition()

            # If out of bounds
            if not (0 <= next_x < 8 and 0 <= next_y < 8):
                return

            next_height = self.terrain_heights[next_x][next_y]
            height_diff = next_height - self.player_z

            # Prevent movement for large height differences
            if abs(height_diff) > 1:
                return

            self.player_pos = [next_x, next_y]
            self.player_z = max(next_height, self.player_z)
            self.updatePlayerPosition()

    def turn_player(self, direction):
        if self.is_jumping:
            return

        if direction == "left":
            self.player_direction = (self.player_direction - 90) % 360
        elif direction == "right":
            self.player_direction = (self.player_direction + 90) % 360

        self.player.setH(self.player_direction)

    def jump_player(self):
        if self.is_jumping:
            return

        next_x, next_y = self.getNextPosition()

        # If out of bounds
        if not (0 <= next_x < 8 and 0 <= next_y < 8):
            return

        next_height = self.terrain_heights[next_x][next_y]
        height_diff = next_height - self.player_z

        # Jump only if height difference is exactly 0.5
        if height_diff == 0.5:
            self.jump_target = (next_x, next_y, next_height)
            self.is_jumping = True
            self.taskMgr.add(self.jump_task, 'jumpTask')

    def jump_task(self, task):
        t = task.time
        start_z = self.player_z
        target_x, target_y, target_z = self.jump_target

        if t < 0.2:  # Jump up phase
            self.player.setZ(start_z + 2 * sin(pi * t / 0.25))
        elif t < 0.4:  # Landing phase
            self.player.setZ(target_z + 0.5)
            self.player_pos = [target_x, target_y]
            self.player_z = target_z
            self.is_jumping = False
            self.jump_target = None
            return Task.done

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
        skybox = self.loader.loadModel('skybox/skybox.egg')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(self.render)

    def createScreenControls(self):
        button_base_x = 0.8

        self.forwardButton = DirectButton(
            text="Forward",
            pos=(button_base_x, 0, 0.2),
            scale=0.1,
            command=self.move_player,
            extraArgs=["forward"],
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )

        self.turnLeftButton = DirectButton(
            text="Turn Left",
            pos=(button_base_x, 0, 0),
            scale=0.1,
            command=self.turn_player,
            extraArgs=["left"],
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )

        self.turnRightButton = DirectButton(
            text="Turn Right",
            pos=(button_base_x, 0, -0.2),
            scale=0.1,
            command=self.turn_player,
            extraArgs=["right"],
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )

        self.jumpButton = DirectButton(
            text="Jump",
            pos=(button_base_x, 0, -0.4),
            scale=0.1,
            command=self.jump_player,
            borderWidth=(0.005, 0.005),
            rolloverSound=None,
            clickSound=None,
            frameColor=(0.8, 0.8, 0.8, 0.7),
            text_fg=(0, 0, 0, 1),
        )


game = ChessboardGame()
game.run()
