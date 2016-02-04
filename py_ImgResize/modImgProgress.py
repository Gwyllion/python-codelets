from tkinter import *
from tkinter.ttk import *
from PIL import Image

def popupProgressbar(progressRoot,numberOfImages) :
    #progressRoot = Toplevel()
    progressRoot.title("Resizing...")
    progressRoot.iconbitmap('imgs\PonyProgress_Icon.ico')
    progressRoot.minsize(width=200, height=180)
    progressRoot.maxsize(width=200, height=180)
    progressRoot.resizable(0,0)
    progressRoot.geometry('+300+300') 

    ponyContainer = Frame(progressRoot)
    ponyContainer.pack(fill=X)

    holder = Canvas(ponyContainer,height=110)
    holder.pack(padx=45)

    progressbarContainer = Frame(progressRoot)
    progressbarContainer.pack(fill=X)

    progressLabel = Label(progressbarContainer,text="Resizing "+str(numberOfImages)+" images...",font='None 10 bold')
    progressLabel.pack()

    pb = Progressbar(progressbarContainer,length=125,mode='indeterminate')
    pb.pack(padx=25)
    pb.start(interval=10)

    duration = 5*numberOfImages
    durationLabel = Label(progressbarContainer,text="This process can take up to "+str(duration)+" seconds",font='None 7 italic')
    durationLabel.pack()

    StaticFrame=[] #create empty
     
    #Importing the images. (FrameA,FrameB,...)
    alphabeta=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    for i in range(1,16):
        filename=r"imgs\progressImage\frame_"+alphabeta[i]+".png"
        StaticFrame+=[PhotoImage(file=filename)]
     
    def animatePony(currentframe):

        def change_image():
            holder.create_image(0,0,anchor=NW,image=StaticFrame[currentframe], tag='Animate')

        # Delete the current picture if one exists
        try: holder.delete('Animate')
        except:
            pass
        try:
            change_image()
        except IndexError:
            # When you get to the end of the list of images - it simply resets itself back to zero and then we start again
            currentframe = 0
            change_image()
        holder.update_idletasks() #Force redraw
        currentframe = currentframe + 1
        # Call loop again to keep the animation running in a continuous loop
        progressRoot.after(75, animatePony, currentframe)

    # Start the animation loop just after the Tkinter loop begins
    progressRoot.after(10, animatePony, 0)
 
    progressRoot.mainloop()
    

    

