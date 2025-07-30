import tkinter as tk
import math
from PIL import Image, ImageTk # pip install pillow
from networktables import NetworkTables
import time

# Team 3354:
robot_ip = "10.33.54.2"

NetworkTables.initialize(server=robot_ip)

if not NetworkTables.isConnected():
    print("Esperando conexión con el robot...")
    time.sleep(2)

table = NetworkTables.getTable("ReefAppData")

# state = table.getNumber("State", 0.0)
# Send a value to the robot
# table.putString("Side", side)

class CircularButton:
    def __init__(self, canvas, x, y, r, side, level, number, normal_color="gray", hover_color="darkgray", active_color="blue"):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.r = r
        self.side = side
        self.level = level
        self.number = number
        self.normal_color = normal_color
        self.hover_color = hover_color
        self.active_color = active_color
        self.current_color = normal_color
        self.selected = False

        self.oval = canvas.create_oval(x - r, y - r, x + r, y + r, fill=self.normal_color, outline="")

        # Bind events
        canvas.tag_bind(self.oval, "<Enter>", self.on_enter)
        canvas.tag_bind(self.oval, "<Leave>", self.on_leave)
        canvas.tag_bind(self.oval, "<Button-1>", self.on_left_click)
        canvas.tag_bind(self.oval, "<Button-3>", self.on_right_click)

    def on_enter(self, event):
        if not self.selected:
            self.canvas.itemconfig(self.oval, fill=self.hover_color)

    def on_leave(self, event):
        if not self.selected:
            self.canvas.itemconfig(self.oval, fill=self.normal_color)

    def on_left_click(self, event):
        self.selected = True
        self.canvas.itemconfig(self.oval, fill=self.active_color)

        # Print data
        print(self.number)
        print(self.level)
        print(self.side)

        # Send Data
        table.putString("ApriltagId", self.number)
        table.putString("Level", self.level)
        table.putString("Side", self.side)

    def on_right_click(self, event):
        self.selected = False
        self.canvas.itemconfig(self.oval, fill=self.normal_color)

class HexagonApp:
    def __init__(self, root):
        self.root = root
        root.title("Hexagon Buttons")

        canvas_width = 600
        canvas_height = 600
        root.geometry("600x600")

        self.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height, bg="#3e3e3e")
        self.canvas.pack(fill="both", expand=True)

        # Reef image

        # Cargar imagen desde archivo
        img = Image.open("C:/Users/Santy/Desktop/ReefApp/Reef_img.png")  # Asegúrate que la ruta sea correcta

        # Redimensionar imagen
        img_width = int(canvas_width * 7/12)
        img_height = int(canvas_height * 7/12)
        img = img.resize((img_width, img_height), Image.LANCZOS)

        self.bg_img = ImageTk.PhotoImage(img)

        # Center the image
        x = (canvas_width - img.width) // 2
        y = (canvas_height - img.height) // 2

        self.canvas.create_image(x, y, image=self.bg_img, anchor="nw")

        # Center and size of the hexagon
        cx = canvas_width / 2
        cy = canvas_height / 2
        r = min(canvas_width, canvas_height) * 0.2  # 35% del lado menor

        # Calculate the hexagon vertex
        self.hex_points = []
        for i in range(6):
            angle_deg = 60 * i
            angle_rad = angle_deg * 3.14159 / 180
            x = cx + r * math.cos(angle_rad)
            y = cy + r * math.sin(angle_rad)
            self.hex_points.append((x, y))

        # Draw the hexagon
        points_flat = [coord for point in self.hex_points for coord in point]
        self.canvas.create_polygon(points_flat, outline="black", fill="", width=2)

        # Create the buttons
        self.buttons = []
        for i in range(6):
            sideIndex = i + 1

            p1 = self.hex_points[i]
            p2 = self.hex_points[(i + 1) % 6]

            vx = p2[0] - p1[0]
            vy = p2[1] - p1[1]

            px_left = -vy
            py_left = vx
            
            px_right = vy
            py_right = -vx

            def norm(x, y):
                mag = (x**2 + y**2)**0.5
                return (x/mag, y/mag)

            px_left, py_left = norm(px_left, py_left)
            px_right, py_right = norm(px_right, py_right)

            fractions = [0.25, 0.75]

            sideCount = 0

            for fi, f in enumerate(fractions):
                # Original sizes
                #start_offset = -100

                #offset_dist_row_2 = 60

                # Adjusted sizes

                start_offset = -canvas_width / 6
                offset_dist_row_2 = canvas_width / 10

                offset_dist_row_3 = 0

                px_up, py_up = norm(-vy, vx)

                p1_up_x = p1[0] + px_up * start_offset
                p1_up_y = p1[1] + py_up * start_offset

                base_x = p1_up_x + vx * f
                base_y = p1_up_y + vy * f

                x1 = base_x + px_left * offset_dist_row_2
                y1 = base_y + py_left * offset_dist_row_2

                x2 = base_x + px_right * offset_dist_row_2
                y2 = base_y + py_right * offset_dist_row_2

                x3 = base_x + px_left * offset_dist_row_3
                y3 = base_y + py_left * offset_dist_row_3

                sideCount += 1

                if(sideCount == 1):
                    side = "right"
                else:
                    side = "left"

                l2Btn = self.create_circle_button(x1, y1, side, "L2", str(sideIndex), r * 0.2)
                l3Btn = self.create_circle_button(x3, y3, side, "L3", str(sideIndex), r * 0.2)
                l4Btn = self.create_circle_button(x2, y2, side, "L4", str(sideIndex), r * 0.2)

                self.buttons.append(l2Btn)
                self.buttons.append(l3Btn)
                self.buttons.append(l4Btn)

        # Side Numbers
        for i in range(6):
            sideIndex = i + 1

            p1 = self.hex_points[i]
            p2 = self.hex_points[(i + 1) % 6]

            mx = (p1[0] + p2[0]) / 2
            my = (p1[1] + p2[1]) / 2

            vx = p2[0] - p1[0]
            vy = p2[1] - p1[1]

            def norm(x, y):
                mag = (x**2 + y**2)**0.5
                return (x/mag, y/mag)

            px, py = norm(-vy, vx)
            offset = 20

            tx = mx + px * offset
            ty = my + py * offset

            self.canvas.create_text(tx, ty, text=str(sideIndex), font=("Arial", 14), fill="black")
            

    def create_circle_button(self, x, y, side, level, number, diameter=30):
        btn = CircularButton(self.canvas, x, y, diameter, side, level, number)

        return btn


if __name__ == "__main__":
    root = tk.Tk()
    app = HexagonApp(root)
    root.mainloop()