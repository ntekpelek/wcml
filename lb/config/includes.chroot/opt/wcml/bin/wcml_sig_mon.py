#! /usr/bin/env python
#
# wcml_sig_mon.py is part of wcml ( WiFi Coverage Mapper Live ), maintained at
# https://github.com/ntekpelek/wcml
# Released under GNU GPL v2
# Copyright (C) 2015 Adam Piontek
#
import subprocess
import threading
import time
import zmq

# change to your system wifi interface
INTF = 'wlan0'


class SignalMonitor(object):
    UPD_INTERV = 0.3

    def __init__(self, intf):
        self.intf = intf
        self.sig = [-200,-200,-200]
        self.t_iw = threading.Thread(target=self._retrieve_iw)
        self.t_iw.start()
        self.ctx = zmq.Context()
        self.skt = self.ctx.socket(zmq.REP)
        self.skt.bind("tcp://*:55555")
        self.t_zmq = threading.Thread(target=self._reply)
        self.t_zmq.start()

    def _get_mean_sig(self):
        return int(round(sum(self.sig)/3.0))

    def _retrieve_iw(self):
        while (True):
            try:
                _res = subprocess.check_output(['iw',
                                            self.intf, 'link']).splitlines()
                _res = [el.strip().replace('\t', '') for el in _res]
                _sig_line = _res[[el.startswith('signal:')
                              for el in _res].index(True)]
                _sig = int(_sig_line.split()[1])
                self.sig = self.sig[1:]
                self.sig.append(_sig)
            except ( subprocess.CalledProcessError, ValueError ):
                self.sig = [-200,-200,-200]

            #print self.sig
            time.sleep(SignalMonitor.UPD_INTERV)

    def _reply(self):
        while (True):
            req = self.skt.recv()
            #print req
            self.skt.send(str(self._get_mean_sig()))

if __name__ == '__main__':
    sig_mon = SignalMonitor(INTF)
