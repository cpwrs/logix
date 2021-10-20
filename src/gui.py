
"""
User Interface
Author: Carson Powers
"""


#Libraries
import tkinter as tk
from tkinter.constants import X
from PIL import ImageTk, Image
import json
import os


#Home screen: Open files/start new project
class Home:
    def __init__(self, root, window):
        self.window = window
        self.root = root

        #Create main frame, button to open editor (new project)
        self.frame = tk.Frame(self.window)
        self.open_button = tk.Button(self.frame, text = 'Open Editor', height = 1, width = 25, command = self.open_editor)

        #Add frame and button to Home window
        self.open_button.pack()
        self.frame.pack()

    #Deletes home window, opens up Editor window
    def open_editor(self):
        self.window.destroy()
        self.newWindow = tk.Toplevel(self.root)
        self.app = Editor(self.root, self.newWindow)


#Diagram structure
"""
Diagram
'---Object
    '---Input points
    '---Output points
"""


#Window to edit a logic gate diagram
class Editor:
    def __init__(self, root, window):
        self.window = window
        self.root = root

        #Create window of size 750x750
        self.window.geometry("750x750")

        #Create Sidebar and Diagram (Frame just holds the Canvas inside it)
        self.sidebar = tk.LabelFrame(self.window, text="Gates") #Sidebar holds buttons for all the objects you can add to the diagram
        self.frame = tk.LabelFrame(self.window, text="Diagram") #Frame holds the canvas
        self.diagram = tk.Canvas(self.frame, bg = "#808080") #Diagram is a canvas which contains all the entire logic gate simulation

        #Create all sidebar buttons - load one asset for each object type
        #Load data regarding the buttons names and assets from json file
        self.button_data = json.load(open("src/sidebar.json"))
        
        #Create table to hold each tk button, loaded_assets to load image for each type of object once
        #loaded_assets avoids garbage collection
        self.buttons = [] #Holds each tk.Button in the sidebar
        self.objects = [] #Holds tag of each object added to the diagram
        self.object_grabbed = False #False = no object currently being grabbed, otherwise holds tag of object being dragged
        self.loaded_assets = {} #Dictionary, key = title of object, value = asset of object

        #For each object, create its tk button, load its image asset, bind to handler, and append to list of buttons
        for title in self.button_data["gates"]:
            #Load asset from button_data and resize
            filename = self.button_data["gates"][title]["asset"]
            dimensions = self.button_data["gates"][title]["dimensions"]
            asset = ImageTk.PhotoImage(Image.open(filename).resize(dimensions))
            #Add asset to dictionary
            self.loaded_assets[title] = asset

            #Create tk.Button
            button = tk.Button(self.sidebar, text = title, height = 1, width = 10)
            button.bind("<ButtonPress-1>", self.gate_handler)
            self.buttons.append(button)
        
        #Bind canvas to zoom/pan functions
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


    #Handles the click of any gate object on the sidebar
    def gate_handler(self, event):
        #Create image on canvas
        title = event.widget['text']
        gate = self.diagram.create_image(20, 20, image = self.loaded_assets[title])
        #Add to list of canvas objects
        self.objects.append(gate)
        #Move image to top layer
        self.diagram.tag_raise(gate)

    
    #Determines whether the mouse is clicking down on an object, sets self.object_grabbed and returns value
    def is_grabbing_object(self, x, y):
        #Loop through each objects, newest to oldest (Top to bottom layer)
        for object in reversed(self.objects):
            #Get object coordinates
            coords = self.diagram.bbox(object)
            x1, y1, x2, y2 = coords

            #See if mouse position is inside these coordinates
            if((x1 < x and x < x2) and (y1 < y and y < y2)):
                self.object_grabbed = object
                return True

        self.object_grabbed = False
        return False


    #Handles any ButtonPress-1 on the diagram
    def down_handler(self, event):
        #Convert mouse coords to canvas coords (required due to canvas panning)
        x = int(self.diagram.canvasx(event.x))
        y = int(self.diagram.canvasy(event.y))

        #Check if clicking down on an object
        if(self.is_grabbing_object(x, y)):
            #Set starting point of object drag
            self.drag_x = x 
            self.drag_y = y
        else:
            #Set starting point of canvas pan
            self.diagram.scan_mark(event.x, event.y) #Doesn't need converted coordinates


    #Handles movement of mouse after pressed down
    def move_handler(self, event):
        #Check if object is being dragged
        if(self.object_grabbed):
            #Conver mouse coords to canvas coords
            x = int(self.diagram.canvasx(event.x))
            y = int(self.diagram.canvasy(event.y))

            #Calculate distance
            diff_x = x - self.drag_x
            diff_y = y - self.drag_y

            #Reset starting point of drag
            self.drag_x = x
            self.drag_y = y
            #Move object to new coords
            self.diagram.move(self.object_grabbed, diff_x, diff_y)
        else:
            #Pan diagram
            self.diagram.scan_dragto(event.x, event.y, gain=1)
    

    #Zoom canvas based on MouseScroll
    def do_zoom(self, event):
            x = self.diagram.canvasx(event.x)
            y = self.diagram.canvasy(event.y)
            factor = 1.001 ** event.delta
            self.diagram.scale(tk.ALL, x, y, factor, factor)
        

#Start main loop
def main():
    root = tk.Tk()
    #Don't display root, allows only one window to be open at a time
    root.withdraw()
    window = tk.Toplevel(root)
    app = Home(root, window)
    root.mainloop()

if __name__ == '__main__':
    main()