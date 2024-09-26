#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3				// Use modern global access method and strict wave access
#pragma DefaultTab={3,20,4}		// Set default tab width in Igor Pro 9 and later

function Panel()
     NewDataFolder/O root:Packages
     NewDataFolder/O root:Packages:myFolder
     Make/T/O/N=5 root:Packages:myFolder:Path
     wave/T Path = root:Packages:myFolder:Path
     
    NewPanel /W=(81,73,774,248)
    Button FilesDir,pos={13.00,10.00},size={140.00,20.00},proc=ButtonProc,title="Select Data Folder"
    SetVariable FilesDirDialog,pos={168.00,13.00},size={800.00,14.00},value= Path[0], title="Path"
    Button DoIt,pos={13.00,41.00},size={100.00,20.00},proc=ButtonProc,title="Load Data"
    SetVariable SpecNameDialog,pos={168.00,41.00},size={170.00,14.00},value= Path[1], title="Spec Name"
    SetVariable FirstHSINum,pos={350.00,41.00},size={140.00,14.00},value= Path[2], title="Start HSI count"
    
    SetVariable coswidth,pos={168.00,61.00},size={170.00,14.00},value= Path[3], title="Cosmic width"
    SetVariable costhresh,pos={350,61.00},size={140.00,14.00},value= Path[4], title="Cosmic thresh" 
    
end

// define buttons
Function ButtonProc(ctrlName) : ButtonControl
    String ctrlName
   
        wave/T Path = root:Packages:myFolder:Path
        variable refnum
   
        strswitch(ctrlName)
       
            case "SelectFile1"  :
                // get File Paths
                Open/D/R/F="*.tif"/M="Select fist file" refNum
                if (strlen(S_FileName) == 0) // user cancelled or some error occured
                    return -1
                endif
                Path[0] = S_fileName
                break
       
            case "SelectFile2"  :
                // get File Paths
                Open/D/R/F="*.tif"/M="Select fist file" refNum
                if (strlen(S_FileName) == 0)
                    return -1
                endif
                Path[1] = S_fileName
                break
       
            case "FilesDir"   :
                // set outputfolder
                NewPath/Q/O OutputPath
                PathInfo OutputPath
                Path[0] = S_Path
                break
           
            case "DoIt" :      		
                LoadHSIData()
                break
       
        EndSwitch
End

function LoadHSIData()

	setdatafolder root:
	
    NewDataFolder/O root:Packages
    NewDataFolder/O root:Packages:myFolder
    Make/T/O/N=3 root:Packages:myFolder:Path
    wave/T Path = root:Packages:myFolder:Path
       		         		
    KillDataFolder/Z HSI
    
    	
    NewDataFolder/O root:HSI
    NewDataFolder/O root:HSI:metadata
    NewDataFolder/O root:HSI:spec
    NewDataFolder/O root:HSI:rawspecs
   	
    setdatafolder root:
    
    LoadDF1(Path[0], Path[1], Path[2])
    
end

function makeFigure(wX, wY)
	wave wX, wY
	Display wX vs wY
	ModifyGraph mode=4,marker=19,msize=5,lsize=2,lstyle=3,rgb=(52428,1,42942)
	Label left "\\Z14Speed"; DelayUpdate
	Label bottom "\\Z14Distance"; DelayUpdate
	ModifyGraph axThick=1.5
	ModifyGraph margin(left)=216, margin(bottim)=72, margin(right)=72, margin(top)=72
end function

function doFigureIfFlagged(wX, wY, doPlot)
	wave wX, wY
	int doPlot
	
	if(doPlot == 1)
		makeFigure(wX, wY)
	endif
end function

function loadfit() 
    string filename=""                             
    string pathname=""

    newpath/o temporaryPath
        if (v_flag!=0)
            return -1
        endif
    pathname= "temporarypath"

        /// Proceed to the loading waves from the selected folder!
end function  

static function /s sanitizeFPath(path)
    // Avoid annoyances with escape characters when using Microsoft Windows directories.
   
    string path
    path = replaceString("\t", path, "\\t")
    path = replaceString("\r", path, "\\r")
    path = replaceString("\n", path, "\\n")

    return path
end

function clearall()
	setdatafolder root:
	Killwaves/Z /A
	Killvariables/Z /A
	KillDataFolder/Z Packages
	KillDataFolder/Z HSI
	
end

// Given a path to a folder on disk, gets all files ending in "ext"
Function/S findallFiles(path, ext[, recurse])
// By default, subfolders are searched. Turn off with recurse=0.
// 2017-05-02, joel corbin
//
    string path, ext; variable recurse
   
    if (paramIsDefault(recurse))
        recurse=1
    endif
    path = sanitizeFilePath(path)                                               // may not work in extreme cases
   
    string fileList=""
    string files=""
    string pathName = "tmpPath"
    string folders =path+";"                                                    // Remember the full path of all folders in "path" & search each for "ext" files
    string fldr
    
    string thelist 
    variable nt
    
    do
        fldr = stringFromList(0,folders)
        NewPath/O/Q $pathName, fldr                                             // sets S_path=$path, and creates the symbolic path needed for indexedFile()
        PathInfo $pathName
        files = indexedFile($pathName,-1,ext)                                   // get file names
        if (strlen(files))
            files = fldr+":"+ replaceString(";", removeEnding(files), ";"+fldr+":") // add the full path (folders 'fldr') to every file in the list
            fileList = addListItem(files,fileList)
        endif
        if (recurse)
            folders += indexedDir($pathName,-1,1)                               // get full folder paths
        endif
        folders = removeFromList(fldr, folders)                                 // Remove the folder we just looked at
    while (strlen(folders))
    KillPath/Z $pathName
    //printf fileList
    printf "\n"
    //printf stringFromList(3, filelist)
    
    //nt = itemsInList(filelist)
    //printf "\n" + num2str(nt)
   	
    return filelist
end

static function /s sanitizeFilePath(path)
    // Avoid annoyances with escape characters when using Microsoft Windows directories.
   
    string path
    path = replaceString("\t", path, "\\t")
    path = replaceString("\r", path, "\\r")
    path = replaceString("\n", path, "\\n")

    return path
end

Function SetNote(wavenm, noteKey, newValueStr)
    WAVE wavenm
    string noteKey
    string newValueStr
   
    if(stringmatch(newValueStr,""))
        note/k wavenm, removebykey(noteKey,Note(wavenm),":","\r")
    else
        note/k wavenm, replacestringbykey(noteKey,Note(wavenm)," "+newValueStr,":","\r")
    endif
end

Function/S GetNote(wavenm,noteKey)
    WAVE wavenm
    string noteKey
    return stringbykey(noteKey,note(wavenm),":","\r")[1,inf]
end

Function LoadDF1(pathName, spechead, startHSIcount)
	String pathName
	String spechead
	String startHSIcount
	variable HSI0 = str2num(startHSIcount)
	String extension
	string name
	string opennames 
	string specfolder = ":HSI:rawspecs:"
	string metadataf = ":HSI:metadata:"
	string iasstr
	string wavenote
	
	Variable refNum
	string filePath
	string allfilesindir
	
 	name = spechead + "_" //"spectrum_"
 	extension = ".txt" 	
 	opennames = findallFiles(pathName, extension)
 	
 	variable ic 
 	variable vin 
 	vin = itemsInList(opennames)
 	//printf opennames
 	setdatafolder root:HSI:rawspecs
 	//wave wave1, wave2
 	string metadata
 	variable posx = 300
 	variable posy = 300
 	variable xmin = 300
 	variable xmax = 0
 	variable ymin = 300
 	variable ymax = 0
 	variable dx = 300
 	variable dy = 300
 	variable newdx = 0
 	variable newdy = 0
 	
 	for (ic=HSI0; ic<vin+HSI0; ic+=1)
 		sprintf iasstr "%05d", ic
 		string n1 = pathName + name + iasstr + extension
 		string n2 = pathName + name + iasstr + ".txt"
 		string n3 = pathName + name + iasstr
 		string n4 = name + iasstr
 		string n5 = pathName + name + iasstr + ".ibw"
 		string n6 = name + num2str(ic) //+ ".txt"
 		string Laserpos = "Laser Position"
 	
		string linedata
 		
 		// read the file and read the data
 		Loadwave/N/O/G/Q/C n1 // /G for .txt instead of /H for .ibw
 		wave wave0, wave1, wave2
 		if (ic == 0)
 			duplicate/O wave0, root:HSI:metadata:WL
 			duplicate/O wave1, root:HSI:metadata:BG
 		endif
 		
 		wave2 -= wave1 //root:HSI:metadata:BG
 		duplicate/O wave2, $n4
 		
 		// first try to read x and y coordinates
 		Loadwave/O/Q/C n5 // now late .ibw file to obtain meta data
 		metadata = stringfromlist(2, note($n6))
 		killwaves $n6
 		
 		posx = str2num(stringfromlist(1, stringfromlist(22, metadata, "\n"), ":"))
 		posy = str2num(stringfromlist(1, stringfromlist(23, metadata, "\n"), ":"))
 		
 		wavenote = "x=" + num2str(posx) + ";y=" + num2str(posy) + ";"
 		Setnote($n4, "Coordinates", wavenote)
 		
 		if (posx < xmin)
 			xmin = posx
 		endif
 		
 		newdx = posx - xmin
 		if (newdx < dx)
 			if (newdx > 0)
 				dx = posx - xmin
 			endif
 		endif
 		if (posx > xmax)
 			xmax = posx
 		endif
 		
 		if (posy < ymin)
 			ymin = posy
 		endif
 		
 		newdy = posy - ymin
 		if (newdy < dy)
 			if (newdy > 0)
 				dy = posy - ymin
 			endif
 		endif
 		if (posy > ymax)
 			ymax = posy
 		endif
 		
  	endfor
  	killwaves wave0, wave1, wave2
  	
  	setdatafolder root:HSI:metadata:
    make/O/N=(1024, 0) WL
    make/O BG
    make/O/N=(Ceil((xmax-xmin)/dx)+1, 0) gridx
    make/O/N=(Ceil((ymax-ymin)/dy)+1, 0) gridy
  	
 	variable new
  	// generate dx and dy matrix axes
  	for (ic=0; ic<=(xmax-xmin)/dx; ic+=1)
  		new = ic*dx
  		gridx[ic] = new
  	endfor
  	for (ic=0; ic<=(ymax-ymin)/dy; ic+=1)
  		new = ic*dy
  		gridy[ic] = new
  	endfor
  	
  	setdatafolder root:HSI:spec
  	
  	Make/O /N=((xmax-xmin)/dx+1, (ymax-ymin)/dy+1, 1024) hsidata
  	Make/O /N=((xmax-xmin)/dx+1, (ymax-ymin)/dy+1) PixMatrix
  	
  	setdatafolder root:
  	
  	PutSpecIn3DWave(xmin, ymin, dx, dy)

END

// Given a path to a folder on disk, gets all files ending in "ext"
Function/S findFiles(path, ext[, recurse])
// By default, subfolders are searched. Turn off with recurse=0.
// 2017-05-02, joel corbin
//
    string path, ext; variable recurse
   
    if (paramIsDefault(recurse))
        recurse=1
    endif
    path = sanitizeFilePath(path)                                               // may not work in extreme cases
   
    string fileList=""
    string files=""
    string pathName = "tmpPath"
    string folders =path+";"                                                    // Remember the full path of all folders in "path" & search each for "ext" files
    string fldr
    do
        fldr = stringFromList(0,folders)
        NewPath/O/Q $pathName, fldr                                             // sets S_path=$path, and creates the symbolic path needed for indexedFile()
        PathInfo $pathName
        files = indexedFile($pathName,-1,ext)                                   // get file names
        if (strlen(files))
            files = fldr+":"+ replaceString(";", removeEnding(files), ";"+fldr+":") // add the full path (folders 'fldr') to every file in the list
            fileList = addListItem(files,fileList)
        endif
        if (recurse)
            folders += indexedDir($pathName,-1,1)                               // get full folder paths
        endif
        folders = removeFromList(fldr, folders)                                 // Remove the folder we just looked at
    while (strlen(folders))
    KillPath $pathName
    return fileList
End

Function PutSpecIn3DWave(xmin, ymin, dx, dy)
	variable xmin
	variable ymin
	variable dx
	variable dy
	string substr
	variable i
	variable j
	variable gridx
	variable gridy
	setdatafolder root:HSI:rawspecs
	string a = wavelist("*", ";", "")
	string stringspecwave = "root:HSI:spec:hsidata"
	wave d = $stringspecwave
	for (i=0; i<ItemsInList(a); i+=1)
		substr = StringFromList(i,a)
		wave c = $substr
		gridx = (str2num(stringfromlist(0, stringfromlist(1, note(c), "x="), ";"))-xmin)/dx
		gridy = (str2num(stringfromlist(0, stringfromlist(1, note(c), "y="), ";"))-ymin)/dy
		for (j=0; j<1023; j+=1)
			d[gridx][gridy][j] = c[j]
		endfor
	endfor
End

Function IntHSItoPixMatrix()
	wave gridx = $"gridx"
	wave gridy = $"gridy"
	wave pixmat = $"root:HSI:spec:PixMatrix"
	wave hsidata = $"root:HSI:spec:hsidata"
	setdatafolder root:HSI:metadata
	variable i
	variable j
	for (i=0; i<numpnts(gridx); i+=1)
		for (j=0; j<numpnts(gridy); j+=1)
			root:HSI:spec:pixmat[i][j] = 1//sum(hsidata[i][][])
		endfor
	endfor
End

Function Integratehsidata()
	setdatafolder root:HSI:spec
	wave intmap = $"root:HSI:spec:intmap"
	wave hsidata = $"root:HSI:spec:hsidata"
	sumdimension/D=2 /DEST=intmap hsidata
	newimage intmap
	ModifyImage intmap ctab= {*,*,YellowHot256,0}
End

Function PlotPixMatrix()
	setdatafolder root:HSI:spec
	Display/K=0 root:HSI:spec:PixMatrix
	
End