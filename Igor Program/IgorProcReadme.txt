Run Program: 
1. copy function body of createfolders() into command line and hit enter (compiling wont work before, since folders must be created first)
2. If folders are constructed properly, compile code
3. If compiled: open loadpanel by calling loadpanel() in the console
4. open folder with HSI data and insert name body according to convension (without number, e. g. HSI20241108_I01 to open HSI20241108_I01_00000.ibw, ...)
5. click on "load files", now process panel opens (can also be called via processpanel())


Load Test data into HSI program:
 multmasktoimg(root:hsi:spec:pixmatrix7, root:hsi:roi:roi2, "root:hsi:spec:pixmatrix7roi1")
 NewImage/K=0 root:HSI:spec:pixmatrix7roi1
 ColorScale/C/N=text0
 1. run code in createfolders()
 2. compile
 3. copy the files of the testdataset to root:HSI:rawspecs
 4. run Initfrotestdata(10, 10, 1024) for 10x10 testdataset with 1024 pixels per spec
 		Note: filenames are constructed by i*ic+j in loop, maybe change this
 5. call loadpanel() but do NOT click load data
 6. call addcosmicremloadpanel() to remove cosmics from data set
 7. insert Cosmic width and Cosmic thresh on loadpanel, then click Remove Cosmics to remove cosmics from testdataset
 8. call processpanel() to open processpanel, from here on continue as usual


Pathnum to store numerical variables: 
 cosmic width and thresh are 3 and 4
 WL start,end in pixel x and y are 5 and 6
 WL start,end in nm x and y are 7 and 8
Pathnum[9] = dlambda der WL achse
Pathnum[10] = WLwave[0] // lambda min selection
Pathnum[11] = WLwave[numpnts(WLwave)-1] // lambda max selection
Pathnum[12] = 0	// lambda min selection in pixels
Pathnum[13] = numpnts(WLwave)-1		// lambda max selection in pixels
Pathnum[14] = count threshold for fit (no fit if counts under thresh)
Pathnum[15] = number of existing pixmatrix
pathnum[16] = gridx[1] - gridx[0] // grid dx
pathnum[17] = gridy[1] - gridy[0] // grid dy
pathnum[18] = gauss fit WL pixel start
pathnum[19] = gauss fit WL pixel end
pathnum[20] = lorentz fit WL pixel start
pathnum[21] = lorentz fit WL pixel end
pathnum[22] = voigt fit WL pixel start
pathnum[23] = voigt fit WL pixel end
pathnum[24] = double gauss fit WL pixel start
pathnum[25] = double gauss fit WL pixel end
pathnum[26] = double lorentz fit WL pixel start
pathnum[27] = double lorentz fit WL pixel end
pathnum[28] = double voigt fit WL pixel start
pathnum[29] = double voigt fit WL pixel end

