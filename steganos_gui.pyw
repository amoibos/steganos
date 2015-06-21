#!/usr/bin/env python

try:
    from Tkinter import *
    import tkFileDialog as filedialog
    from tkMessageBox import showinfo
except ImportError:
    from tkinter import *
    from tkinter.messagebox import showinfo

from steganos import Steganos

__author__ = "Daniel Oelschlegel"
__copyright__ = "Copyright 2015, " + __author__
__credits__ = [""]
__license__ = "NBSD"
__version__ = "0.0.1"

class Steganos_Gui():
    
    def __init__(self):
        self.window = Tk(className="Steganos")
        self.window.resizable(False, False)
        
        self.label1 = Label(self.window, text="text: ", pady=10)
        self.label1.grid(row=0,column=0)
        self.text = StringVar()
        self.entry1 = Entry(self.window, textvariable=self.text)
        self.text.set('sample text')
        self.entry1.grid(row=0, column=1)
        
        self.label2 = Label(self.window, text="password: ", pady=10)
        self.label2.grid(row=1,column=0)
        self.password = StringVar()
        self.entry2 = Entry(self.window, textvariable=self.password)
        self.entry2.grid(row=1, column=1)

        self.label3 = Label(self.window, text="path to image: ", pady=10)
        self.label3.grid(row=2, column=0)
        self.source = StringVar()
        self.entry3 = Entry(self.window, textvariable=self.source)
        self.source.set('C:\\')
        self.entry3.grid(row=2, column=1)
        self.button2 = Button(master=self.window, text="...", command=self.openDialog)
        self.button2.grid(row=2, column=2, padx=10)
        
        self.button2 = Button(master=self.window, text="update", command=self.update, 
            padx=50, textvariable=self.update)  
        self.button2.grid(row=3, column=0)
        self.button3 = Button(master=self.window, text="save", command=self.save, 
            padx=50, textvariable=self.save)  
        self.button3.grid(row=3, column=1)
        self.button4 = Button(master=self.window, text="extract", command=self.extract, 
            padx=50, textvariable=self.extract)  
        self.button4.grid(row=3, column=2)       
        self.window.mainloop()
     
    def update(self):
       showinfo('', 'not implemented yet')

    def save(self):
        showinfo('', 'not implemented yet')

    def extract(self):
        self.text.set(Steganos(self.source.get(), self.password.get()).extract())
  
    def openDialog(self):
        filePath = filedialog.askopenfilename(parent=self.window,
            initialdir=self.source.get(), 
            title="Please select an image")
        self.source.set(filePath)
    
if __name__ == "__main__":
    steganos_gui = Steganos_Gui()    