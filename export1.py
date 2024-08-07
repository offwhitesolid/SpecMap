# add Frame to export PixMatrix
import csv
import tkinter as tk

class Exportframe():
    def __init__(self, Notebook, Nanomap) -> None:
        self.PixMatrix = [[0]]
        self.Notebook = Notebook
        self.Nanomap = Nanomap
        self.gdx = 1
        self.gdy = 1
        self.xaxis = [0]
        self.yaxis = [0]
        self.metadadict = {'Title': 'Pixel Matrix', 'Units': 'Counts', 'xaxis': self.Nanomap.PixAxX, 'yaxis': self.Nanomap.PixAxY}
        self.buildframe()

    def buildframe(self):
        self.export_frame = tk.Frame(self.Notebook, borderwidth=5, relief="ridge")
        self.export_frame.grid(row=0, column=1, sticky='nsew')
        self.export_button = tk.Button(self.export_frame, text='Export Pixel Matrix to PixMatrix.csv', command=lambda: self.export_to_csv(self.Nanomap.PixMatrix, 'PixMatrix.csv'))
        self.export_button.grid(row=0, column=0)
    
    # export a matrix like the PixMatrix to a csv file
    def export_to_csv(self, matrix, filename):
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            # first row is the header, gdx, gdy, and some further information
            for i in self.metadadict.keys():
                writer.writerow([i, str(self.metadadict[i])])
            # Write the matrix to the CSV file
            writer.writerows(matrix)