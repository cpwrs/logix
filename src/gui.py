
"""
User Interface
Author: Carson Powers
"""

import tkinter as tk
from PIL import ImageTk, Image
import os

class Home:
    def __init__(self, root, window):
        self.window = window
        self.root = root

        self.frame = tk.Frame(self.window)
        self.open_button = tk.Button(self.frame, text = 'Open Editor', height = 1, width = 25, command = self.open_editor)

        self.open_button.pack()
        self.frame.pack()

    def open_editor(self):
        self.window.destroy()
        self.newWindow = tk.Toplevel(self.root)
        self.app = Editor(self.root, self.newWindow)

class Editor:
    def __init__(self, root, window):
        self.window = window
        self.root = root
        self.window.attributes("-fullscreen", True)

        #Create Sidebar and Diagram
        self.sidebar = tk.LabelFrame(self.window, text="Gates")
        self.frame = tk.LabelFrame(self.window, text="Diagram")
        self.diagram = tk.Canvas(self.frame, bg = "Black")

        #Create all sidebar buttons
        button_titles = ["and", "or", "not", "nor", "nand", "xor", "xnor", "buffer"]
        self.buttons = []
        for title in button_titles:
            button = tk.Button(self.sidebar, text = title, height = 1, width = 10, command = self.button_controller)
            self.buttons.append(button)
        
        #Bind canvas to zoom/pan options
        self.diagram.bind("<MouseWheel>", self.do_zoom)
        self.diagram.bind('<ButtonPress-1>', lambda event: self.diagram.scan_mark(event.x, event.y))
        self.diagram.bind("<B1-Motion>", lambda event: self.diagram.scan_dragto(event.x, event.y, gain=1))

        #Configure grid scaling
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(1, weight=1)
        self.sidebar.columnconfigure(0,weight=1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        #Add widgets to grid
        for i in range(len(self.buttons)):
            self.buttons[i].grid(row = i, column = 0, sticky = "EW")

        self.diagram.grid(row = 0, column = 0, sticky = "NSEW")
        self.sidebar.grid(row = 0, column = 0, sticky = "NS")
        self.frame.grid(row = 0, column = 1, sticky = "NSEW")

    def button_controller(self):
        print(os.getcwd())
        img = ImageTk.PhotoImage(Image.open("circle.png"))
        self.diagram.create_image(20, 20, image = img)
        self.diagram.image = img
    
    def do_zoom(self, event):
            x = self.diagram.canvasx(event.x)
            y = self.diagram.canvasy(event.y)
            factor = 1.001 ** event.delta
            self.diagram.scale(tk.ALL, x, y, factor, factor)
        
def main():
    root = tk.Tk()
    root.withdraw()
    window = tk.Toplevel(root)
    app = Home(root, window)
    root.mainloop()

if __name__ == '__main__':
    main()