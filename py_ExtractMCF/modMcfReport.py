from tkinter import *
from tkinter.ttk import *
from math import *

def popupReport(filename,claimnumber,insuredname,contentBools,filesizes) :
    # The POPUP window called reportWindow
    reportWindow = Toplevel()
    reportWindow.title("MCF Extraction Report")
    reportWindow.minsize(width=300, height=200)
    reportWindow.config(padx=5)

    # The TITLE showing at the top of the window
    reportHeader = Label(reportWindow, text="MCF Extraction Report", font="None 16 bold italic")
    reportHeader.pack()

    # The ADMIN DETAILS labelframe
    reportAdminFrame = LabelFrame(reportWindow, text="Administrative Information")
    reportAdminFrame.pack(fill="x",pady=(15,0))

    # The contents of the ADMIN DETAILS labelframe
    Label(reportAdminFrame, text="MCF Filename: ", font="none 9 bold").grid(row=0,column=0,sticky=W)
    Label(reportAdminFrame, text=filename).grid(row=0,column=1,sticky=W)
    Label(reportAdminFrame, text="Claim Number: ", font="none 9 bold").grid(row=1,column=0,sticky=W)
    Label(reportAdminFrame, text=claimnumber).grid(row=1,column=1,sticky=W)
    Label(reportAdminFrame, text="Insured Name: ", font="none 9 bold").grid(row=2,column=0,sticky=W)
    Label(reportAdminFrame, text=insuredname).grid(row=2,column=1,sticky=W)

    # The CONTENTS labelframe
    reportContentsFrame = LabelFrame(reportWindow, text="MCF Contents")
    reportContentsFrame.pack(fill="x",ipady=5,pady=(15,0))

    # Declare the CHECKMARK and X-MARK images
    checkmark = PhotoImage(file=r'imgs\checkmark.png')
    xmark = PhotoImage(file=r'imgs\xmark.png')

    # Function to DISPLAY contents of the CONTENTS labelframe
    def displayContentElement(elementname,b,ctr3) :
        if ctr3 <= 1 :
            c=0
            padleft=0
        else :
            c=2
            padleft=10
        if ctr3%2 == 0 :
            r=0
        else :
            r=1
            
        if b :
            contentsImage = Label(reportContentsFrame,image=checkmark)
            contentsImage.image = checkmark
        else :
            contentsImage = Label(reportContentsFrame,image=xmark)
            contentsImage.image = xmark
        contentsImage.grid(row=r,column=c,sticky=W,pady=(5,0),padx=(padleft,0))
        Label(reportContentsFrame, text=elementname, font="none 11 bold").grid(row=r,column=c+1,sticky=W,pady=(5,0))

    ctr5=0
    for key,val in contentBools:
        displayContentElement(key,val,ctr5)
        ctr5+=1
        
    # The ANALYSIS labelframe
    reportAnalysisFrame = LabelFrame(reportWindow, text="Filesize Analysis")
    reportAnalysisFrame.pack(fill="x",ipady=5,pady=(15,0))

    # List of available COLORS
    colors = ("red","blue","green","orange","yellow","purple","cyan","tan","sienna","dark slate gray")

    # Draw the PIE CHART
    pieChart = Canvas(reportAnalysisFrame,width=150,height=150)
    pieChart.grid(row=0,column=0,sticky=W,pady=5)
    xy=5,5,145,145
    # The CHART LEGEND frame
    pieChartLegendFrame = Frame(reportAnalysisFrame)
    pieChartLegendFrame.grid(row=0,column=1,sticky=W,pady=5)
    
    # Function that creates a PIE SLICE
    def pieslice(startpoint,slicesize,ftype,size,clr,counter) :
        pieChart.create_arc(xy,start=startpoint,extent=slicesize,fill=clr,style=PIESLICE)
        legend = Canvas(pieChartLegendFrame,width=12,height=12)
        legend.grid(row=counter,column=0,sticky=NW,padx=(20,0),pady=(6,0))
        legend.create_rectangle(0,0,12,12,fill=clr)
        Label(pieChartLegendFrame,text=ftype,font="none 9 bold").grid(row=counter,column=1,sticky=NW,padx=(5,0),pady=(5,0))
        Label(pieChartLegendFrame,text=size).grid(row=counter,column=2,sticky=NW,padx=(5,0),pady=(5,0))
    
    # Function that CONVERTS numeric filesize to string
    def convertSize(size):
       size_name = ("bytes", " kB", " MB", " GB", " TB", " PB", " EB", " ZB", " YB")
       i = int(floor(log(size,1024)))
       p = pow(1024,i)
       s = round(size/p,2)
       if (s > 0):
           return '%s %s' % (s,size_name[i])
       else:
           return '0 bytes'

    # Calculate the TOTAL FILESIZE
    totalFilesize = 0
    for ftype,fsize,fcount in filesizes:
        totalFilesize+=fsize

    ctr2=0
    startpoint=0
    endpoint=0
    for ftype,fsize,fcount in filesizes:
        endpoint=int(fsize*360/totalFilesize)
        pieslice(startpoint,endpoint,ftype,convertSize(fsize),colors[ctr2],ctr2)
        startpoint+=endpoint
        ctr2+=1    

    # The EXIT button
    button = Button(reportWindow, text="Dismiss", command=reportWindow.destroy)
    button.pack(pady=(15,0)) 
