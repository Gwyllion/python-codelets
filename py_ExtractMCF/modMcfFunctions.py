from tkinter import *
from tkinter.ttk import *
from urllib import request, error

# Write a function that will change the contents of a given Textbox/Entry e, with a given string value str
def editEntry(e,str) :
    e.configure(state='normal')
    e.delete(0,END)
    e.insert(0,str)
    e.configure(state='readonly')

# Write function that changes the state of an arraylist of radiobuttons
def changeRadioState() :
    global rbState
    if rbState == 'disabled':
        rbState='normal'
        customNameEntry.configure(state='normal')
    else:
        rbState='disabled'
        customNameEntry.configure(state='readonly')
    for rb in radiobuttons:
        rb.configure(state=rbState)

# Test whether there is an internet connection
def testConnection():
    try:
        response=request.urlopen('http://198.199.75.203',timeout=1)
        return True
    except error.URLError as err:
        pass
    return False
