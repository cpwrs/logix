
"""
User Interface
Author: Carson Powers
"""

import tkinter as tk
from PIL import ImageTk, Image
import json
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
        #Create window of size 750x750
        self.window.geometry("750x750")

        #Create Sidebar and Diagram (Frame just holds the Canvas inside it)
        self.sidebar = tk.LabelFrame(self.window, text="Gates")
        self.frame = tk.LabelFrame(self.window, text="Diagram")
        self.diagram = tk.Canvas(self.frame, bg = "Black")


        #Create all sidebar buttons - load one asset for each object type
        #Load data regarding the buttons names and assets from json file
        self.button_data = json.load(open("src/sidebar.json"))
        
        #Create table to hold each tk button, loaded_assets to load image for each type of object once
        #loaded_assets avoids garbage collection
        self.buttons = []
        self.objects = []
        self.object_grabbed = False
        self.loaded_assets = {}

        #For each object, create its tk button, load its image asset, bind to handler, and append to list of buttons
        for title in self.button_data["gates"]:
            #Load asset
            filename = self.button_data["gates"][title]["asset"]
            dimensions = self.button_data["gates"][title]["dimensions"]

            asset = ImageTk.PhotoImage(Image.open(filename).resize(dimensions))
            self.loaded_assets[title] = asset

            #Create button
            button = tk.Button(self.sidebar, text = title, height = 1, width = 10)
            button.bind("<ButtonPress-1>", self.gate_handler)
            self.buttons.append(button)
        

        #Bind canvas to zoom/pan options
        self.diagram.bind("<MouseWheel>", self.do_zoom)
        self.diagram.bind('<ButtonPress-1>', self.down_handler)
        self.diagram.bind("<B1-Motion>", self.move_handler)


        #Configure grid scaling
        self.window.rowconfigure(0, weight=1)
        self.window.columnconfigure(1, weight= 1)
        self.sidebar.columnconfigure(0,weight = 1)
        self.frame.rowconfigure(0, weight=1)
        self.frame.columnconfigure(0, weight=1)

        #Add buttons to sidebar grid
        for i in range(len(self.buttons)):
            self.buttons[i].grid(row = i, column = 0, sticky = "EW")
        #Add all other widgets to grid
        self.diagram.grid(row = 0, column = 0, sticky = "NSEW")
        self.sidebar.grid(row = 0, column = 0, sticky = "NS")
        self.frame.grid(row = 0, column = 1, sticky = "NSEW")


    def gate_handler(self, event):
        #Create image on canvas
        title = event.widget['text']
        gate = self.diagram.create_image(20, 20, image = self.loaded_assets[title])
        #Add to list of canvas objects
        self.objects.append(gate)
        #Move image to top layer
        self.diagram.tag_raise(gate)

    
    def grabbing_object(self, x, y):
        #Loop through each objects, newest to oldest (Top to bottom layer)
        for object in reversed(self.objects):
            #Get object coordinates
            coords = self.diagram.bbox(object)
            x1, y1, x2, y2 = coords

            #See if mouse position is inside these coordinates
            if((x1 < x and x < x2) and (y1 < y and y < y2)):
                self.object_grabbed = object
                print("Test")
                return True
        self.object_grabbed = False
        return False

    def down_handler(self, event):
        x, y = event.x, event.y
        if(self.grabbing_object(x, y)):
            self.grab_coords = [x, y]
        else:
            self.diagram.scan_mark(x, y)

    def move_handler(self, event):
        if(self.object_grabbed):
            diff_x = event.x - self.grab_coords[0]
            diff_y = event.y - self.grab_coords[1]
            self.grab_coords = [event.x, event.y]
            self.diagram.move(self.object_grabbed, diff_x, diff_y)
        else:
            self.diagram.scan_dragto(event.x, event.y, gain=1)
    

    def do_zoom(self, event):
            x = self.diagram.canvasx(event.x)
            y = self.diagram.canvasy(event.y)
            factor = 1.001 ** event.delta
            self.diagram.scale(tk.ALL, x, y, factor, factor)
        
def main():
    root = tk.Tk()
    #Don't display root, allows only one window to be open at a time
    root.withdraw()
    window = tk.Toplevel(root)
    app = Home(root, window)
    root.mainloop()

if __name__ == '__main__':
    main()