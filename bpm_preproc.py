#!/usr/bin/env python3

import numpy as np
import pycx4.qcda as cda
import sys
import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic


class BpmPreproc(QMainWindow):
    def __init__(self):
        super(BpmPreproc, self).__init__()
        uic.loadUi("for_fft.ui", self)
        self.bpm_x = {}
        self.bpm_z = {}
        self.chan_bpm_marker = []
        self.chan_bpm_numpts = []
        self.chan_bpm_vals = []
        self.for_fft_x = []
        self.for_fft_z = []

        self.bpms = {'bpm01': 21.4842, 'bpm02': 23.3922, 'bpm03': 24.6282, 'bpm04': 26.5572, 'bpm05': 0.8524,
                     'bpm07': 2.7974, 'bpm08': 4.0234, 'bpm09': 5.9514, 'bpm10': 7.7664, 'bpm11': 9.6884,
                     'bpm12': 10.9154, 'bpm13': 12.8604, 'bpm14': 14.5802, 'bpm15': 16.5152, 'bpm16': 17.7697}#,
                     #'bpm17': 19.6742}
        self.bpm_val_renew = {'bpm01': 0, 'bpm02': 0, 'bpm03': 0, 'bpm04': 0, 'bpm05': 0, 'bpm07': 0, 'bpm08': 0,
                              'bpm09': 0, 'bpm10': 0, 'bpm11': 0, 'bpm12': 0, 'bpm13': 0, 'bpm14': 0, 'bpm15': 0,
                              'bpm16': 0}#, 'bpm17': 0}
        self.bpm_numpts_renew = self.bpm_val_renew.copy()

        self.chan_x_orbit = cda.VChan('cxhw:4.bpm_preproc.x_orbit', max_nelems=16)
        self.chan_z_orbit = cda.VChan('cxhw:4.bpm_preproc.z_orbit', max_nelems=16)
        self.btn_fft.clicked.connect(self.save_fft)
        print('start')

        for bpm, bpm_coor in self.bpm_val_renew.items():
            # bpm numpts init
            chan = cda.VChan('cxhw:37.ring.' + bpm + '.numpts')
            chan.valueMeasured.connect(self.bpm_numpts)
            self.chan_bpm_numpts.append(chan)

            # bpm channels init
            chan = cda.VChan('cxhw:37.ring.' + bpm + '.datatxzi', max_nelems=4096)
            chan.valueMeasured.connect(self.data_proc)
            self.chan_bpm_vals.append(chan)

            # bpms marker init
            chan = cda.VChan('cxhw:37.ring.' + bpm + '.marker')
            chan.valueMeasured.connect(self.bpm_marker)
            self.chan_bpm_marker.append(chan)

    def save_fft(self):
        time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        np.savetxt("for_fft" + " " + time, np.vstack((self.for_fft_x, self.for_fft_z)))

    def bpm_numpts(self, chan):
        self.bpm_numpts_renew[chan.name.split('.')[-2]] = chan.val

    def data_proc(self, chan):
        bpm_num = chan.name.split('.')[-2]
        data_len = int(self.bpm_numpts_renew[bpm_num][0])
        self.bpm_x[bpm_num] = np.mean(chan.val[data_len:2*data_len-1])
        self.bpm_z[bpm_num] = np.mean(chan.val[2*data_len:3*data_len-1])

        if bpm_num == 'bpm15':
            self.for_fft_x = chan.val[data_len:2*data_len-1]
            self.for_fft_z = chan.val[2*data_len:3*data_len-1]

    def bpm_marker(self, chan):
        self.bpm_val_renew[chan.name.split('.')[-2]] = 1
        if all(sorted(self.bpm_val_renew.values())):
            for key in self.bpm_val_renew:
                self.bpm_val_renew[key] = 0
            x = np.array([])
            z = np.array([])
            for key in sorted(self.bpms, key=self.bpms.__getitem__):
                x = np.append(x, self.bpm_x[key])
                z = np.append(z, self.bpm_z[key])
            self.chan_x_orbit.setValue(x)
            self.chan_z_orbit.setValue(z)


if __name__ == "__main__":
    app = QApplication(['BPM'])
    w = BpmPreproc()
    sys.exit(app.exec_())
