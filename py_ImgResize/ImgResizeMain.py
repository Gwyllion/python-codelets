import tkinter, io
from tkinter import *
from tkinter.ttk import *
from tkinter import font,filedialog,messagebox
#from tkinter import filedialog
from modImgResizeFunctions import *
from modImgProgress import *
from threading import Thread
from time import sleep
from os import *


# Version number
vNumber = "v0.1"

# Accepted filetypes
#myfiletypes = [("Image files",("*.png","*.gif","*.jpg","*.jpeg","*.bmp","*.tiff","*.tif"))]
myfiletypes = [(".JPEG Images",("*.jpg","*.jpeg"))]


### Start to build the interface    
# Initialize our TKINTER GUI window and call it root
root = Tk()
# Set the title of our window
root.title("Image Resizer 9000")
# Add the application icon
root.iconbitmap('imgs\ImgResize_Icon.ico')
# Set the size of our window
root.minsize(width=525, height=250)
# Disallow resizing the screen
root.resizable(0,0)
# Create a tkinter.Notebook variable that we will later add to our window. This allows us to have tabs.
note = Notebook(root)

# Create the variable for the source's path
sourcePath = StringVar()
selectedImages = []
# Write a function that opens a file dialog, stores the selected file's path and shows it in the textbox
def selectImages() :
    del selectedImages[:]    # Clear the list of selected images
    x = filedialog.askopenfilenames(filetypes=myfiletypes)
    if x == ('',):
        messagebox.showerror("Unable to read library location","Could not identify the location of the selected file(s). \nInstead of browsing through Windows' libraries, try selecting Desktop in the left hand pane and then open the folder that says your username. \nIdeally, you would browse through the full path of the images. E.g. C:\\Users\\[your username]\\")
    else:
        for y in x:
            selectedImages.append(y)
        # Clear the selectedPicturesFrame
        for child in selectedPicturesFrame.winfo_children():
            child.destroy()
        # Check whether we selected images
        if not selectedImages:
            Label(selectedPicturesFrame,text="None",font="none 9 italic").pack(padx=75)
        else:
            # Create the scrollbar and add it to our frame
            listboxImagesScrollbar = Scrollbar(selectedPicturesFrame,orient=VERTICAL)
            listboxImagesScrollbar.pack(side=RIGHT, fill=Y)
            # Create a listbox and add it to our user interface
            listboxImages = Listbox(selectedPicturesFrame)
            listboxImages.pack(padx=(4,3))
            # Loop through the selected images and add them to the listbox
            for selectedImg in selectedImages:  
                listboxImages.insert(END,path.basename(selectedImg))
            # Configure the scrollbar to interact with the listbox
            listboxImages.config(height=4,width=26,yscrollcommand=listboxImagesScrollbar.set)
            listboxImagesScrollbar.config(command=listboxImages.yview)

# Toggle the filter checkboxes
def toggleFilter(toggleBool,entries):
    if toggleBool:
        for e in entries:
            e.config(state=NORMAL)
    else:
        for e in entries:
            e.delete(0, END)
            e.config(state=DISABLED)

# Write a functions that will either enable or disable the inputs
def switchInputs(x):
    if x:
        cbMaxFilesize.config(state=NORMAL)
        enMaxFilesize.config(state=NORMAL)
        cbMaxDimensions.config(state=NORMAL)
        enMaxHeight.config(state=NORMAL)
        enMaxWidth.config(state=NORMAL)
    else:
        cbMaxFilesize.config(state=DISABLED)
        enMaxFilesize.config(state=DISABLED)
        cbMaxDimensions.config(state=DISABLED)
        enMaxHeight.config(state=DISABLED)
        enMaxWidth.config(state=DISABLED)

# Write a function that will clear the inputs
def clearInputs():
    switchInputs(1)
    boolMaxFilesize.set(False)
    enMaxFilesize.delete(0, END)
    boolMaxDimensions.set(False)
    enMaxHeight.delete(0, END)
    enMaxWidth.delete(0, END)

# Write the function that will be called when a profile is picked
def changeProfile(*args):
    clearInputs()
    if profileDropdownVar.get() == 'Custom...':
        toggleFilter(boolMaxFilesize.get(),[enMaxFilesize])
        toggleFilter(boolMaxDimensions.get(),[enMaxHeight,enMaxWidth])
    else:
        for resizeProfile in resizeProfiles:
            if resizeProfile[0] == profileDropdownVar.get():
                if resizeProfile[1][0]:
                    boolMaxFilesize.set(True)
                    enMaxFilesize.configure(state=NORMAL)
                    enMaxFilesize.insert(0,str(resizeProfile[1][0]))
                if resizeProfile[1][1]:
                    boolMaxDimensions.set(True)
                    enMaxHeight.configure(state=NORMAL)
                    enMaxWidth.configure(state=NORMAL)
                    enMaxHeight.insert(0,str(resizeProfile[1][1][0]))
                    enMaxWidth.insert(0,str(resizeProfile[1][1][1]))
                if resizeProfile[2]:
                    actionDropdownVar.set(resizeProfile[2]) 
                if resizeProfile[3]:
                    destinationDropdownVar.set(resizeProfile[3])
                switchInputs(0)
                break
            else:
                continue

# Write the function that will reset all fields
def resetFields():
    # Clear the selectedPicturesFrame
    for child in selectedPicturesFrame.winfo_children():
        child.destroy()
    selectedImages = []
    Label(selectedPicturesFrame,text="None",font="none 9 italic").pack(padx=75)
    # Set the profile to the default
    profileDropdownVar.set(resizeProfileNames[0])
    changeProfile()

# Write the function that will kill out program
def quitResizer():
    root.quit()
    root.destroy()

# Write a function that checks our entries for valid input
def validateEntry(d, i, P, s, S, v, V, W):
    userInput = P
    if userInput:
        try:
            int(userInput)
            if int(userInput) <= 9999:
                return True
            else:
                return False
        except ValueError:
            return False
    else:
        return True
                    
# Create the variable for the destination path
destinationPath = StringVar()
# Write a function that opens a file dialog, stores the selected directory's path and shows it in the textbox
def setDestination(*args) :
    if destinationDropdownVar.get() == "Browse...":
        destinationPath.set(filedialog.askdirectory(mustexist='true'))
        if len(destinationPath.get()) > 30:
            slicedPath = ".."+destinationPath.get()[len(destinationPath.get())-24:]            
            destinationDropdownVar.set(slicedPath)
        else:
            destinationDropdownVar.set(destinationPath.get())

# Write a function that runs the resize function
def runResizer(*args):
    if not selectedImages:                  # Make sure that images are selected
        messagebox.showwarning("No images were selected","Please select at least one image to resize.")
    elif not boolMaxFilesize.get() and not boolMaxDimensions.get():     # Make sure that at least one filter is chosen
        messagebox.showwarning("No filters selected","Please select either a maximum filesize or maximum dimensions")
    elif boolMaxFilesize.get() and not enMaxFilesize.get():             # Make sure that the selected filters are filled out
        messagebox.showwarning("Maximum filesize undefined",r"Please either deselect the maximum filesize filter or enter a maximum filesize value")
    elif boolMaxDimensions.get() and not (enMaxHeight.get() and enMaxWidth.get()):  # Make sure that the selected filters are filled out
        messagebox.showwarning("Maximum dimensions undefined",r"Please either deselect the maximum dimensions filter or enter a maximum height and width")
    elif not (enMaxHeight.get() and enMaxWidth.get()) and not enMaxFilesize.get():    # Make sure that at least one resizing value is filled out
        messagebox.showwarning("Insufficient input",r"Please either enter a maximum filesize and/or a maximum height AND width")
    elif enMaxFilesize.get() and int(enMaxFilesize.get()) < 5: # Make sure that the given maximum filesize is an acceptable size
        messagebox.showwarning("Computer says no",r"I understand that you want to put as many pictures on your floppy disk as you can, but 5 kB per picture is more than small enough.")
        enMaxFilesize.delete(0, END)
        enMaxFilesize.insert(0,"5")
    elif (enMaxWidth.get() and enMaxHeight.get()) and (int(enMaxWidth.get()) < 10 or int(enMaxHeight.get()) < 10): # Make sure that the given height and width are acceptable values
        messagebox.showwarning("Honey, I shrunk the kids",r"Let's be real: No one needs pictures smaller than 10px by 10px. Here, I'll get that for you...")
        enMaxHeight.delete(0, END)
        enMaxHeight.insert(0,"9999")
        enMaxWidth.delete(0, END)
        enMaxWidth.insert(0,"9999")
    else:
        if enMaxFilesize.get():
            maximumFileSize = int(enMaxFilesize.get())*1024
        else:
            maximumFileSize = None
        if enMaxWidth.get() and enMaxHeight.get():
            maximumDimensions = (int(enMaxWidth.get()),int(enMaxHeight.get()))
        else:
            maximumDimensions = (None,None)
        popupwindow = Toplevel()
        popupwindow.grab_set()
        
        if destinationPath.get() and not destinationDropdownVar.get() in resizeDestinations:
            t=Thread(target=imageResizeAndMove,args=(selectedImages,maximumFileSize,maximumDimensions,actionDropdownVar.get(),destinationPath.get(),popupwindow))
        else:
            t=Thread(target=imageResizeAndMove,args=(selectedImages,maximumFileSize,maximumDimensions,actionDropdownVar.get(),destinationDropdownVar.get(),popupwindow))
        t.start()
        popupProgressbar(popupwindow,len(selectedImages))
        if len(selectedImages) == 1:
            messagebox.showinfo("Resize Successful","Successfully resized "+str(len(selectedImages))+" image.")
        else:
            messagebox.showinfo("Resize Successful","Successfully resized "+str(len(selectedImages))+" images.")
        resetFields()
        del selectedImages[:]
        destinationPath.set("")

# Initialize the different tabs
tab1 = Frame(note)

### Build Tab 1
# Get the banner online if there is an online connection
#if testConnection():
#    request.urlretrieve("http://198.199.75.203/wp-content/uploads/2016/01/ImgResize_Banner.png", "imgs\ImgResize_Banner.png")
banner = PhotoImage(file='imgs\ImgResize_Banner.png')
bannerImage = Label(tab1,image=banner)
bannerImage.image = banner  # Redo the reference to prevent it from being garbage collected
bannerImage.pack(padx=5, pady=5)

# Create a FRAME as the main container
mainContainer = Frame(tab1,borderwidth=5,relief=GROOVE)
mainContainer.pack(fill="x",padx=5,pady=5)

# Create the FRAME on the LEFT, with the images
inputFrame = Frame(mainContainer, width=200)
inputFrame.grid(row=0,column=0,padx=5,sticky=NW)
# Create the Browse buttons
browseButton = Button(inputFrame, text='Select Images...', command=selectImages)
browseButton.pack(padx=5,pady=(5,10))
# Create the LABELFRAME that will contain the selected pictures
selectedPicturesFrame = LabelFrame(inputFrame, text="Selected Images:")
selectedPicturesFrame.pack(padx=(0,3))
# Add a LABEL to say that there are no images yet
Label(selectedPicturesFrame,text="None",font="none 9 italic").pack(padx=75)

# SEPARATOR
Separator(mainContainer,orient=VERTICAL).grid(row=0,column=1,sticky=NS)

# Create the FRAME on the RIGHT, with the output details
outputFrame = Frame(mainContainer)
outputFrame.grid(row=0,column=2,padx=5)

# Create the FRAME for the PROFILE DROPDOWN
profileFrame = Frame(outputFrame)
profileFrame.pack(fill="x")
# Add a LABEL for the profile dropdown
Label(profileFrame,text="Profile: ",font="none 9 bold").grid(row=0,column=0,sticky=NW, padx=5,pady=3)
# Add the DROPDOWN for the resize profiles
profileDropdownVar = StringVar()
profileDropdownVar.set("eClaim")   # Default value
profileDropdown = OptionMenu(profileFrame,profileDropdownVar,resizeProfileNames[0],*resizeProfileNames,command=changeProfile)
profileDropdown["menu"].config(bg="WHITE")
profileDropdown.grid(row=0,column=1,padx=5,sticky=NW)

# Create the FRAME for the RESIZING OPTIONS
optionsFrame = Frame(outputFrame)
optionsFrame.pack(fill="x")
# Write a function that checks our entries for valid input
vcmd = (optionsFrame.register(validateEntry),'%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
# Allow to choose the maximum filesize in KB
boolMaxFilesize = IntVar()
cbMaxFilesize = Checkbutton(optionsFrame, text="Maximum filesize: ", variable=boolMaxFilesize,command=lambda:toggleFilter(boolMaxFilesize.get(),[enMaxFilesize]))
cbMaxFilesize.grid(row=1,column=0,columnspan=7,sticky=NW,pady=5,padx=(15,0))
enMaxFilesize = Entry(optionsFrame,width=10,validate=ALL,validatecommand=vcmd)
enMaxFilesize.grid(row=1,column=7,columnspan=5,sticky=NW,pady=5,padx=(0,5))
Label(optionsFrame,text="kB").grid(row=1,column=12,columnspan=2,sticky=NW,pady=5)
# Allow to choose the maximum dimensions
boolMaxDimensions = IntVar()
cbMaxDimensions = Checkbutton(optionsFrame, text="Maximum dimensions: ", variable=boolMaxDimensions,command=lambda:toggleFilter(boolMaxDimensions.get(),[enMaxHeight,enMaxWidth]))
cbMaxDimensions.grid(row=2,column=0,columnspan=7,sticky=NW,pady=5,padx=(15,0))
enMaxHeight = Entry(optionsFrame,width=5,validate=ALL,validatecommand=vcmd)
enMaxHeight.grid(row=2,column=7,columnspan=3,sticky=NE,pady=5,padx=(0,5))
Label(optionsFrame,text="x").grid(row=2,column=10,sticky=W)
enMaxWidth = Entry(optionsFrame,width=5,validate=ALL,validatecommand=vcmd)
enMaxWidth.grid(row=2,column=11,columnspan=3,sticky=NW,pady=5,padx=(4,5))

# Create the FRAME for the ACTION and DESTINATION DROPDOWNs
actionFrame = Frame(outputFrame)
actionFrame.pack(fill="x")
# Add a LABEL for the ACTION dropdown
Label(actionFrame,text="Action: ",font="none 9 bold").grid(row=0,column=0,sticky=NW, padx=5,pady=3)
# Add the DROPDOWN for the resize ACTION
actionDropdownVar = StringVar()
def changeAction(*args):
    if actionDropdownVar.get()=="Resize and Replace Original":
        destinationDropdownVar.set("<Same Folder as Original>")
        destinationDropdown.config(state=DISABLED)
    else:
        destinationDropdown.config(state=NORMAL)
actionDropdownVar.set("Resize and Copy")   # Default value
actionDropdown = OptionMenu(actionFrame,actionDropdownVar,resizeActions[0],*resizeActions, command=changeAction)
actionDropdown["menu"].config(bg="WHITE")
actionDropdown.grid(row=0,column=1,padx=5,sticky=NW)
# Add a LABEL for the DESTINATION dropdown
Label(actionFrame,text="Destination: ",font="none 9 bold").grid(row=1,column=0,sticky=NW, padx=5,pady=3)
# Add the DROPDOWN for the copy's DESTINATION
destinationDropdownVar = StringVar()
destinationDropdownVar.set("<Same Folder as Original>")   # Default value
destinationDropdown = OptionMenu(actionFrame,destinationDropdownVar,resizeDestinations[0],*resizeDestinations,command=setDestination)
destinationDropdown["menu"].config(bg="WHITE")
destinationDropdown.grid(row=1,column=1,padx=5,sticky=NW)

## Create a FRAME for the BUTTONS
buttonFrame = Frame(tab1)
buttonFrame.pack(pady=(5,3))
# Add the RESET button
imgReset = PhotoImage(file=r'imgs\reset.png')
btnReset = Button(buttonFrame, text='Reset', image=imgReset, compound=LEFT,command=resetFields)
btnReset.grid(row=0,column=0)
# Add the RESIZE button
s = Style()
s.configure('Ibs.TButton',font=('none',9,'bold'))
imgResize = PhotoImage(file=r'imgs\resize.png')
btnResize = Button(buttonFrame, text='RESIZE', image=imgResize, compound=LEFT, style='Ibs.TButton',command=runResizer)
btnResize.grid(row=0,column=1,padx=10)
# Add the CANCEL button
imgCancel = PhotoImage(file=r'imgs\cancel.png')
btnCancel = Button(buttonFrame, text='Cancel', image=imgCancel, compound=LEFT,command=quitResizer)
btnCancel.grid(row=0,column=2)

# Initialize our resize profile
changeProfile()

# Give our tabs names
note.add(tab1, text = "Resize Image(s)")

# Now that we've built our tabs, we can stick it to our window
note.pack(fill="both", expand="yes")

# Show the window and start the main loop. The main loop is what listens for events (like clicks)
root.mainloop()

# Once the main loop is broken, the program will stop running
#exit()
