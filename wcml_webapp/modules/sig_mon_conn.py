#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *
import zmq

ctx = zmq.Context()
skt = ctx.socket(zmq.REQ)
skt.connect("tcp://localhost:55555")

def get_signal():
    skt.send("REQ.SIG")
    resp = skt.recv()
    return str(resp)

if __name__ == "__main__":
    get_signal()
