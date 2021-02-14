from math import sqrt
import numpy as np

class Person():

    def __init__(self,index,x,y):
        self.id = index
        self.x = x
        self.y = y
        self.state="susceptible"
        self.timeIncubated=0
        self.timeInfected=0


    def changePosition(self,x,y):
        self.x=x
        self.y=y

    def checkDistantePersons(self,person,disease):
        distance = abs(sqrt((self.x - person.x)**2 + (self.y-person.y)**2))
        if(distance<disease.dInfection and self.state=="infected"):
            self.infect(person,disease)

    def infect(self,person,disease):
        prob = np.random.random()
        if(prob<disease.pInfection/10 and person.state == "susceptible"):
            person.timeIncubated=1
            print(self.id , "infected " ,person.id, "now incubating")
            
