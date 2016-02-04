import os, shutil, zipfile, xml.etree.ElementTree as ET
from subprocess import call

# Identify the full path of where the .EXE is located
folder = os.getcwd()

# Set the variables for the full paths of each subdirectory
binaries = os.path.join(folder, 'bin')

# Set the variable for the TRID tool that recognizes filetypes
tridLocation = os.path.join(binaries, 'trid.exe')

# Set the constant variable that will be used to prevent console windows to be opened
CREATE_NO_WINDOW = 0x08000000

# Create a function that will create given directory. If the directory exists, it will create a new directory with a version number
def createCustomDirectory(d):
    if not os.path.exists(d):
        os.makedirs(d)
        return(d)
    else:
        ctr=2
        while True:
            newDir = d+" v"+str(ctr)
            if not os.path.exists(newDir):
                os.makedirs(newDir)
                return(newDir)
            else:
                ctr+=1

def extractMCF(file_path,destination,openfolder,newfoldernameparam) :
# Start looping through the files in the 'raw' subdirectory
    mcf_file = os.path.basename(file_path)
    destination = os.path.normpath(destination)
    filename = os.path.splitext(mcf_file)[0]                    # Get the filename without its extension
    destination_path_tmp = os.path.join(destination, filename)      # Set the desired path for the new folder that will contain the extracted MCF
    print("D temp: "+destination_path_tmp)
    destination_path = createCustomDirectory(destination_path_tmp)  # Create this new folder that will contain the MCF. If it already exists, the path will be changed accordingly.
    destination_wildcard = os.path.join(destination_path, "*")  # Set the variable that will be used by TRID to identify each file's extension

    # Extract the MCF's contents to the 'extracted' folder
    with zipfile.ZipFile(file_path, "r") as mcf:
        mcf.extractall(destination_path)
        mcf.close()

    # TRID doesn't recognize proprietary filetypes like Mitchell's .MIE and the more generic .EST .
    # We would also like to rename a few files just for clarity's sake (the compliance report xml, for example)
    # For this, we will parse the MCF.XML file to identify the objects that weren't recognized by TRID, or the objects to rename

    # Parse the XML and give it a variable
    xml_path = os.path.join(destination_path, 'MCF.XML') 
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Loop through the different sections of the XML file.
    contentBools = [('Estimate PDF',0),('Estimate MIE',0),('Compliance Report',0),('Images',0)]
    claimNumber = "Undefined"
    insuredName = "Undefined"
    for child in root:
        # Look for the CLAIM NUMBER in the AdminData
        if child.tag == 'AdminData':
            claimNumber = child.find('ClaimNumber').text
        # Look for the INSURED NAME in the Entities
        if child.tag == 'Entities':
            for entity in child:
                if entity.find('EntityCode').text == 'IS':
                    insuredName = entity.find('FName').text + " " + entity.find('LName').text
                    break
        # Now let's look at all the objects included in the MCF file
        if child.tag == 'EObjects':
            # We then want to loop through all the EObjects and find the ones that are of interest t us
            for eobject in child:
                print("Iterating eObject " + eobject.find('ObjectID').text)
                # Look for the PDF Print Image so that we can check whether one was attached to the folder
                #if eobject.find('Desc2').text == 'PDF Print Image':
                if eobject[5].text == 'PDF Print Image':
                    pdf_path = os.path.join(destination_path, eobject.find('ObjectFileName').text) 
                    os.rename(pdf_path, os.path.join(destination_path, eobject.find('Desc1').text + " Estimate PDF.PDF"))
                    contentBools[0]=('Estimate PDF',1)
                # Look for the .MIE file so that we can rename it accordingly
                elif eobject[5].text == 'UltraMate Export File':
                    mie_path = os.path.join(destination_path, eobject.find('ObjectFileName').text) 
                    os.rename(mie_path, os.path.join(destination_path, eobject.find('Desc1').text + " Estimate MIE.MIE"))
                    contentBools[1]=('Estimate MIE',1)
                # Look for the .EST file so that we can rename it accordingly
                elif eobject[5].text == 'TEXT Print Image':
                    est_path = os.path.join(destination_path, eobject.find('ObjectFileName').text) 
                    os.rename(est_path, os.path.join(destination_path, eobject.find('Desc1').text + " Estimate Text.EST"))
                # Look for the Compliance Report so that we can rename it accordingly
                elif eobject[5].text == 'Estimate Review Log':
                    comp_path = os.path.join(destination_path, eobject.find('ObjectFileName').text) 
                    os.rename(comp_path, os.path.join(destination_path, eobject.find('Desc1').text + " Estimate Compliance Report.EST"))
                    contentBools[2]=('Compliance Report',1)
                # Look for the Dispatch Report so that we can rename it accordingly
                elif eobject.find('Desc1').text == 'Dispatch Report':
                    dr_path = os.path.join(destination_path, eobject.find('ObjectFileName').text) 
                    os.rename(dr_path, os.path.join(destination_path, "Dispatch Report.txt"))

    # Run TRID to identify the filetypes of the files that were in the MCFs. The '-ce' parameter immediately appends the correct extension
    call([tridLocation, destination_wildcard, "-ce"], stdout=open(os.devnull, 'wb'), creationflags=CREATE_NO_WINDOW)

    # Loop through the DESTINATION folder to get the filesize for each filetype
    filesizes = []
    print("START ANALYZING FILES....")
    print("==================================")
    print("  ")
    for extractedfile in os.listdir(destination_path):
        fullfilepath = os.path.join(destination_path,extractedfile)
        file_extension = os.path.splitext(extractedfile)[1]
        file_size = int(os.path.getsize(fullfilepath))
        found=0

        # PDF Files
        if file_extension.lower() == ".pdf":
            print("Found a PDF file whose size is " + str(file_size))
            ctrFS=0
            if filesizes :
                for ftype,fsize,fcount in filesizes :
                    if ftype=="PDF Files":
                        print("INSERT: filesizes["+str(ctrFS)+"]=("+ftype+","+ str(fsize+file_size) +","+ str(fcount+1))
                        filesizes[ctrFS]=(ftype,fsize+file_size,fcount+1)
                        print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                        found=1
                        break
                    else:
                        ctrFS+=1
            else :
                print("FIRST INSERT: filesizes.append(('PDF Files',"+str(file_size)+",1))")
                filesizes.append(("PDF Files",file_size,1))
                print(filesizes[0][0] + " files take up " + str(filesizes[0][1]) + " through " + str(filesizes[0][2]) + " files.")
                found=1
            if not found :
                print("FIRST INSERT: filesizes.append(('PDF Files',"+str(file_size)+",1))")
                filesizes.append(("PDF Files",file_size,1))
                print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                found=1

        # XML Files
        elif file_extension.lower() == ".xml":
            print("Found an XML file whose size is " + str(file_size))
            ctrFS=0
            if filesizes :
                for ftype,fsize,fcount in filesizes :
                    if ftype=="XML Files":
                        print("INSERT: filesizes["+str(ctrFS)+"]=("+ftype+","+ str(fsize+file_size) +","+ str(fcount+1))
                        filesizes[ctrFS]=(ftype,fsize+file_size,fcount+1)
                        print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                        found=1
                        break
                    else:
                        ctrFS+=1
            else:
                print("FIRST INSERT: filesizes.append(('XML Files',"+str(file_size)+",1))")
                filesizes.append(("XML Files",file_size,1))
                print(filesizes[0][0] + " files take up " + str(filesizes[0][1]) + " through " + str(filesizes[0][2]) + " files.")
                found=1
            if not found :
                print("FIRST INSERT: filesizes.append(('XML Files',"+str(file_size)+",1))")
                filesizes.append(("XML Files",file_size,1))
                print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                found=1
                

        # Image Files
        elif file_extension.lower() in (".png",".gif",".jpg",".jpeg",".bmp",".tiff",".tif"):
            contentBools[3]=('Images',1)
            print("Found an IMAGE file whose size is " + str(file_size))
            ctrFS=0
            if filesizes :
                for ftype,fsize,fcount in filesizes :
                    if ftype=="Images":
                        print("INSERT: filesizes["+str(ctrFS)+"]=("+ftype+","+ str(fsize+file_size) +","+ str(fcount+1))
                        filesizes[ctrFS]=(ftype,fsize+file_size,fcount+1)
                        print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                        found=1
                        break
                    else:
                        ctrFS+=1
            else:
                print("FIRST INSERT: filesizes.append(('Images',"+str(file_size)+",1))")
                filesizes.append(("Images",file_size,1))
                print(filesizes[0][0] + " files take up " + str(filesizes[0][1]) + " through " + str(filesizes[0][2]) + " files.")
                found=1
            if not found :
                print("FIRST INSERT: filesizes.append(('Images',"+str(file_size)+",1))")
                filesizes.append(("Images",file_size,1))
                print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                found=1

        # ZIP Files
        elif file_extension.lower() in (".zip"):
            print("Found a ZIP file whose size is " + str(file_size))
            ctrFS=0
            if filesizes :
                for ftype,fsize,fcount in filesizes :
                    if ftype=="ZIP Files":
                        print("INSERT: filesizes["+str(ctrFS)+"]=("+ftype+","+ str(fsize+file_size) +","+ str(fcount+1))
                        filesizes[ctrFS]=(ftype,fsize+file_size,fcount+1)
                        print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                        found=1
                        break
                    else:
                        ctrFS+=1
            else:
                print("FIRST INSERT: filesizes.append(('ZIP Files',"+str(file_size)+",1))")
                filesizes.append(("ZIP Files",file_size,1))
                print(filesizes[0][0] + " files take up " + str(filesizes[0][1]) + " through " + str(filesizes[0][2]) + " files.")
                found=1
            if not found :
                print("FIRST INSERT: filesizes.append(('ZIP Files',"+str(file_size)+",1))")
                filesizes.append(("ZIP Files",file_size,1))
                print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                found=1

        # Other filetypes
        elif not found :
            print("Found a MISCELLANEOUS file whose size is " + str(file_size))
            ctrFS=0
            if filesizes :
                for ftype,fsize,fcount in filesizes :
                    if ftype=="Other":
                        print("INSERT: filesizes["+str(ctrFS)+"]=("+ftype+","+ str(fsize+file_size) +","+ str(fcount+1))
                        filesizes[ctrFS]=(ftype,fsize+file_size,fcount+1)
                        print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                        found=1
                        break
                    else:
                        ctrFS+=1
            else:
                print("FIRST INSERT: filesizes.append(('Other',"+str(file_size)+",1))")
                filesizes.append(("Other",file_size,1))
                print(filesizes[0][0] + " files take up " + str(filesizes[0][1]) + " through " + str(filesizes[0][2]) + " files.")
                found=1
            if not found :
                print("FIRST INSERT: filesizes.append(('Other',"+str(file_size)+",1))")
                filesizes.append(("Other",file_size,1))
                print(filesizes[ctrFS][0] + " files take up " + str(filesizes[ctrFS][1]) + " through " + str(filesizes[ctrFS][2]) + " files.")
                found=1

    # Now rename the folder if the user wishes to do so
    newfoldername = os.path.basename(os.path.normpath(destination_path))
    if newfoldernameparam == "1":
        pass
    elif newfoldernameparam == "2":
        newfoldername = claimNumber
    elif newfoldernameparam == "3":
        newfoldername = insuredName
    else :
        newfoldername = newfoldernameparam

    newfolderpath = os.path.join(destination, newfoldername)

    if not os.path.exists(newfolderpath):
        os.rename(destination_path,newfolderpath)
    else:
        ctr=2
        while True:
            newfolderpath = newfolderpath+" v"+str(ctr)
            if not os.path.exists(newfolderpath):
                os.rename(destination_path,newfolderpath)
                break
            else:
                ctr+=1
    
    # Open the 'extracted' folder in Windows Explorer after we extracted all the MCFs
    if openfolder == 1:
        print("Opening "+newfolderpath)
        call(['explorer', newfolderpath], stdout=open(os.devnull, 'wb'), creationflags=CREATE_NO_WINDOW)

    # Return the destination path
    return (filename,claimNumber,insuredName,contentBools,filesizes)
