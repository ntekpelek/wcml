#! /usr/bin/env python
import zmq

ctx = zmq.Context()
skt = ctx.socket(zmq.REQ)
skt.connect("tcp://127.0.0.1:55555")
skt.send("REQ.SIG")
resp = skt.recv()
print resp
