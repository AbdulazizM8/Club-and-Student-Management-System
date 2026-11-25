import math
import tkinter as tk
import turtle

try:
    from matplotlib.figure import Figure
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

BADGE_COLORS = ["#ff6b6b", "#feca57", "#48dbfb", "#1dd1a1", "#a29bfe", "#ff9ff3"]


class EnrollmentChart:
    def __init__(self, parent_frame):
        self.figure = Figure(figsize=(6, 3.2), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=parent_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update(self, data_manager):
        self.ax.clear()
        clubs = list(data_manager.clubs.values())
        names = [club.name for club in clubs]
        members = [len(club) for club in clubs]
        capacity = [club.max_capacity for club in clubs]

        self.ax.barh(names, capacity, color="#e3e8f0", height=0.6, label="Capacity")
        self.ax.barh(names, members, color="#3b7ddd", height=0.6, label="Members")

        for i in range(len(clubs)):
            label = str(members[i]) + " / " + str(capacity[i])
            if clubs[i].schedule != "":
                label += "  |  " + clubs[i].schedule
            self.ax.text(capacity[i] + 0.5, i, label, va="center", fontsize=9, color="#333333")

        if len(clubs) > 0:
            self.ax.set_xlim(0, max(capacity) * 1.45)
            self.ax.set_xticks(range(0, max(capacity) + 1, 5))
        self.ax.invert_yaxis()
        self.ax.set_xlabel("Students")
        self.ax.set_title("Club Enrollment and Meeting Times", loc="left", fontsize=13, fontweight="bold")
        self.ax.grid(axis="x", color="#dddddd", linestyle="--")
        self.ax.set_axisbelow(True)
        self.ax.spines["top"].set_visible(False)
        self.ax.spines["right"].set_visible(False)
        self.ax.legend(loc="lower right", bbox_to_anchor=(1, 1), ncol=2, frameon=False)
        self.figure.tight_layout()
        self.canvas.draw_idle()


class ClubBadge:
    def __init__(self, parent_frame, size=220):
        self.size = size
        self.canvas = tk.Canvas(parent_frame, width=size, height=size, highlightthickness=0)
        self.canvas.pack()
        self.screen = turtle.TurtleScreen(self.canvas)
        self.draw(None)

    def draw(self, club):
        r = self.size / 2 - 8
        self.screen.clear()
        self.screen.tracer(0)
        self.screen.bgcolor("#101a33")

        pen = turtle.RawTurtle(self.screen)
        pen.hideturtle()
        pen.speed(0)

        pen.penup()
        pen.goto(-r, -r)
        pen.pendown()
        pen.color("#feca57")
        pen.pensize(3)
        for i in range(4):
            pen.forward(2 * r)
            pen.left(90)

        pen.penup()
        pen.goto(0, -r * 0.8)
        pen.setheading(0)
        pen.pendown()
        pen.color("#48dbfb", "#1b2a52")
        pen.begin_fill()
        pen.circle(r * 0.8)
        pen.end_fill()

        if club is None:
            pen.penup()
            pen.goto(0, -8)
            pen.color("white")
            pen.write("Select a club", align="center", font=("Arial", 12, "bold"))
        else:
            seed = 0
            for letter in club.name:
                seed += ord(letter)
            sides = 3 + len(club) % 6
            side_length = 0.7 * r * math.sin(math.pi / sides)

            pen.penup()
            pen.goto(0, 0)
            pen.setheading(0)
            pen.pendown()
            pen.pensize(2)
            for i in range(12):
                pen.color(BADGE_COLORS[(seed + i) % len(BADGE_COLORS)])
                for j in range(sides):
                    pen.forward(side_length)
                    pen.right(360 / sides)
                pen.right(30)

            pen.penup()
            pen.goto(0, -r + 4)
            pen.color("white")
            pen.write(club.name, align="center", font=("Arial", 10, "bold"))

        self.screen.update()


def draw_school_logo(parent_frame):
    canvas = tk.Canvas(parent_frame, width=200, height=200, bg="#9fd3f5", highlightthickness=0)
    canvas.pack()

    canvas.create_oval(150, 15, 185, 50, fill="#ffd93b", outline="")
    canvas.create_oval(15, 25, 60, 45, fill="white", outline="")
    canvas.create_oval(40, 18, 85, 40, fill="white", outline="")

    canvas.create_rectangle(0, 150, 200, 200, fill="#5cb85c", outline="")
    canvas.create_rectangle(14, 115, 24, 155, fill="#6b4226", outline="")
    canvas.create_oval(0, 85, 38, 125, fill="#2e8b57", outline="")

    canvas.create_rectangle(50, 85, 170, 150, fill="#d9825b", outline="")
    canvas.create_polygon(40, 85, 110, 40, 180, 85, fill="#8b3a2f", outline="")

    canvas.create_oval(98, 55, 122, 79, fill="white", outline="#333333")
    canvas.create_line(110, 67, 110, 59, fill="#333333", width=2)
    canvas.create_line(110, 67, 116, 67, fill="#333333", width=2)

    canvas.create_line(110, 40, 110, 18, fill="#555555", width=2)
    canvas.create_rectangle(110, 18, 128, 28, fill="#e74c3c", outline="")

    canvas.create_rectangle(98, 115, 122, 150, fill="#6b4226", outline="")
    canvas.create_oval(115, 131, 119, 135, fill="#ffd93b", outline="")

    for x in (60, 136):
        canvas.create_rectangle(x, 98, x + 24, 125, fill="#cfe9ff", outline="white")
        canvas.create_line(x + 12, 98, x + 12, 125, fill="white")
        canvas.create_line(x, 111, x + 24, 111, fill="white")

    canvas.create_rectangle(80, 150, 140, 157, fill="#bdbdbd", outline="")
    canvas.create_rectangle(90, 157, 130, 168, fill="#d8c3a5", outline="")

    canvas.create_text(100, 185, text="SCHOOL CLUBS", fill="white", font=("Arial", 10, "bold"))
    return canvas
