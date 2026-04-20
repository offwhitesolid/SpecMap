import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button
import deflib1 as deflib

class Roihandler():
    def __init__(self, roilist={}, pixmatrix=[[]]):
        self.roi_mode = True
        self.roi_points = []
        self.roi_lines = []
        self.fig = None
        self.roilist = roilist
        self.pixmatrix = pixmatrix
        self.pixmatrix = np.transpose(self.pixmatrix)
        # loading init
        self.construct_roiselgui()
    
    def construct_roiselgui(self, roiselgui=None):
        if roiselgui is not None:
            self.roiselgui = roiselgui

    def construct(self, pixmatrix, roiselgui):
        self.pixmatrix = pixmatrix
        self.pixmatrix = np.transpose(self.pixmatrix)
        self.roiselgui = roiselgui
        self.fig, self.ax = plt.subplots()
        self.fig.subplots_adjust(right=0.89)# distance on right side for buttons
        self.ax.imshow(pixmatrix, cmap='viridis')
        # plt.axess([left, bottom, width, height])
        self.ax_button_toggle = plt.axes((0.89, 0.95, 0.1, 0.05))
        self.button_toggle = Button(self.ax_button_toggle, 'Save ROI')
        self.button_toggle.on_clicked(self.toggle_roi)
        self.ax_button_clear = plt.axes((0.89, 0.89, 0.1, 0.05))
        self.button_clear = Button(self.ax_button_clear, 'Clear ROI')
        self.button_clear.on_clicked(self.clear_roi)
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        plt.show()
        self.selnewestroi()

    def toggle_roi(self, event):
        if self.roi_mode == True:
            # Save the current ROI if valid
            if len(self.roi_points) > 2:
                fig, ax = plt.subplots()
                nrois = len(list(self.roilist.keys()))
                for i in range(len(self.roi_points)):
                    self.roi_points[i] = [float(self.roi_points[i][0]), float(self.roi_points[i][1])]
                newroi = deflib.highlight_roi(self.pixmatrix, self.roi_points)
                # transpose newroi
                #newroi = np.transpose(newroi)
                self.roilist[str('roi'+str(nrois+1))] = newroi
                cax = ax.imshow(newroi, cmap='viridis')
                # add colorbar to the plot
                cbar = fig.colorbar(cax, ax=ax)

                plt.show()
                self.roiselgui['values'] = list(self.roilist.keys())
                # Clear ROI points and lines to allow immediate painting of new ROI
                self.roi_points.clear()
                self.clear_roi_lines()
                # Keep roi_mode = True to allow immediate painting of next ROI
                print(len(self.roilist))
                plt.draw()
            else:
                # Not enough points, just clear and stay in painting mode
                self.roi_points.clear()
                self.clear_roi_lines()
                plt.draw()
        else:
            self.button_toggle.label.set_text('Save ROI')
            self.roi_points.clear()
            self.clear_roi_lines()
            self.roi_mode = True
            plt.draw()

    def clear_roi(self, event):
        self.clear_roi_points()
        self.clear_roi_lines()
        plt.draw()
            
    def on_click(self, event):
        if self.roi_mode and event.inaxes == self.ax:
            x, y = event.xdata, event.ydata
            self.roi_points.append((x, y))
            point_plot, = self.ax.plot(x, y, 'ro')
            self.roi_lines.append(point_plot)
            if len(self.roi_points) > 1:
                line_plot, = self.ax.plot([self.roi_points[-2][0], x],
                                            [self.roi_points[-2][1], y], 'r-')
                self.roi_lines.append(line_plot)
            plt.draw()

    def clear_roi_points(self):
        self.roi_points.clear()

    def clear_roi_lines(self):
        for line in self.roi_lines:
            line.remove()
        self.roi_lines.clear()
    
    def plotroi(self, fontsize=12):
        # get selection of self.roiselgui
        roi = self.roilist[self.roiselgui.get()]
        fig, ax = plt.subplots()
        cax = ax.imshow(roi, cmap='viridis')
        cbar = fig.colorbar(cax, ax=ax)
        cbar.set_label('ROI', fontsize=fontsize)
        cbar.ax.tick_params(labelsize=fontsize)
        ax.set_title('Region of Interest')
        ax.set_xlabel('Nanostage X Axis in \u03bcm', fontsize=fontsize)
        ax.set_ylabel('Nanostage Y Axis in \u03bcm', fontsize=fontsize)
        plt.show()
    
    def delete_roi(self):
        if self.roiselgui.get() != '':
            del self.roilist[self.roiselgui.get()]
            self.roiselgui['values'] = list(self.roilist.keys())
            self.selnewestroi()
            plt.show()
        else:
            pass
    
    def selnewestroi(self):
        if len(self.roilist) > 0:
            self.roiselgui.set(list(self.roilist.keys())[-1])
        else:
            self.roiselgui.set('')
    
    def on_close(self):
        plt.close('all')

if __name__ == "__main__":
    pass