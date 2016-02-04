from urllib import request, error
from PIL import Image
from shutil import copyfile
from os import *

# Add some variables
resizeActions = ["Resize and Copy","Resize and Replace Original"]
resizeDestinations = [r"<Create Subfolder 'Resized'>","<Same Folder as Original>","Browse..."]
resizeProfiles = [('eClaim',(500,None),"Resize and Copy",r"<Create Subfolder 'Resized'>"),
                  ('VGA (640x480)',(None,(640,480)),"Resize and Copy",r"<Create Subfolder 'Resized'>"),
                  ('Custom...',(None,None),"Resize and Copy",r"<Create Subfolder 'Resized'>")]
resizeProfileNames = []
for resizeProfile in resizeProfiles:
    resizeProfileNames.append(resizeProfile[0])

# Test whether there is an internet connection
def testConnection():
    try:
        response=request.urlopen('http://198.199.75.203',timeout=1)
        return True
    except error.URLError as err:
        pass
    return False

# Resize an image given a maximum filesize and maximum dimensions
standardSizes = [(4256,2848),(3008,2000),(2590,1920),(1920,1080),(1280,960),(1024,768),(800,600),(640,480),(320,240),(160,120),(80,60),(40,30)]
def imgResize(img,maxFilesize,maxDimensions):
    # Set the variables that will stay throughout the entire process
    originalPath = img                                               # Save a copy of the initial image's location
    fileDir = path.dirname(originalPath)                          # Get the image's directory
    fileName = path.splitext(path.basename(originalPath))[0]   # Get the image's filename
    fileExt = path.splitext(path.basename(originalPath))[1]    # Get the image's extension

    # Set a few variables that will be used throughout the resizing process
    filePath = originalPath                                     # Initialize the file path
    tmpPath = path.join(fileDir,fileName+"TMP"+fileExt)      # Define the location where we will save the temporary file
    ctr = 0                                                     # Initialize the counter
    
    # Start the resize algorithm
    while ctr <= len(standardSizes):
        #print(str(ctr))
        imgObject = Image.open(filePath)            # Load the image
        imgWidth, imgHeight = imgObject.size        # Get the image's dimensions
        imgRatio = imgWidth / imgHeight             # Get the image's aspect ratio
        imgFilesize = path.getsize(filePath)     # Get the image's filesize

        # Check the Dimensions
        # On the first pass, check the maximum dimensions given by the user.
        #  On the second pass, we're resizing to get a smaller filesize. For this, we use the array with standard sizes to identify what maximum dimensions to use.

        if not ctr:
            maxWidth, maxHeight = maxDimensions                 # Get the user-defined maximum dimensions if it's our first pass
        elif ctr > 1:
            maxWidth, maxHeight = standardSizes[ctr-1]          # If it's not our second pass, that means we already determined a spot in the array of standard sizes
        else:
            for standardX,standardY in standardSizes:
                #print("StandardX is "+str(standardX)+" and StandardY is "+str(standardY))
                if imgRatio < 1 :                                       # Identify a good starting point in our array of standard sizes. First, take the aspect ratio into account
                    if standardX <= imgHeight and standardY <= imgWidth:   # For PORTRAIT images  
                        maxWidth = standardY
                        maxHeight = standardX
                        break
                    else:
                        ctr+=1
                else:
                    if standardX < imgWidth or standardY < imgHeight:   # For LANDSCAPE images  
                        maxWidth = standardX
                        maxHeight = standardY
                        break
                    else:
                        ctr+=1
                    
        if maxWidth and maxHeight:                              # Only redimension if the given dimensions aren't 0
            if maxWidth < maxHeight:
                maxHeight2=maxHeight
                maxHeight=maxWidth
                maxWidth=maxHeight2                             # Re-arrange the maximum dimensions if the orientation is Portrait (higher than it is wide)
            #print("For this pass, maxWidth is "+str(maxWidth)+" and maxHeight is "+str(maxHeight))
            if imgWidth > maxWidth or imgHeight > maxHeight:    # Only redimension if there is a need to (if either the width or the height is bigger than the max)
                if imgRatio >= maxWidth/maxHeight :                              # Make sure the aspect ratio is maintained
                    newWidth = maxWidth                                 
                    newHeight = int(newWidth / imgRatio)
                else:
                    newHeight = maxHeight
                    newWidth = int(newHeight * imgRatio)
                imgObject = imgObject.resize((newWidth,newHeight),Image.ANTIALIAS)   # Resize the image object with the given width and height, preserving the aspect ratio
                filePath = tmpPath                                          # Set the in-work path to the temporary path
                imgObject.save(filePath)                                    # Save the temporary file
            else:
                if ctr:
                    imgObject.save(tmpPath)
                else:
                    copyfile(originalPath,tmpPath)
                filePath = tmpPath                                          # No redimensioning was needed. The dimensions meet the requirements
        else:
            pass                                                            # No redimensioning needed because no maximum dimensions were given

        # Check the FileSize
        #print("We're matching the filesize - "+str(path.getsize(filePath))+" - to the maximum, being "+str(maxFilesize))
        if maxFilesize :       # Only optimize if necessary (a maximum filesize is given and the current filesize is larger
            if path.getsize(filePath) > maxFilesize:
                filePath = tmpPath                                              # Set the in-work path to the temporary path
                imgObject.save(filePath,quality=60)                             # Save the image with reduced quality
                #print("We optimized the image. The filesize is now "+str(path.getsize(filePath)))
                if path.getsize(filePath) > maxFilesize :                    # If the filesize is still too large after reducing quality
                    imgObject.save(filePath)                                    #  then restore quality by reverting back to the un-optimized image
                else:
                    break                                                       # Otherwise we successfully resized the image to meet the requirements
            else:
                if ctr:
                    imgObject.save(tmpPath)
                else:
                    copyfile(originalPath,tmpPath)
                filePath = tmpPath
                break
        else:
            break                                                           # If we didn't even need to optimize, then just resizing was enough to meet the reqs

        # The file is still too large.
        ctr += 1

    # Return the filePath if we were able to resize to meet the requirements. Otherwise return False
    if ctr > len(standardSizes):
        return False
    else:
        return filePath

# A function that accepts a list of images, maxdimensions, maxfilesize, action to be taken and the destination to where the image should go
def imageResizeAndMove(imgPaths,maxFilesize,maxDimensions,action,dest,p):
    #print("Resized "+str(resizedImages.get())+" out of "+str(totalImages.get())+" Images")
    if action == resizeActions[1]:              # If the option is resize and replace, just replace the original with the resized file
        for imgPath in imgPaths:
            resizedImagePath = imgResize(imgPath,maxFilesize,maxDimensions)
            remove(imgPath)
            rename(resizedImagePath,imgPath)
    elif action == resizeActions[0]:             # If the option is resize and copy, then move the resized file to the given destination
        rootDir = path.dirname(imgPaths[0])              # Identify the root directory
        
        if dest == resizeDestinations[0]:               # If the resize destination is the subfolder, then create the subfolder and move the file in there
            subdir = path.join(rootDir,"Resized")        # Define the subdirectory
            if not path.exists(subdir):                  #  if it doesn't exist yet, create it
                makedirs(subdir)
            for imgPath in imgPaths:
                resizedImagePath = imgResize(imgPath,maxFilesize,maxDimensions)
                fileName = path.splitext(path.basename(imgPath))[0]   # Get the image's filename
                fileExt = path.splitext(path.basename(imgPath))[1]    # Get the image's extension
                newFilename = fileName+"-Resized"+fileExt                   # Create the new filename
                newFilePath = path.join(subdir,newFilename)              # Build the new path with the subfolder
                if path.exists(newFilePath):
                    replace(resizedImagePath,newFilePath)
                else:
                    rename(resizedImagePath,newFilePath)                     # Now move the file to the subfolder

        elif dest == resizeDestinations[1]:              # If the resize destination is the root folder, then just rename the file
            for imgPath in imgPaths:
                resizedImagePath = imgResize(imgPath,maxFilesize,maxDimensions)
                fileName = path.splitext(path.basename(imgPath))[0]   # Get the image's filename
                fileExt = path.splitext(path.basename(imgPath))[1]    # Get the image's extension
                newFilename = fileName+"-Resized"+fileExt                   # Create the new filename
                newFilePath = path.join(rootDir,newFilename)             # Build the new path within the root folder
                rename(resizedImagePath,newFilePath)                     # Now rename the file
            
        else:                                           # In any other case, the destination will be a custom location that exists, so just move the file in there
            for imgPath in imgPaths:
                resizedImagePath = imgResize(imgPath,maxFilesize,maxDimensions)
                fileName = path.splitext(path.basename(imgPath))[0]   # Get the image's filename
                fileExt = path.splitext(path.basename(imgPath))[1]    # Get the image's extension
                newFilename = fileName+"-Resized"+fileExt                   # Create the new filename
                newFilePath = path.join(dest,newFilename)# Build the new path within the given folder
                if path.exists(newFilePath):
                    replace(resizedImagePath,newFilePath)
                else:
                    rename(resizedImagePath,newFilePath)                     # Now move the file

        #ELSE print("The given action is unknown")    # The given action is unknown
    p.grab_release()
    p.destroy()
    p.quit()
    return True
