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

## Do a Frame object for each MP, with methods
## or an MP object which has a frame
frame = []
for i in range(ndevices):
    frame.append(Frame(window,borderwidth=2,relief=GROOVE))
    frame[i].pack(side=LEFT,padx=10,pady=10)
    frame[i].label = Label(frame[i], text="Device "+str(i+1))
    frame[i].label.pack()
    frame[i].x = StringVar()
    frame[i].x.set('0')
    frame[i].xlabel = Label(frame[i], textvariable=frame[i].x)
    frame[i].xlabel.pack()
    #frame[i].Valeur = StringVar()
    #frame[i].Valeur.set(0.0)
    #frame[i].boite = Spinbox(frame[i],from_=0,to=10,increment=0.5,textvariable=frame[i].Valeur,width=5)
    #frame[i].boite.pack(padx=30,pady=10)

def move():
    frame[0].x.set(float(frame[0].x.get())+1)
    window.after(100, move)

window.after(100, move)

window.mainloop()
