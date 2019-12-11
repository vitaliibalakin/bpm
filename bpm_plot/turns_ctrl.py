#!/usr/bin/env python3

from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout
from PyQt5 import uic
import sys
import pycx4.qcda as cda
import numpy as np
import json
import pyqtgraph as pg
from bpm_plot.aux_mod.turns_plot import TurnsPlot
from bpm_plot.aux_mod.fft_plot import FFTPlot
from bpm_plot.aux_mod.coor_plot import CoorPlot


class TurnsControl(QMainWindow):
    def __init__(self):
        super(TurnsControl, self).__init__()
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')
        uic.loadUi("uis/plot's.ui", self)
        self.setWindowTitle('Orbit Plot')
        self.show()

        self.ic_mode = ' '

        # fft and turns
        self.fft_p = FFTPlot(self, self.status_bar)
        self.coor_p = CoorPlot(self)
        p0 = QVBoxLayout()
        self.fft_plot_p.setLayout(p0)
        p0.addWidget(self.coor_p)
        p0.addWidget(self.fft_p)

        self.fft_e = FFTPlot(self, self.status_bar)
        self.coor_e = CoorPlot(self)
        p1 = QVBoxLayout()
        self.fft_plot_e.setLayout(p1)
        p1.addWidget(self.coor_e)
        p1.addWidget(self.fft_e)

        self.turns_p = TurnsPlot(self)
        p2 = QVBoxLayout()
        self.turns_mes_plot_p.setLayout(p2)
        p2.addWidget(self.turns_p)

        self.turns_e = TurnsPlot(self)
        p3 = QVBoxLayout()
        self.turns_mes_plot_e.setLayout(p3)
        p3.addWidget(self.turns_e)

        # other ordinary channels
        self.chan_cmd = cda.StrChan('cxhw:4.bpm_preproc.cmd', max_nelems=1024)
        self.chan_res = cda.StrChan('cxhw:4.bpm_preproc.res', max_nelems=1024)
        self.chan_turns = cda.VChan('cxhw:4.bpm_preproc.turns', max_nelems=131072)
        self.chan_fft_coor = cda.VChan('cxhw:4.bpm_preproc.fft', max_nelems=262144)
        self.chan_mode = cda.StrChan("cxhw:0.k500.modet", max_nelems=4, on_update=1)

        # other ctrl callbacks
        self.chan_turns.valueMeasured.connect(self.turn_proc)
        self.chan_fft_coor.valueMeasured.connect(self.fft_coor_proc)
        self.chan_mode.valueMeasured.connect(self.mode_proc)
        self.chan_cmd.valueMeasured.connect(self.res)

        # boxes changes
        self.turns_bpm.currentTextChanged.connect(self.settings_changed)
        self.bpm_num_pts.valueChanged.connect(self.settings_changed)

    def cmd(self, chan):
        turn_bpm = json.loads(chan.val)['turn_bpm']
        num_pts = json.loads(chan.val)['num_pts']
        if turn_bpm != self.turns_bpm.currentText():
            self.turns_bpm.setText(turn_bpm)
        if num_pts != self.bpm_num_pts.value():
            self.bpm_num_pts.setValue(num_pts)

    def settings_changed(self):
        self.chan_cmd.setValue(json.dumps({'turn_bpm': self.turns_bpm.currentText(),
                                           'num_pts': self.bpm_num_pts.value()}))

    def turn_proc(self, chan):
        if self.ic_mode == 'p':
            self.turns_p.turns_plot(chan.val)
        elif self.ic_mode == 'e':
            self.turns_e.turns_plot(chan.val)
        else:
            print('WTF turn_proc')

    def fft_coor_proc(self, chan):
        if self.ic_mode == 'p':
            self.fft_p.fft_proc(chan.val)
            self.coor_p.coor_proc(chan.val)
        elif self.ic_mode == 'e':
            self.fft_e.fft_proc(chan.val)
            self.coor_e.coor_proc(chan.val)
        else:
            print('WTF fft_proc')

    def mode_proc(self, chan):
        self.ic_mode = chan.val[0]
        self.bpm_num_changed()
        if self.ic_mode == 'p':
            self.tab_fourier.setCurrentIndex(1)
            self.tab_turns.setCurrentIndex(1)
        elif self.ic_mode == 'e':
            self.tab_fourier.setCurrentIndex(0)
            self.tab_turns.setCurrentIndex(0)
        else:
            print('WTF mode_proc')


if __name__ == "__main__":
    app = QApplication(['turns_ctrl'])

    w = TurnsControl()
    sys.exit(app.exec_())
