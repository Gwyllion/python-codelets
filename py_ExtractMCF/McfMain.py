import tkinter, io, time
from tkinter import filedialog
from modMcfFunctions import *
from modMcfExtraction import *
from modMcfReport import *
from tkinter.ttk import *
from urllib import request

# Create the variable that holds the list of allowed filetypes
myfiletypes = [('MCF Files', '*.MCF')]

# Version number
vNumber = "v0.1"

# Initialize the path variables
filePath = ""
outputPath = ""

# Create the variable that will say whether our rename radiobuttons are disabled or not
rbState = 'disabled'
# Create the variable that will say whether the user wants to use a custom directory name or not
customNameState = 'disabled'

### Start to build the interface    
# Initialize our TKINTER GUI window and call it root
root = Tk()
# Set the title of our window
root.title("MCF Uber Extractor")
# Add the application icon
root.iconbitmap('imgs\MCF_Icon.ico')
# Set the size of our window
root.minsize(width=600, height=350)
# Create a tkinter.Notebook variable that we will later add to our window. This allows us to have tabs.
note = Notebook(root)

# Create the variable for the source's path
sourcePath = StringVar()
# Write a function that opens a file dialog, stores the selected file's path and shows it in the textbox
def setFilePath(e,ftypes,msg) :
    filePath = filedialog.askopenfilename(filetypes=ftypes)
    if filePath == "":
        editEntry(e,msg)
    else:
        editEntry(e,filePath)
    sourcePath.set(filePath)

# Create the variable for the destination path
outputPath = StringVar()
# Write a function that opens a file dialog, stores the selected directory's path and shows it in the textbox
def setOutputPath(e,msg) :
    outputPath_tmp = filedialog.askdirectory(mustexist='true')
    if outputPath_tmp == "":
        editEntry(e,msg)
    else:
        editEntry(e,outputPath_tmp)
    outputPath.set(outputPath_tmp)

# Write function that changes the state of an arraylist of radiobuttons
def changeRadioState() :
    global rbState
    if rbState == 'disabled':
        rbState='normal'
        customNameEntry.configure(state=customNameState)
    else:
        rbState='disabled'
        customNameEntry.configure(state='disabled')
    for rb in radiobuttons:
        rb.configure(state=rbState)

def changeCustomNameState(*args) :
    global customNameState
    if renameOption.get() == 4:
        customNameState='normal'
    else:
        customNameState='disabled'
    customNameEntry.configure(state=customNameState)

# The EXECUTION FUNCTION when we click execute
executionOutput = ()
def executeExtraction():
    # Create the list of errors
    errorList = list()
    ### Start testing for errors
    if not sourcePath.get() :     # Test for empty input path
        errorList.append("Empty input path. Please select a valid MCF file.")
    elif not os.path.exists(sourcePath.get()): # Test for invalid input path
        errorList.append("File doesn't exist. Please select a valid MCF file.")
    if not outputPath.get() :     # Test for empty Output path
        errorList.append("Empty output directory. Please select a valid directory.")
    elif not os.path.isdir(outputPath.get()) :   # Test for invalid output path
        errorList.append("Invalid output directory. Please select a valid directory.")

    # Start extraction if the errorList is empty
    if not errorList :
        # Set the destination foldername parameter. Option 4 = Custom name
        destinationFolderParam = "1"
        if renameOption.get() == 4 :
            destinationFolderParam = customNameEntry.get()
        else :
            destinationFolderParam = str(renameOption.get())
        
        # Extract and store the output in the variable EXTRACTIONOUTPUT
        extractionOutput = extractMCF(sourcePath.get(),outputPath.get(),bool_openFolder.get(),destinationFolderParam)
        if bool_showReport.get() :
            popupReport(extractionOutput[0],extractionOutput[1],extractionOutput[2],extractionOutput[3],extractionOutput[4])
    # Otherwise, show a messagebox with the error messages
    else :
        messagebox.showwarning('Could not extract', "\n".join(errorList))

# Initialize the different tabs
tab1 = Frame(note)
#tab2 = Frame(note)
#tab3 = Frame(note)

### Build Tab 1
# Get the banner online if there is an online connection
if testConnection():
    request.urlretrieve("http://198.199.75.203/wp-content/uploads/2016/01/MCF_Banner.png", "imgs\MCF_Banner.png")
banner = PhotoImage(file='imgs\MCF_Banner.png')
bannerImage = Label(tab1,image=banner)
bannerImage.image = banner  # Redo the reference to prevent it from being garbage collected
bannerImage.pack(padx=50, pady=15)
# Create a LABELFRAME for the input file and destination directory
fileFrame = LabelFrame(tab1, text="Files / Directories")
fileFrame.pack(fill="x")
## Fit the different components in the grid
# Create the labels
Label(fileFrame, text="Select MCF file").grid(row=0, sticky=W)
Label(fileFrame, text="Select output directory").grid(row=1, sticky=W)
# Create the textboxes
sourceEntry = Entry(fileFrame)
outputEntry = Entry(fileFrame)
# Configure the textboxes/280
sourceMessage = "Click on the Browse button to select the MCF file"
sourceEntry.insert(0,sourceMessage)
sourceEntry.configure(state='readonly', width=60)
outputMessage = "Click on the Browse button to select the output directory"
outputEntry.insert(0,outputMessage)
outputEntry.configure(state='readonly', width=60)
# Fit the textboxes in the grid
sourceEntry.grid(row=0, column=1)
outputEntry.grid(row=1, column=1)
# Create the Browse buttons
Button(fileFrame, text='Browse...', command=lambda:setFilePath(sourceEntry,myfiletypes,sourceMessage)).grid(row=0, column=2)
Button(fileFrame, text='Browse...', command=lambda:setOutputPath(outputEntry,outputMessage)).grid(row=1, column=2)

# Create a LABELFRAME for the Settings for extracting an MCF
extractSettingsFrame = LabelFrame(tab1, text="Extraction Settings")
extractSettingsFrame.pack(fill="x",pady=(15,0))
## Fit the different components in the grid
# Create the variable that will determine wether or not the user wants the destination folder to be opened
bool_openFolder = IntVar()
# Create the variable that will determine wether or not the user wants to generate the Extraction Report
bool_showReport = IntVar()
# Create a checkbox whether or not to open the destination folder upon extraction
checkbox_openFolder = Checkbutton(extractSettingsFrame, text="Open folder after extraction", variable=bool_openFolder)
checkbox_openFolder.grid(row=0, column=0, padx=(0,20), sticky=W)
# Create a checkbox whether or not to show the high-level report upon extraction
checkbox_showReport = Checkbutton(extractSettingsFrame, text="Show high level report", variable=bool_showReport)
checkbox_showReport.grid(row=0, column=1, sticky=W)

# Create a LABELFRAME for the Rename options
renameOptionsFrame = LabelFrame(tab1, text="Rename options")
renameOptionsFrame.pack(fill="x",pady=15)
# Create a checkbox whether or not to rename the destination folder to something else than the MCF's filename
bool_renameFolder = IntVar()
checkbox_renameFolder = Checkbutton(renameOptionsFrame, text="Rename destination folder", variable=bool_renameFolder, command=changeRadioState)
checkbox_renameFolder.grid(row=0, column=0, sticky=W, pady=5, columnspan=3)
## Create the radio buttons that give you the different rename options
# Set the variable that holds the radiobuttons' state
renameOption = IntVar()
renameOption.set(1)
renameOption.trace('w',changeCustomNameState)
# Build the radiobuttons and add them to an arraylist for easy navigation
radiobuttons = []
radiobuttons.append(Radiobutton(renameOptionsFrame,text="File name",variable=renameOption,value=1,state='disabled'))
radiobuttons[0].grid(row=1,column=0,sticky=W, padx=(20,10))
radiobuttons.append(Radiobutton(renameOptionsFrame,text="Claim number",variable=renameOption,value=2,state='disabled'))
radiobuttons[1].grid(row=1,column=1,sticky=W, padx=(0,10))
radiobuttons.append(Radiobutton(renameOptionsFrame,text="Insured",variable=renameOption,value=3,state='disabled'))
radiobuttons[2].grid(row=1,column=2,sticky=W, padx=(0,10))
radiobuttons.append(Radiobutton(renameOptionsFrame,text="Custom:",variable=renameOption,value=4,state='disabled'))
radiobuttons[3].grid(row=1,column=3,sticky=W, padx=(0,3))
customNameEntry = Entry(renameOptionsFrame,state='disabled', width=30)
customNameEntry.grid(row=1,column=4,sticky=W)

## Create a FRAME for the EXTRACT button
extractFrame = Frame(tab1)
extractFrame.pack(fill="x",pady=(0,5))
# Add the button
Button(extractFrame, text='Extract',command=executeExtraction).pack(side=BOTTOM)
# Add version number
#Label(extractFrame, text=vNumber).pack(side=LEFT)

# Give our tabs names
note.add(tab1, text = "Extract MCF")
#note.add(tab2, text = "Tab Two")
#note.add(tab3, text = "Tab Three")

# Now that we've built our tabs, we can stick it to our window
note.pack(fill="both", expand="yes")

# Show the window and start the main loop. The main loop is what listens for events (like clicks)
root.mainloop()

# Once the main loop is broken, the program will stop running
exit()
