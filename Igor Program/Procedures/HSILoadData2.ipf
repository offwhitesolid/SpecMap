#pragma TextEncoding = "UTF-8"
#pragma rtGlobals=3				// Use modern global access method and strict wave access
#pragma DefaultTab={3,20,4}		// Set default tab width in Igor Pro 9 and later

function createfolders()
	NewDataFolder/O root:Packages
	NewDataFolder/O root:Packages:myFolder
	Make/T/O/N=9 root:Packages:myFolder:Path
	NewDataFolder/O root:HSI
	NewDataFolder/O root:HSI:metadata
	NewDataFolder/O root:HSI:spec
	NewDataFolder/O root:HSI:rawspecs
	NewDataFolder/O root:HSI:spec:CosmicSpecs
end

function LoadPanel()
	variable coswid = 20
	variable costhr = 200
    NewDataFolder/O root:Packages
    NewDataFolder/O root:Packages:myFolder
    Make/T/O/N=9 root:Packages:myFolder:Path
    // cosmic width and tresh are 3 and 4
    // WL start,end in pixel x and y are 5 and 6
    // WL start,end in nm x and y are 7 and 8
    wave/T Path = root:Packages:myFolder:Path
    Path[3] = num2str(10)
    Path[4] = num2str(100)
     
    NewPanel /W=(81,73,774,248)/N=Load_Panel
    Button FilesDir,pos={13.00,10.00},size={140.00,20.00},proc=ButtonProc,title="Select Data Folder"
    SetVariable FilesDirDialog,pos={168.00,13.00},size={800.00,14.00},value= Path[0], title="Path"
    Button DoIt,pos={13.00,41.00},size={100.00,20.00},proc=ButtonProc,title="Load Data"
    SetVariable SpecNameDialog,pos={168.00,41.00},size={170.00,14.00},value= Path[1], title="Spec Name"
    SetVariable FirstHSINum,pos={350.00,41.00},size={140.00,14.00},value= Path[2], title="Start HSI count"
    
    SetVariable coswidth,pos={168.00,61.00},size={170.00,14.00},value= Path[3], title="Cosmic width", proc=SetVarProc, value=_STR:num2str(coswid)
    SetVariable costhresh,pos={350,61.00},size={140.00,14.00},value= Path[4], title="Cosmic thresh", proc=SetVarProc, value=_STR:num2str(costhr) 
    
    return 0
    
end

function ProcessPanel()
	wave WLwave = root:HSI:metadata:WL
	wave/T Path = root:Packages:myFolder:Path
	
	Path[5] = "0"
	Path[6] = "1023"
	Path[7] = num2str(WLwave[0])
	Path[8] = num2str(WLwave[1023])
	NewPanel /W=(81,73,774,248)/N=Process_Panel
	Button GenIntHSI,pos={13.00,10.00},size={140.00,20.00},proc=ButtonProc,title="Integrate Pixels to HSI"
	SetVariable wl_start, title="WL start (min="+Path[7]+" nm)",size={200,20},pos={170,10},proc=SetVarProc, value=_STR:Path[7]
    SetVariable wl_end, title="WL end (min="+Path[8]+" nm)",size={200,20},pos={400,10},proc=SetVarProc, value=_STR:Path[8]
	
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
       
            case "FilesDir"   :
                // set outputfolder
                NewPath/Q/O OutputPath
                PathInfo OutputPath
                Path[0] = S_Path
                break
           
            case "DoIt" :      		
                LoadHSIData()
                ProcessPanel()
                break
            
            case "GenIntHSI" :
            	integratehsidata()
            	break
       
        EndSwitch
End

function LoadHSIData()

	setdatafolder root:
	
    NewDataFolder/O root:Packages
    NewDataFolder/O root:Packages:myFolder
    //Make/T/O/N=7 root:Packages:myFolder:Path
    
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
    wave WL = root:HSI:metadata:WL
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
  	
  	Make/O /N=((xmax-xmin)/dx+1, (ymax-ymin)/dy+1, numpnts(WL)) hsidata
  	Make/O /N=((xmax-xmin)/dx+1, (ymax-ymin)/dy+1) PixMatrix
  	
  	setdatafolder root:
  	
  	
  	
  	PutSpecIn3DWave(xmin, ymin, dx, dy)

END

//	setdatafolder root:HSI:rawspecs
//	string a = wavelist("*", ";", "")
//	string stringspecwave = "root:HSI:spec:hsidata"
//	wave d = $stringspecwave
//	for (i=0; i<ItemsInList(a); i+=1)
//		substr = StringFromList(i,a)
//		wave c = $substr
//		gridx = (str2num(stringfromlist(0, stringfromlist(1, note(c), "x="), ";"))-xmin)/dx
//		gridy = (str2num(stringfromlist(0, stringfromlist(1, note(c), "y="), ";"))-ymin)/dy
//		for (j=0; j<1023; j+=1)
//			d[gridx][gridy][j] = c[j]
//		endfor
//	endfor

Function sumupcosmics()
	wave/T Path = root:Packages:myFolder:Path // width 3, tresh 4
	variable i
	variable j
	variable k
	string substr
	variable costresh = str2num(Path[4])
	setdatafolder root:HSI:spec:
	
	wave d = root:HSI:hsidata
	duplicate/O/D root:HSI:spec:hsidata, root:HSI:spec:hsidatad
	differentiate /dim=2 root:HSI:spec:hsidatad

	wave gridx = root:HSI:metadata:gridx
	wave gridy = root:HSI:metadata:gridy
	wave WL = root:HSI:metadata:WL
	wave hsiptr = root:HSI:spec:hsidatad
	make/O/N=(numpnts(WL), 0) currcol
	wave currcol
	Make/O/N=(numpnts(WL), 0) diffoverth
	wave diffoverth
	Make/O/N=(numpnts(WL), 0) diffunderth
	wave diffunderth
	
	variable countcosmics = 0
	variable somecosmics = 0
	
	// init diffoverth and diffoverth with zeros
	for (k=0; k<numpnts(WL); k+=1)
		diffoverth[k] = 0
		diffunderth[k] = 0
	endfor

	for (i=0; i<numpnts(gridx); i+=1)
		for (j=0; j<numpnts(gridy); j+=1)
			make/O/N=(numpnts(WL), 0) currcol
			// diffoverth and diffunterth collect cosmic start and end
			for (k=0; k<numpnts(WL); k+=1)
				if (hsiptr[i][j][k] > costresh)
					diffoverth[k] += hsiptr[i][j][k]
					somecosmics = 1
				endif
				if (hsiptr[i][j][k] < -costresh)
					diffunderth[k] += hsiptr[i][j][k]
					somecosmics = 1
				endif
			endfor
		endfor
	endfor
End

Function removecosmics()
	wave/T Path = root:Packages:myFolder:Path // width 3, tresh 4
	// iterators
	variable i // col
	variable j // row
	variable k // spec
	variable l // spec to remove cosmics
	string substr
	variable costresh = str2num(Path[4])
	variable coswidth = str2num(Path[3])
	setdatafolder root:HSI:spec:
	
	wave hs = root:HSI:spec:hsidata
	duplicate/O/D root:HSI:spec:hsidata, root:HSI:spec:hsidatad
	differentiate /dim=2 root:HSI:spec:hsidatad

	wave gridx = root:HSI:metadata:gridx
	wave gridy = root:HSI:metadata:gridy
	wave WL = root:HSI:metadata:WL
	wave hsiptrd = root:HSI:spec:hsidatad
	
	variable countcosmics = 0
	variable somecosmics = 0
	
	// now iterate over 3D wave to find cosmics
	for (i=1; i<numpnts(gridx)-1; i+=1)
		for (j=1; j<numpnts(gridy)-1; j+=1)
			for (k=1; k<numpnts(WL)-1; k+=1)
				if (hsiptrd[i][j][k] > costresh | hsiptrd[i][j][k] < -costresh)
					somecosmics = 1
				endif
			endfor
			
			if (somecosmics == 1)				
				variable cstart = 0
				variable cend = 0
				variable reading = 0
				// reading: 
				// 0=looking for cosmic, 
				// 1=up started, 2=down found, 3=up-down pair detected
				// 4=down started, 5=up found, 6=down-up pair detected
				for (k=0; k<numpnts(WL); k+=1)
					// cosmic start
					if (reading == 0)
						if (hsiptrd[i][j][k] > costresh)
							cstart = k
							reading = 1 // cosmic up started
						elseif (hsiptrd[i][j][k] < -costresh)
							cstart = k
							reading = 4 // cosmic down started
						endif
					// find cosmic end
					elseif (reading > 0)
						if (k-cstart <= coswidth) 
							print k, reading
							if (reading == 1)
								if (hsiptrd[i][j][k] < -costresh)
									// started with up, now detected down
									reading = 2
								endif
							elseif (reading == 2)
								if (hsiptrd[i][j][k] > -costresh)
									cend = k
									reading = 3
								endif
							elseif (reading == 4)
								if (hsiptrd[i][j][k] > costresh)
									// started with down, now detected up
									reading = 5
								endif
							elseif (reading == 5)
								if (hsiptrd[i][j][k] < costresh)
									cend = k
									reading = 6
								endif
							endif
						else
							// did not find cosmic within width
							reading = 0
						endif
						// cosmic start and end identified, now remove them
						if (reading == 3 | reading == 6 )
							for (l=cstart; l<cend; l+=1)
								print i, j, l, hs[i-1][j][l]
								// set the cosmic to the average value of the other pixels around it
								hs[i][j][l] = (hs[i-1][j-1][l]+hs[i-1][j][l]+hs[i-1][j+1][l]+hs[i][j-1][l]+hs[i][j+1][l]+hs[i+1][j-1][l]+hs[i+1][j][l]+hs[i+1][j+1][l])/8
							endfor
							reading = 0
							somecosmics = 0
						endif
					endif
				endfor
			endif
		endfor
	endfor
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
	wave WL = root:HSI:metadata:WL
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

// Slider demo test
Window SliderDemoPanel() : Panel
	PauseUpdate; Silent 1 // building window...
	NewPanel /W=(262,115,665,287)
	TitleBox Title0,pos={46,21},size={139,15},fSize=12,frame=0,fStyle=1
	TitleBox Title0,title="Live Mode Off"
	Slider slider0,pos={197,23},size={150,44},proc=Slider0Proc
	Slider slider0,limits={0,2,0},value=0,live=0,vert=0
	TitleBox Title1,pos={52,114},size={135,15},fSize=12,frame=0,fStyle=1
	TitleBox Title1,title="Live Mode On"
	Slider slider1,pos={197,113},size={150,44},proc=Slider1Proc
	Slider slider1,limits={0,2,0},value=0,live=0,vert=0
EndMacro

Function Slider0Proc(sa) : SliderControl // Action procedure for slider0
	STRUCT WMSliderAction &sa
	switch(sa.eventCode)
		case -3: // Control received keyboard focus
		case -2: // Control lost keyboard focus
		case -1: // Control being killed
			break
	default:
		if (sa.eventCode & 1) // Value set
			Printf "Value = %g, event code = %d\r", sa.curval, sa.eventCode
		endif
			break
	endswitch
	return 0
End

Function Slider1Proc(sa) : SliderControl // Action procedure for slider1
	STRUCT WMSliderAction &sa
	switch(sa.eventCode)
	case -3: // Control received keyboard focus
	case -2: // Control lost keyboard focus
	case -1: // Control being killed
		break
	default:
		if (sa.eventCode & 1) // Value set
			Printf "Value = %g, event code = %d\r", sa.curval, sa.eventCode
		endif
		if (sa.eventCode & 8) // Mouse moved or arrow key moved the slider
			Printf "Value = %g, event code = %d\r", sa.curval, sa.eventCode
		endif
		break
	endswitch
	return 0
End

// simple float input
// creates selection in analysis pull down menu

Menu "Analysis"
    "Open Calculate Panel",/Q, OpenCalculatePanel()
End
 
// creates panel, defines operations
 
Function OpenCalculatePanel()

// make space for the pane to live, name it

    DoWindow/K CalculatePanel
    Newpanel /W=(248,115,730,626)/N=CalculatePanel
   
// create a button, with title "Load Waves" that execeutes the procedure ButtonProc when pressed       
    Button button1,pos={160,165},size={161,35},proc=ButtonProc,title="String Maker"
//  
    SetVariable sample_name title="sample ",size={200,136},pos={136,100},proc=SetVarProc, value=_STR:"sample name"
    SetVariable ref_name title="reference ",size={200,136},pos={136,200},proc=SetVarProc, value=_STR:"reference name"
    SetVariable temp_list title="temperature list ",size={400,136},pos={40,300},proc=SetVarProc, value=_STR:"temperature list;separated by ; ex. 10;20 "
        return 0
end

Function SetVarProc(sva) : SetVariableControl
        STRUCT WMSetVariableAction &sva
 
        switch(sva.eventCode)
               case 1:
               case 2:
               case 3:
                     string/g sam = sva.sval
                  if(cmpstr(sva.ctrlname,"temp_list")==0)
                     print sva.ctrlname
                   endif
                     break
        endswitch
        return 0
end