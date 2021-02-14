import numpy as np
from scipy.spatial.distance import pdist, squareform

import matplotlib.pyplot as plt
import scipy.integrate as integrate
import matplotlib.animation as animation
from Person import Person
from Disease import Disease
from math import sqrt


class ParticleBox:

    def __init__(self,
                 init_state=[[1, 0, 0, -1],
                             [-0.5, 0.5, 0.5, 0.5],
                             [-0.5, -0.5, -0.5, 0.5]],
                 bounds=[-2, 2, -2, 2],
                 size=0.04,
                 ):
        self.init_state = np.asarray(init_state, dtype=float)
        self.M = np.ones(self.init_state.shape[0])
        self.size = size
        self.state = self.init_state.copy()
        self.time_elapsed = 0
        self.bounds = bounds

    def step(self, dt):
        """step once by dt seconds"""

        self.time_elapsed += dt
        global time,numberDead,numberSusceptible, numberIll,numberInmune
        time = time+1

        if(numberSusceptible<5 or time>5000):
            print(numberSusceptible,time)
            print("Finished: Dead people:" , numberDead,) 
            print("People Inmune" , numberInmune , "in" , time/10 , "days" )
            numberSusceptible=30
            time = 0

        
        # update positions
        self.state[:, :2] += dt * self.state[:, 2:]
        for b in range(30):
            for index in range(30):
                if(index!=b):
                    list_person[b].checkDistantePersons(list_person[index],covid19)
            if(list_person[b].timeIncubated>0):
                if(list_person[b].timeIncubated==covid19.t1):
                    list_person[b].state="infected"
                    print(list_person[b].id , " is now infected ")

                    numberIll=numberIll+1
                    numberSusceptible=numberSusceptible-1

                    list_person[b].timeInfected=1
                    list_person[b].timeIncubated=0
                    self.state[b][2]=0
                    self.state[b][3]=0
                else: list_person[b].timeIncubated=list_person[b].timeIncubated+1
            
            if(list_person[b].timeInfected>0):
                if(list_person[b].timeInfected==covid19.t2):
                    probDead=np.random.random()
                    if(probDead<covid19.mortality):
                        list_person[b].state="dead"
                        print(list_person[b].id , " is now dead ")
                        list_person[b].timeInfected=0
                        self.state[b][2]=0
                        self.state[b][3]=0
                        self.state[b][0]=10
                        self.state[b][1]=10
                        numberDead=numberDead+1
                        numberIll=numberIll-1
                        print("Number dead people:",numberDead)

                    else: 
                        list_person[b].state="immune"
                        print(list_person[b].id , " is now immune ")
                        list_person[b].timeInfected=0
                        numberInmune=numberInmune+1
                        numberIll=numberIll-1
                else: list_person[b].timeInfected=list_person[b].timeInfected+1


            x=self.state[b][0]
            y=self.state[b][1]
            list_person[b].changePosition(x,y)
            

        # find pairs of particles undergoing a collision
        D = squareform(pdist(self.state[:, :2]))
        ind1, ind2 = np.where(D < 2 * self.size)
        unique = (ind1 < ind2)
        ind1 = ind1[unique]
        ind2 = ind2[unique]
        # check for crossing boundary
        crossed_x1 = (self.state[:, 0] < self.bounds[0] + self.size)
        crossed_x2 = (self.state[:, 0] > self.bounds[1] - self.size)
        crossed_y1 = (self.state[:, 1] < self.bounds[2] + self.size)
        crossed_y2 = (self.state[:, 1] > self.bounds[3] - self.size)

        self.state[crossed_x1, 0] = self.bounds[0] + self.size
        self.state[crossed_x2, 0] = self.bounds[1] - self.size

        self.state[crossed_y1, 1] = self.bounds[2] + self.size
        self.state[crossed_y2, 1] = self.bounds[3] - self.size

        self.state[crossed_x1 | crossed_x2, 2] *= -1
        self.state[crossed_y1 | crossed_y2, 3] *= -1


# ------------------------------------------------------------
# set up initial state and creation of objects
np.random.seed(0)
init_state = -0.5 + np.random.random((30, 4))
init_state[:, :2] *= 3.9

# set up the disease
pInfection= 0.3
dInfection = 0.2
t1 = 100
t2 = 200
mortality = 0.3
velocity = 2

covid19 = Disease(pInfection,dInfection,t1,t2,mortality,velocity)

list_person = []

#create people 
for b in range(30):
    
    x=init_state[b][0]
    y=init_state[b][1]
    a = Person(b,x,y)
    list_person.append(a)
#infect 1 person
list_person[0].state="infected"

box = ParticleBox(init_state, size=0.04)
dt = 1. / 30  # 30fps
time = 0
#initData
numberDead = 0
numberIll = 1
numberSusceptible = 29
numberInmune = 0


# ------------------------------------------------------------
# set up figure and animation
fig = plt.figure()
fig.subplots_adjust(left=0, right=1, bottom=0, top=1)
ax = fig.add_subplot(111, aspect='equal', autoscale_on=False,
                     xlim=(-3.2, 3.2), ylim=(-2.4, 2.4))

# particles holds the locations of the people
particles, = ax.plot([], [], 'b.', ms=1)


# rect is the box edge
rect = plt.Rectangle(box.bounds[::2],
                     box.bounds[1] - box.bounds[0],
                     box.bounds[3] - box.bounds[2],
                     ec='none', lw=2, fc='none')
ax.add_patch(rect)


def init():
    global box, rect
    particles.set_data([], [])
    
    rect.set_edgecolor('none')
    return particles, rect


def animate(i):
    global box, rect, dt, ax, fig, time , numberDead
    box.step(dt)

    ms = int(fig.dpi * 2 * box.size * fig.get_figwidth()
             / np.diff(ax.get_xbound())[0])

    # update pieces of the animation
    rect.set_edgecolor('k')
    particles.set_data(box.state[:, 0], box.state[:, 1])
    particles.set_markersize(ms)

    return particles, rect


ani = animation.FuncAnimation(fig, animate, frames=600,
                              interval=10, blit=True, init_func=init)


plt.show()
