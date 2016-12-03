'''
Software to control SM-10 micromanipulator controller

Tkinter:
http://apprendre-python.com/page-tkinter-interface-graphique-python-tutoriel
http://fsincere.free.fr/isn/python/cours_python_tkinter.php
'''
from Tkinter import *
import tkFileDialog

ndevices = 3

window = Tk()
window.title('Manipulator')

device_name = ['Left manipulator','Right manipulator','Microscope']

## Do a Frame object for each MP, with methods
## or an MP object which has a frame
frame = []
for i in range(ndevices):
    frame.append(Frame(window,borderwidth=2,relief=GROOVE))
    frame[i].pack(side=LEFT,padx=10,pady=10)
    frame[i].label = Label(frame[i], text=device_name[i])
    frame[i].label.pack()

    frame[i].coordinate = [None,None,None]
    for j in range(3):
        frame[i].coordinate[j] = Label(frame[i], text='= 0 um')
        frame[i].coordinate[j].pack()

    #frame[i].x = StringVar()
    #frame[i].x.set('0')
    #frame[i].xlabel = Label(frame[i], textvariable=frame[i].x)
    #frame[i].xlabel.pack()

## Display coordinates
#for i in range(ndevices):
#    frame[i].coordinate[0].set('x = 0 um')


def move():
    frame[0].x.set(float(frame[0].x.get())+1)
    window.after(100, move)

#window.after(100, move)

window.mainloop()
