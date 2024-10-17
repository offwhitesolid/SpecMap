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
	make/O/N=1 root:Packages:myFolder:Pathnum
	variable/G root:Packages:myFolder:checkcosrem
end

// 1. run code in createfolders()
// 2. compile
// 3. copy the files of the testdataset to root:HSI:rawspecs
// 4. run Initfrotestdata(10, 10, 1024) for 10x10 testdataset with 1024 pixels per spec
// 		Note: filenames are constructed by i*ic+j in loop, maybe change this
// 5. call loadpanel() but do NOT click load data
// 6. call addcosmicremloadpanel() to remove cosmics from data set
// 7. insert Cosmic width and Cosmic thresh on loadpanel, then click Remove Cosmics to remove cosmics from testdataset
// 8. call processpanel() to open processpanel, from here on continue as usual
function Initfortestdata(ic, jc, wlc)
	variable ic // corresponds to x
	variable jc // corresponds to j
	variable wlc // number of points in WL
	variable i
	variable j
	setdataFolder root:HSI:metadata
	make/O/N=(ic, 0) gridx
	wave gridx
	for (i=0; i<ic; i+=1)
		gridx[i] = i
	endfor
	make/O/N=(jc, 0) gridy
	wave gridy
	for (j=0; j<jc; j+=1)
		gridy[j] = j
	endfor
	setdatafolder root:HSI:metadata
	make /O/N=(wlc) WL
	wave wl
	for (i=0;i<wlc;i+=1) 
		WL[i]=i 
	endfor
	PutTestSpecIn3DWave(ic, jc)
	
end

function LoadPanel()
    NewDataFolder/O root:Packages
    NewDataFolder/O root:Packages:myFolder
    Make/T/O/N=16 root:Packages:myFolder:Path
    Make/O/N=18 root:Packages:myFolder:Pathnum
    // pathnum to store numerical variables: 
    // Path:
    // cosmic width and thresh are 3 and 4
    // WL start,end in pixel x and y are 5 and 6
    // WL start,end in nm x and y are 7 and 8
    //
    // Pathnum A=6,7 B=8, 9 C=10,11 D=12,13 E=14,15 F=16,17 (x,y)
    wave/T Path = root:Packages:myFolder:Path
    wave Pathnum = root:Packages:myFolder:Pathnum
    Pathnum[3] = 10
    Pathnum[4] = 150
     
    NewPanel /W=(81,73,774,248)/N=Load_Panel
    Button FilesDir,pos={13.00,10.00},size={140.00,20.00},proc=ButtonProc,title="Select Data Folder",win=Load_Panel
    SetVariable FilesDirDialog,pos={168.00,13.00},size={800.00,14.00},value= Path[0], title="Path",win=Load_Panel
    Button DoIt,pos={13.00,41.00},size={100.00,20.00},proc=ButtonProc,title="Load Data",win=Load_Panel
    SetVariable SpecNameDialog,pos={168.00,41.00},size={170.00,14.00},value= Path[1], title="Spec Name",win=Load_Panel
    SetVariable FirstHSINum,pos={350.00,41.00},size={140.00,14.00},value=Path[2], title="Start HSI count",win=Load_Panel
     
    return 0
    
end

function addcosmicremonloadpanel()
	NVAR checkcosrem = root:Packages:myFolder:checkcosrem
	wave/T Path = root:Packages:myFolder:Path
	wave Pathnum = root:Packages:myFolder:Pathnum
	// create button elements for cosmic ray removal
	Button cosmicremoval,pos={13.00,65.00},size={140.00,20.00},proc=ButtonProc,title="Remove Cosmics",win=Load_Panel
    SetVariable coswidth,pos={168.00,65.00},size={170.00,14.00}, title="Cosmic width", proc=SetVarProc, value=Pathnum[3],win=Load_Panel
    SetVariable costhresh,pos={350,65.00},size={140.00,14.00}, title="Cosmic thresh", proc=SetVarProc, value=Pathnum[4],win=Load_Panel
    Checkbox showremcos, pos={500, 65}, title="Display removed Cosmics",proc=CheckProc, variable=checkcosrem, win=Load_Panel
end

function ProcessPanel()
	wave WLwave = root:HSI:metadata:WL
	wave/T Path = root:Packages:myFolder:Path
	wave Pathnum = root:Packages:myFolder:Pathnum
	
	Pathnum[5] = 0
	Pathnum[6] = numpnts(WLwave)-1
	Pathnum[7] = WLwave[0]												// lambda min
	Pathnum[8] = WLwave[numpnts(WLwave)-1] 								// lambda max
	Pathnum[9] = (WLwave[numpnts(WLwave)-1]-WLwave[0])/numpnts(WLwave) 	// = dlambda der WL achse
	Pathnum[10] = WLwave[0]												// lambda min selection
	Pathnum[11] = WLwave[numpnts(WLwave)-1]								// lambda max selection
	Pathnum[12] = 0														// lambda min selection in pixels
	Pathnum[13] = numpnts(WLwave)-1										// lambda max selection in pixels
		
	NewPanel /W=(81,73,774,248)/N=Process_Panel
	Button GenIntHSI,pos={13.00,10.00},size={140.00,20.00},proc=ButtonProc,title="Integrate Pixels to HSI",win=Process_Panel
	SetVariable wl_start, title="WL start (min="+num2str(Pathnum[7])+" nm)",size={200,20},pos={170,10},proc=SetVarProc, value=Pathnum[10],win=Process_Panel
    SetVariable wl_end, title="WL end (min="+num2str(Pathnum[8])+" nm)",size={200,20},pos={400,10},proc=SetVarProc, value=Pathnum[11],win=Process_Panel
    Button PlotspecCA, pos={13.00,30.00},size={180.00,20.00},proc=ButtonProc,title="Plot Spectrum under Cursor A",win=Process_Panel
    Button FitFunction, pos={13.00,50.00},size={180.00,20.00},proc=ButtonProc,title="Fit Function to hsi",win=Process_Panel
	
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
                addcosmicremonloadpanel()
                ProcessPanel()
                break
            
            case "GenIntHSI" :
            	//updateWLInput()
            	integratehsispeclim()
            	//integratehsidata()
            	break
            	
            case "cosmicremoval":
            	removecosmics()
            	break
            
            case "PlotspecCA":
				variable cx = pcsr(A)
            	variable cy = qcsr(A)
            	HSIplotspec(cx, cy)
            	break
            
            case "fitfunction":
            	FittoHSI()
       
        EndSwitch
End

function fittohsi()
	wave specfitwave
	
end


function HSIplotspec(x, y)
	variable x
	variable y
	variable i
	wave wl = root:HSI:metadata:Wl
	wave hsiptr = root:hsi:spec:hsidata
	string spec = "root:HSI:spec:specx" + num2str(x) + "y" + num2str(y)
	Make/O/N=(numpnts(WL)) $spec
	wave d =$spec
	for (i=0; i<numpnts(WL); i+=1)
		d[i] = hsiptr[x][y][i]
	endfor
	display d vs WL
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
	variable i
	variable j
	variable k
	
	Variable refNum
	string filePath
	string allfilesindir
	
 	name = spechead + "_" //"spectrum_"
 	extension = ".txt" 	
 	opennames = findallFiles(pathName, extension)
 	
 	variable ic 
 	variable vin 
 	vin = itemsInList(opennames)
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
  	Make/O /N=((xmax-xmin)/dx+1, (ymax-ymin)/dy+1, 20) Fitparameter
  	wave fit = $"Fitparameter"
  	for (i=0; i<(xmax-xmin)/dx+1; i+=1)
  		for (j=0; j<(ymax-ymin)/dy+1; j+=1)
  			for (k=0; k<(ymax-ymin)/dy+1; k+=1)
  				fit[i][j][k] = NaN
  			endfor
  		endfor
  	endfor
  	
  	
  	setdatafolder root:

  	PutSpecIn3DWave(xmin, ymin, dx, dy)

END

Function sumupcosmics()
	wave Pathnum = root:Packages:myFolder:Pathnum 
	wave Path = root:Packages:myFolder:Path			// width 3, tgresh 4
	variable i
	variable j
	variable k
	string substr
	variable costhresh = Pathnum[4]
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
				if (hsiptr[i][j][k] > costhresh)
					diffoverth[k] += hsiptr[i][j][k]
					somecosmics = 1
				endif
				if (hsiptr[i][j][k] < -costhresh)
					diffunderth[k] += hsiptr[i][j][k]
					somecosmics = 1
				endif
			endfor
		endfor
	endfor
End

Function removecosmics()
	wave Pathnum = root:Packages:myFolder:Pathnum 
	wave/T Path = root:Packages:myFolder:Path // width 3, tgresh 4
	NVAR checkcosrem = root:Packages:myFolder:checkcosrem
	// iterators
	variable i // col
	variable j // row
	variable k // spec
	variable l // spec to remove cosmics
	string substr
	variable costhresh = Pathnum[4]
	variable coswidth = Pathnum[3]
	setdatafolder root:HSI:spec:
	
	wave hs = root:HSI:spec:hsidata
	duplicate/O/D root:HSI:spec:hsidata, root:HSI:spec:hsidatad
	duplicate/O/D root:HSI:spec:hsidata, hsidatanocrm
	differentiate /dim=2 root:HSI:spec:hsidatad

	wave gridx = root:HSI:metadata:gridx
	wave gridy = root:HSI:metadata:gridy
	wave WL = root:HSI:metadata:WL
	wave hsiptrd = root:HSI:spec:hsidatad
	
	variable countcosmics = 0
	variable somecosmics = 0
	
	// now iterate over 3D wave to find cosmics
	for (i=0; i<numpnts(gridx); i+=1)
		for (j=0; j<numpnts(gridy); j+=1)
			for (k=0; k<numpnts(WL); k+=1)
				if (abs(hsiptrd[i][j][k]) > costhresh)
					somecosmics = 1
					break
				endif
			endfor
			
			if (somecosmics == 1)
				// display old spectrum with cosmic
				string plotname = "wi" + num2str(i) + "j"+ num2str(j)
				if (checkcosrem > 0)
					display/N=$plotname hsidatanocrm [i][j][]
					ModifyGraph rgb(hsidatanocrm)=(0,0,0)
				endif
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
						if (hsiptrd[i][j][k] > costhresh)
							cstart = k
							reading = 1 // cosmic up started
						elseif (hsiptrd[i][j][k] < -costhresh)
							cstart = k
							reading = 4 // cosmic down started
						endif
					// find cosmic end
					elseif (reading > 0)
						if (k-cstart <= coswidth) 
							if (reading == 1)
								if (hsiptrd[i][j][k] < -costhresh)
									// started with up, now detected down
									reading = 2
								endif
							elseif (reading == 2)
								if (hsiptrd[i][j][k] > -costhresh)
									cend = k
									reading = 3
								endif
							elseif (reading == 4)
								if (hsiptrd[i][j][k] > costhresh)
									// started with down, now detected up
									reading = 5
								endif
							elseif (reading == 5)
								if (hsiptrd[i][j][k] < costhresh)
									cend = k
									reading = 6
								endif
							endif
						else
							// did not find cosmic within width
							reading = 0
						endif
						// cosmic start and end identified, now remove them
						if (reading == 3 || reading == 6 )
							variable ci
							variable cj
							variable cl
							variable findcs
							for (l=cstart; l<cend; l+=1)
								if (i>0&&j>0&&l>0&&i<numpnts(gridx)-1&&j<numpnts(gridy)-1&&l<numpnts(WL)-1)
									// set the cosmic to the average value of the other pixels around it
									hs[i][j][l] = (hs[i-1][j-1][l]/sqrt(2)+hs[i-1][j][l]+hs[i-1][j+1][l]/sqrt(2)+hs[i][j-1][l]+hs[i][j+1][l]+hs[i+1][j-1][l]/sqrt(2)+hs[i+1][j][l]+hs[i+1][j+1][l]/sqrt(2))/(4+4/sqrt(2))
								else // at the edges of the HSI, select different methode
									// last or first WL pixel cosmic: set zero instead of interplating, since last WL pixel might also contain straylight and should never be located in a relevant spectral area
									print 2
									if (l==0||l>=numpnts(WL))
										hs[i][j][l] = 0
									elseif (i==0)
										if (j==0)
											hs[i][j][l] = (hs[i+1][j][l]+hs[i][j+1][l]+hs[i+1][j+1][l]/sqrt(2))/(2+1/sqrt(2))
										elseif (j>=numpnts(gridy))
											hs[i][j][l] = (hs[i+1][j][l]+hs[i][j-1][l]+hs[i+1][j-1][l]/sqrt(2))/(2+1/sqrt(2))
										else
											hs[i][j][l] = (hs[i][j-1][l]+hs[i][j+1][l]+hs[i+1][j-1][l]/sqrt(2)+hs[i+1][j][l]+hs[i+1][j+1][l]/sqrt(2))/(3+2/sqrt(2))
										endif
									elseif (i>=numpnts(gridx))
										if (j==0)
											hs[i][j][l] = (hs[i-1][j][l]+hs[i][j+1][l]+hs[i-1][j+1][l]/sqrt(2))/(2+1/sqrt(2))
										elseif (j>=numpnts(gridy)-1)
											hs[i][j][l] = (hs[i-1][j][l]+hs[i][j-1][l]+hs[i-1][j-1][l]/sqrt(2))/(2+1/sqrt(2))
										else
											hs[i][j][l] = (hs[i][j-1][l]+hs[i][j+1][l]+hs[i-1][j-1][l]/sqrt(2)+hs[i-1][j][l]+hs[i-1][j+1][l]/sqrt(2))/(3+2/sqrt(2))
										endif
									endif
								endif
							endfor
							reading = 0
							somecosmics = 0
						endif
						// add cosmic removed spectrum to plot 
						if (checkcosrem > 0)
							AppendToGraph/W=$plotname/L/B hs[i][j][]
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

function PutTestSpecIn3DWave(imax, jmax)
	variable imax
	variable jmax
	string substr
	variable i
	variable j
	variable k
	wave WL = root:HSI:metadata:WL
	setdatafolder root:HSI:spec
	Make/O /N=(imax, jmax, numpnts(WL)) hsidata
	setdatafolder root:HSI:rawspecs
	string a = wavelist("*", ";", "")
	string stringspecwave = "root:HSI:spec:hsidata"
	wave d = $stringspecwave
	for (i=0; i<imax; i+=1)
		for (j=0; j<jmax; j+=1)
			substr = StringFromList(i*imax+j,a)
			wave c = $substr
			for (k=0; k<1023; k+=1)
				d[i][j][k] = c[k]
			endfor
		endfor
	endfor
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

Function updateWLInput()
	wave/T path = root:Packages:myFolder:Path
	wave pathnum = root:Packages:myFolder:Pathnum
	wave WL = root:HSI:metadata:WL
	variable i
	variable j
	// check if wavemin and wavemax are within WL limits
	if (pathnum[10] > pathnum[7])
		if (pathnum[10] < pathnum[8])
		else
			pathnum[10] = pathnum[7]
		endif
	else
		pathnum[10] = pathnum[7]
	endif
	if (pathnum[11] < pathnum[8])
		if (pathnum[11] > pathnum[7])
		else
			pathnum[11] = pathnum[8]
		endif
	else
		pathnum[11] = pathnum[8]
	endif
	pathnum[12] = pathnum[10]
	for (i=0; i<numpnts(WL)-1; i+=1)
		if (Wl[i] > pathnum[10])
			pathnum[12] = i
			break
		endif
	endfor
	pathnum[13] = pathnum[6]
	for (i=numpnts(WL)-1; i>=0; i-=1)
		if (Wl[i] < pathnum[11])
			pathnum[13] = i
			break
		endif
	endfor	
	
end

Function Integratehsidata()
	wave/T path = root:Packages:myFolder:Path
	wave pathnum = root:Packages:myFolder:Pathnum
	setdatafolder root:HSI:spec
	wave intmap = $"root:HSI:spec:intmap"
	wave hsidata = $"root:HSI:spec:hsidata"
	sumdimension/D=2 /DEST=intmap hsidata
	newimage intmap
	ModifyImage intmap ctab= {*,*,YellowHot256,0}
End

Function Integratehsispeclim()
	updateWLInput()
	wave/T path = root:Packages:myFolder:Path
	wave pathnum = root:Packages:myFolder:Pathnum
	wave pixmatrix = $"root:HSI:spec:PixMatrix1"
	variable i
	variable j
	variable k
	
	wave gridx = root:HSI:metadata:gridx
	wave gridy = root:HSI:metadata:gridy
	wave WL = root:HSI:metadata:WL
	wave hsiptr = root:HSI:spec:hsidata
	wave xax = root:hsi:metadata:gridx
	wave yax = root:hsi:metadata:gridy
	string stringspecwave = "root:HSI:spec:pixmatrix1"
	Make/O /N=(numpnts(xax), numpnts(yax)) $stringspecwave
	wave d = $stringspecwave
	
	for (i=0; i<numpnts(gridx); i+=1)
		for (j=0; j<numpnts(gridy); j+=1)
			d[i][j] = 0
			for (k=pathnum[12]; k<=pathnum[13]; k+=1)
				d[i][j] += hsiptr[i][j][k]
			endfor
		endfor
	endfor
	
	wave pixmatrix1 = $"root:HSI:spec:pixmatrix1"
	newimage pixmatrix1
	ModifyImage pixmatrix1 ctab= {*,*,YellowHot256,0}
end

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
    "Open Calculate Pansel",/Q, OpenCalculatePanel()
End
 
// creates panel, defines operations

Function SetVarProc(sva) : SetVariableControl
        STRUCT WMSetVariableAction &sva
 
        switch(sva.eventCode)
               case 1:
               break
               case 2:
               	  	string/g sam = sva.sval
                  if(cmpstr(sva.ctrlname,"temp_list")==0)
                     print sva.ctrlname
                   endif
               break
               case 3:
               		string/g sam = sva.sval
                  if(cmpstr(sva.ctrlname,"temp_list")==0)
                     print sva.ctrlname
                   endif
                     break
        endswitch
        return 0
end

Function ButtonProct(ba) : ButtonControl
	Struct WMButtonAction &ba
	
	switch (ba.eventCode)
		case 2: // mouse up
			// click code here
			break
		case -1: // control being killed
			break
	endswitch
	
	return 0
End
	
Function CheckProc(cba) : CheckBoxControl
	STRUCT WMCheckboxAction &cba
		switch(cba.eventCode)
		case 2: // Mouse up
			Variable checked = cba.checked
			break
		case -1: // Control being killed
			break
		endswitch
	return 0
End

Function dolistbox(ba) : ButtonControl
	STRUCT WMButtonAction &ba

	switch( ba.eventCode )
		case 2: // mouse up
			// click code here
			wave fitbselect = root:packages:myfolder:fitboxselect
			wave/t fitfuncs = root:packages:myfolder:fitfunctions
			variable index, maxindex
			maxindex = numpnts(fitbselect)
			for(index=0;index<maxindex;index+=1)
				if(fitbselect[index])
					print fitfuncs[index]+"\r"
				endif
			endfor
			break
		case -1: // control being killed
			break
	endswitch

	return 0
End
