#!/usr/bin/python

import sys
import argparse
import collections
import numpy
import matplotlib.pyplot as plt
import matplotlib.animation as animation

parser = argparse.ArgumentParser(description='Plots data streaming from STDIN in realtime or statically')
parser.add_argument('--xlen', default=100, type=int)
parser.add_argument('--stream', default=None, type=float)
parser.add_argument('--xmin', default=None, type=float)
parser.add_argument('--xmax', default=None, type=float)
args = parser.parse_args()

#Read a single line from stdin and determine number of streams
S = sys.stdin.readline()
S_F = [float(val) for val in S.strip().split()]
n_streams = len(S_F)

#Create the figure and axes
fig = plt.figure()
ax = plt.axes(xlim=(0, args.xlen), ylim=(numpy.min(S_F)*1.1, numpy.max(S_F)*1.1))
ax.grid(True)

#Variable to hold the lines being plotted
lines = []
#Variables to hold the line data. Use a ring buffer
#So that more data than needed is not stored.
x_buf = collections.deque(maxlen=args.xlen)
y_buf = collections.deque(maxlen=args.xlen)
x = []
y = []

#Plot as many lines as there are streams
for index in range(n_streams):
    lobj, = ax.plot([],[], animated=True, label=str(index))
    lines.append(lobj)

#Display the legend
ax.legend()

def data_gen_rand():
    ctr = 0
    while True:
        ctr += 1
        yield [numpy.random.rand(), ctr]

def data_gen_ser():
    ctr = 0.0
    while True:
        S = sys.stdin.readline()
        S_F = [float(val) for val in S.strip().split()]
        ctr += 1.0
        S_F.append(ctr)
        yield(S_F)

def init():
    for line in lines:
        line.set_data([],[])
    return tuple(lines)

def animate(data):
    #Get the data and convert to list
    x_buf.append(data[-1])
    y_buf.append(data[:-1])

    #Update the data in the lines
    for lnum, line in enumerate(lines):
        line.set_data(x_buf, [row[lnum] for row in y_buf])
    
    #Update the axes ranges
    ax.set_xlim(max([0,max(x_buf)-args.xlen+1]), max(max(x_buf), args.xlen))
    ax.set_ylim(numpy.min(y_buf)*1.1, numpy.max(y_buf)*1.1)
    ax.figure.canvas.draw()

    return tuple(lines)

anim = animation.FuncAnimation(fig, animate, init_func=init,
                               frames=data_gen_ser, interval=0, blit=True)

plt.show()