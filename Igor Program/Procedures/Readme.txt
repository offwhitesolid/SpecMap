use newest procedure (see time stamp)
1. Load Procedure in Igor
2. If Compile fails (it might fail, since folders will not be found):
	look for the function createfolders(), copy its code into the console and run it by hitting enter. 
	Now all required folders will be produced

3. Run the HSI Program: 
	Call the Loadpanel by running Loadpanel() in the console

Open HSI spectra
4. Open the spectra to construct the HSI by following these steps:
	1. Klick "Select Data Folder" and select the folder in which the spectra are located
	2. Enter the name Body of the Spectra until the last "_"
		Example: Spectra name ist "HSI20240909_I01_00000.txt" enter here "HSI20240909_I01"
		Note: This must be the same for all spectra
	3. Enter the "Start HSI count"
		Example: If HSI spectra are "HSI20240909_I01_00000.txt" to "HSI20240909_I01_00399.txt" it must be 0
		Note: This is number is the start of the "counter" to open the spectra
	4. Klick on "Load Data" to load the data. If everything worked properly, the Process_panel should be opened

Cosmic ray removal
5. If u have successfully loaded the Data, you can remove the cosmics by clicking "Remove Cosmics"

Create HSI Image
6. Click "Integrate Pixels to HSI" on the Process_Panel to create the HSI. On this image, the counts on each spectrum are summed up. 