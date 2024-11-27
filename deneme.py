from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3, WindowProperties, CardMaker
from direct.task import Task
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.interval.LerpInterval import LerpHprInterval
from direct.interval.IntervalGlobal import Sequence, Func
from direct.task.TaskManagerGlobal import taskMgr  # Ensure taskMgr is available

class ChessboardGame(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        wp = WindowProperties()
        wp.setSize(1600, 900)
        self.win.requestProperties(wp)

        self.setup_scene_layout()
        self.create_chessboard()
        self.create_player()

        self.movement_queue = []
        self.is_executing_movements = False

        self.createInstructionPlaceholder()
        self.createControlButtons()

        self.accept("enter", self.start_movement)
        self.accept("c", self.change_color)

    def setup_scene_layout(self):
        self.disableMouse()
        self.camera.setPos(8, -15, 15)
        self.camera.lookAt(8, 8, 0)

        cm = CardMaker('background')
        cm.setFrame(-20, 20, -20, 20)
        background = self.render.attachNewNode(cm.generate())
        background.setPos(8, 8, -1)
        background.setColor(0.7, 0.7, 0.7, 1)

    def create_chessboard(self):
        self.chessboard = []
        for x in range(8):
            row = []
            for y in range(8):
                cube = self.loader.loadModel("models/box")
                cube.setScale(1, 1, 1)
                cube.setPos(x, y, 0)
                cube.setColor(0, 0, 0 if (x + y) % 2 == 0 else 1)
                cube.reparentTo(self.render)
                row.append(cube)
            self.chessboard.append(row)

    def create_player(self):
        self.player = self.loader.loadModel("models/smiley")
        self.player.setScale(0.5)
        self.player.setPos(0.5, 0.5, 1.5)
        self.player.reparentTo(self.render)

        self.player_pos = [0, 0]
        self.player_direction = 0
        self.color_changed = False

    def createInstructionPlaceholder(self):
        aspect2d = self.aspect2d
        self.instructionFrame = DirectFrame(
            frameColor=(0.8, 0.8, 0.8, 0.8),
            frameSize=(-1, 1, -0.5, 0.5),
            pos=(0.8, 0, -0.5),
            parent=aspect2d
        )
        self.instruction_labels = []
        for i in range(8):
            label = DirectLabel(
                text="",
                text_scale=0.05,
                frameColor=(0, 0, 0, 0),
                pos=(-0.8, 0, 0.3 - i * 0.075),
                parent=self.instructionFrame
            )
            self.instruction_labels.append(label)

    def createControlButtons(self):
        button_scale = 0.1
        self.forwardButton = DirectButton(
            text="↑",
            pos=(0.9, 0, 0.2),
            scale=button_scale,
            command=self.add_movement,
            extraArgs=["forward"],
            parent=self.aspect2d
        )
        self.turnLeftButton = DirectButton(
            text="←",
            pos=(0.8, 0, 0.1),
            scale=button_scale,
            command=self.add_movement,
            extraArgs=["left"],
            parent=self.aspect2d
        )
        self.turnRightButton = DirectButton(
            text="→",
            pos=(1.0, 0, 0.1),
            scale=button_scale,
            command=self.add_movement,
            extraArgs=["right"],
            parent=self.aspect2d
        )
        self.jumpButton = DirectButton(
            text="⇡",
            pos=(0.9, 0, 0),
            scale=button_scale,
            command=self.add_movement,
            extraArgs=["jump"],
            parent=self.aspect2d
        )
        self.colorButton = DirectButton(
            text="C",
            pos=(0.9, 0, -0.1),
            scale=button_scale,
            command=self.add_movement,
            extraArgs=["color"],
            parent=self.aspect2d
        )
# Color Change Button
        self.colorButton = DirectButton(
            text="C",  # Color change button
            pos=(0.9, 0, -0.1),
            scale=button_scale,
            command=self.add_movement,
            extraArgs=["color"],
            borderWidth=(0.005, 0.005),
            parent=aspect2d
        )
        
    def add_movement(self, movement):
        # Check if we have space in the instruction queue
        if len(self.movement_queue) < 8:
            # Add movement to the queue and update the instruction label
            self.movement_queue.append(movement)
            self.update_instruction_labels()

    def update_instruction_labels(self):
        # Update the instruction labels with current queue
        for i, label in enumerate(self.instruction_labels):
            if i < len(self.movement_queue):
                movement = self.movement_queue[i]
                # Map movement to a more descriptive text
                movement_text = {
                    "forward": "↑ Forward",
                    "left": "← Turn Left",
                    "right": "→ Turn Right", 
                    "jump": "⇡ Jump",
                    "color": "C Color Change"
                }.get(movement, movement)
                label['text'] = movement_text
            else:
                label['text'] = ""

    def start_movement(self):
        # If not already executing and queue is not empty
        if not self.is_executing_movements and self.movement_queue:
            self.is_executing_movements = True
            self.execute_next_movement()

    def execute_next_movement(self):
        # If queue is empty, stop execution
        if not self.movement_queue:
            self.is_executing_movements = False
            return Task.done

        # Get the next movement
        movement = self.movement_queue.pop(0)
        self.update_instruction_labels()

        # Execute the movement based on type
        if movement == "forward":
            self.move_player("forward")
        elif movement == "left":
            self.turn_player("left")
        elif movement == "right":
            self.turn_player("right")
        elif movement == "jump":
            self.jump_player()
        elif movement == "color":
            self.change_color()

        # Schedule next movement using a task instead of doMethodLater
        return taskMgr.doMethodLater(0.5, self.execute_next_movement, "next_movement")

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

        # Rotate the player visually with a smooth rotation
        rotate_interval = LerpHprInterval(
            self.player, 
            0.3,  # Duration of rotation
            Vec3(self.player_direction, 0, 0)
        )
        rotate_interval.start()

    def jump_player(self):
        # Make the player jump
        taskMgr.add(self.jump_task)

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
            self.chessboard[x][y].setColor(0, 0, 0 if (x + y) % 2 == 0 else 1)  # Revert to original color
            self.color_changed = False

game = ChessboardGame()
game.run()