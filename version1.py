from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3
from direct.task import Task

class ChessboardGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()  # Disable the default camera controls
        self.camera.setPos(4, -12, 15)
        self.camera.lookAt(4, 4, 0)

        # Setup the skybox
        self.setupSkybox()  # Ensure the skybox is set up during initialization

        # Create the chessboard
        self.chessboard = []
        for x in range(8):
            row = []
            for y in range(8):
                cube = self.loader.loadModel("models/box")
                cube.setScale(1, 1, 1)  # size
                cube.setPos(x, y, 0)
                cube.setColor(0, 0, 0 if (x + y) % 2 == 0 else 1)  # Black for black boxes, Blue for blue boxes
                cube.reparentTo(self.render)
                row.append(cube)
            self.chessboard.append(row)

        # Create the player sphere
        self.player = self.loader.loadModel("models/smiley")
        self.player.setScale(0.5)  # Make it smaller
        self.player.setPos(0.5, 0.5, 1.5)  # Slightly above the board
        self.player.reparentTo(self.render)

        self.player_pos = [0, 0]  # Initial position on the board
        self.player_direction = 0  # Facing "up" initially (0 degrees)
        self.color_changed = False  # Track if the color has been changed

        # Accept key inputs for movement
        self.accept("arrow_up", self.move_player, ["forward"])
        self.accept("arrow_left", self.turn_player, ["left"])
        self.accept("arrow_right", self.turn_player, ["right"])
        self.accept("space", self.jump_player)
        self.accept("enter", self.change_color)  # Accept Enter key to change color

    def move_player(self, direction):
        x, y = self.player_pos

        # Determine movement based on facing direction
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
        self.player.setPos(x + 0.5, y + 0.5, 1.5)

    def turn_player(self, direction):
        # Update direction based on turning
        if direction == "left":
            self.player_direction = (self.player_direction - 90) % 360
        elif direction == "right":
            self.player_direction = (self.player_direction + 90) % 360

        # Rotate the player visually
        self.player.setH(self.player_direction)

    def jump_player(self):
        # Make the player jump
        self.taskMgr.add(self.jump_task)

    def jump_task(self, task):
        t = task.time

        # Simple parabolic jump motion
        if t < 0.1:  # Ascend
            z = 1.5 + 2 * t
        elif t < 0.5:  # Descend
            z = 1.5 - 2 * (t - 1.5)
        else:
            self.player.setZ(1.5)  # Land back on the board
            return Task.done

        self.player.setZ(z)
        return Task.cont

    def change_color(self):
        # Change the color of the box to red or revert to original
        x, y = self.player_pos
        if not self.color_changed:
            self.chessboard[x][y].setColor(1, 0, 0)  # Set color to red
            self.color_changed = True
        else:
            self.chessboard[x][y].setColor(0, 0, 0 if (x + y) % 2 == 0 else 1)  # Revert to original color (black for black boxes, blue for blue boxes)
            self.color_changed = False

    def setupSkybox(self):
        skybox = self.loader.loadModel('skybox/skybox.egg')  # Use self.loader to load the model
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(self.render)  # Use self.render to reparent the skybox

game = ChessboardGame()
game.run()
