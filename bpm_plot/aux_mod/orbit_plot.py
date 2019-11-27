#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore
import sys
import numpy as np
import pyqtgraph as pg
from bpm_plot.aux_mod.bpm_point import BPMPoint
from bpm_plot.aux_mod.aper_plot import AperPlot


class OrbitPlot(pg.PlotWidget):
    def __init__(self, o_type, file_name, bpms, bpm_coor, parent):
        super(OrbitPlot, self).__init__(parent=parent)
        self.bpms = bpms
        self.showGrid(x=True, y=True)
        self.setLabel('left', o_type.upper() + " coordinate", units='mm')
        self.setLabel('bottom', "Position", units='m')
        self.setRange(yRange=[-40, 40])

        self.pos = {'cur': [], 'eq': [], 'dis': []}
        aper = np.transpose(np.loadtxt(file_name))
        self.addItem(AperPlot(aper))

        for coor in bpm_coor:
            bpm_e = BPMPoint(x=coor, color=QtCore.Qt.blue)
            bpm_c = BPMPoint(x=coor, color=QtCore.Qt.green)
            bpm_d = BPMPoint(x=coor, color=QtCore.Qt.red)
            self.addItem(bpm_e)
            self.addItem(bpm_c)
            self.addItem(bpm_d)
            self.pos['eq'].append(bpm_e)
            self.pos['cur'].append(bpm_c)
            self.pos['dis'].append(bpm_d)
        for bpm in self.pos['dis']:
            bpm.update_pos(100.0)
        self.update_orbit = {'eq': self.update_orbit_eq, 'cur': self.update_orbit_cur}

    def update_orbit_eq(self, orbit, bpm_list, std=np.zeros(16)):
        for i in range(len(self.bpms)):
            self.pos['eq'][i].update_pos(orbit[i])

    def update_orbit_cur(self, orbit, bpm_list, std=np.zeros(16)):
        for i in range(len(self.bpms)):
            if self.bpms[i] in bpm_list:
                # print(orbit)
                self.pos['cur'][i].update_pos(orbit[i])
                self.pos['dis'][i].update_pos(100.0)
            else:
                self.pos['cur'][i].update_pos(100.0)
                self.pos['dis'][i].update_pos(0.0)
        # for i in range(len(self.pos[which_orbit])):
        #     self.pos[which_orbit][i].update_pos(orbit[i])


if __name__ == "__main__":
    app = QApplication(['orbit_plot'])
    w = OrbitPlot("x", "x_aper.txt", ['bpm01', 'bpm02', 'bpm03', 'bpm04', 'bpm05', 'bpm07', 'bpm08', 'bpm09', 'bpm10',
                                      'bpm11', 'bpm12', 'bpm13', 'bpm14', 'bpm15', 'bpm16', 'bpm17'],
                  [0, 1.908, 3.144, 5.073, 6.7938, 8.7388, 9.9648, 11.8928, 13.7078, 15.6298, 16.8568, 18.8018, 20.5216,
                   22.4566, 23.7111, 25.6156], None)
    sys.exit(app.exec_())
