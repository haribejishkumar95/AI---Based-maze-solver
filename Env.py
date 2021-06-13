"""
Created on Sat May  2 14:07:56 2020

@author: harib
"""

import kivy
kivy.require('1.0.6') # replace with your current kivy version !

import numpy as np

from kivy.app import App # To create and run an app 
from kivy.uix.label import Label #to print writings using label function
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout # to make the writings float(rotate,turn etc)
from kivy.uix.scatter import Scatter # to move the writings in the screen
from kivy.uix.textinput import TextInput # to input another text
from kivy.uix.boxlayout import BoxLayout # to create a box layout for new text
from kivy.uix.gridlayout import GridLayout
from kivy.config import Config
from kivy.animation import Animation
from kivy.uix.widget import Widget
from kivy.vector import Vector
from kivy.graphics import Rectangle, Color , Line
from kivy.clock import Clock

from AI import Dqn

from kivy.lang import Builder
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty

#Adding this line if we don't want the right click to put a red point
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

last_point_x = 0
last_point_y = 0
first_point_x  = 0
first_point_y = 0
c = 0
n = 0


brain = Dqn(5,3,0.9)
action2rotation = [0,20,-20] 
last_reward = 0 
scores = []

Initial_update = True

def main(instance):
    global Initial_update
    global goal_x
    global goal_y
    goal_x = 0#goal is the last point in the platform
    goal_y = 0
    Initial_update = instance
    

last_distance = 0

class Car_Functions(Widget):
    angle = NumericProperty(0) # initializing the angle of the car (angle between the x-axis of the map and the axis of the car)
    rotation = NumericProperty(0) # initializing the last rotation of the car (after playing the action, the car does a rotation of 0, 20 or -20 degrees)
    velocity_x = NumericProperty(0) # initializing the x-coordinate of the velocity vector
    velocity_y = NumericProperty(0) # initializing the y-coordinate of the velocity vector
    velocity = ReferenceListProperty(velocity_x, velocity_y) # velocity vector
    sensor1_x = NumericProperty(0) # initializing the x-coordinate of the first sensor 
    sensor1_y = NumericProperty(0) # initializing the y-coordinate of the first sensor 
    sensor1 = ReferenceListProperty(sensor1_x, sensor1_y) # first sensor vector
    sensor2_x = NumericProperty(0) # initializing the x-coordinate of the second sensor 
    sensor2_y = NumericProperty(0) # initializing the y-coordinate of the second sensor 
    sensor2 = ReferenceListProperty(sensor2_x, sensor2_y) # second sensor vector
    sensor3_x = NumericProperty(0) # initializing the x-coordinate of the third sensor 
    sensor3_y = NumericProperty(0) # initializing the y-coordinate of the third sensor 
    sensor3 = ReferenceListProperty(sensor3_x, sensor3_y) # third sensor vector
    signal1 = NumericProperty(0) # initializing the signal received by sensor 1
    signal2 = NumericProperty(0) # initializing the signal received by sensor 2
    signal3 = NumericProperty(0) # initializing the signal
   
    def car_movement(self, turn):
        self.pos = Vector(self.velocity) + self.pos
        self.rotation = turn
        self.angle = self.angle + self.rotation 
        self.sensor1 = Vector(30,0).rotate(self.angle) + self.pos
        self.sensor2 = Vector(30,0).rotate((self.angle+30)%360) + self.pos 
        self.sensor3 = Vector(30,0).rotate((self.angle-30)%360) + self.pos 
        self.signal1 = int(np.sum(wall[int(self.sensor1_x)-10:int(self.sensor1_x)+10, int(self.sensor1_y)-10:int(self.sensor1_y)+10]))/400. 
        self.signal2 = int(np.sum(wall[int(self.sensor2_x)-10:int(self.sensor2_x)+10, int(self.sensor2_y)-10:int(self.sensor2_y)+10]))/400. 
        self.signal3 = int(np.sum(wall[int(self.sensor3_x)-10:int(self.sensor3_x)+10, int(self.sensor3_y)-10:int(self.sensor3_y)+10]))/400.  
        
        if self.sensor1_x> width-10 or self.sensor1_x<10 or self.sensor1_y> height-10 or self.sensor1_y<10:
            self.signal1 = 1
        if self.sensor2_x> width-10 or self.sensor2_x<10 or self.sensor2_y> height-10 or self.sensor2_y<10:
            self.signal2 = 1
        if self.sensor3_x> width-10 or self.sensor3_x<10 or self.sensor3_y> height-10 or self.sensor3_y<10:
            self.signal3 = 1   
        
            
class Right(Widget):
    pass

class Left(Widget):
    pass

class Front(Widget):
    pass

          
class Platform(Widget):
    car= ObjectProperty(None)
    d1= ObjectProperty(None)
    d2= ObjectProperty(None)
    d3= ObjectProperty(None)
    
    def start(self):
        self.car.center = self.center #problem
        self.car.velocity = Vector(3,0) #problem
        #print(self.car.center)
        
               
    def update(self, dt):
        global height
        global width
        global brain
        global last_signal
        global last_distance
        global goal_x
        global goal_y
        global last_reward
        global c
        global wall
        global Initial_update
        global n
        
        height= self.height
        width = self.width
        self.l = Label(text='WINNER!',font_size = 50,pos=(350,500))
        #FINDING THE DESTINATION OF THE ROBOT USING THE LAST POINT ON THE ENVIRONMENT
        if c == 0:
            if n == 0:
                wall = np.zeros((width,height), dtype = int)
                
            des1 = np.sqrt((last_point_x - width)**2 + (last_point_y - height)**2)  
            des2 = np.sqrt((last_point_x - width)**2 + (last_point_y - 0)**2) 
            des3 = np.sqrt((last_point_x - 0)**2 + (last_point_y - height)**2) 
            des4 = np.sqrt((last_point_x - 0)**2 + (last_point_y - 0)**2) 
            
            destination = min(des1,des2,des3,des4)
            
            if destination == des1:
                goal_x = width - 40#goal is the last point in the platform
                goal_y = height - 40 
                
            if destination == des2:
                goal_x = width - 40#goal is the last point in the platform
                goal_y = 0 + 40 
                
                
            if destination == des3:
                goal_x = 0 + 40 #goal is the last point in the platform
                goal_y = height - 40 
                
                
            if destination == des4:
                goal_x = 0 + 40 #goal is the last point in the platform
                goal_y = 0 + 40 
                
            
            
        if Initial_update == False:
            
            if c > 1:
                self.start()
                c = c - 2 #changed, before it was 1
                #self.remove_widget(self.l)
                
              
            x = goal_x - self.car.x
            y = goal_y - self.car.y
            #print(x)
            orientation = Vector(*self.car.velocity).angle((x,y))/180. # direction of the car with respect to the goal (if the car is heading perfectly towards the goal, then orientation = 0)
            last_signal = [self.car.signal1, self.car.signal2, self.car.signal3, orientation, -orientation] # our input state vector, composed of the three signals received by the three sensors, plus the orientation and -orientation
            action = brain.update(last_reward, last_signal) # playing the action from our ai (the object brain of the dqn class)
            scores.append(brain.score()) # appending the score (mean of the last 100 rewards to the reward window)
            rotation = action2rotation[action] # converting the action played (0, 1 or 2) into the rotation angle (0°, 20° or -20°)
            self.car.car_movement(rotation) # moving the car according to this last rotation angle
            distance = np.sqrt((self.car.x - goal_x)**2 + (self.car.y - goal_y)**2) # getting the new distance between the car and the goal right after the car moved
            self.d1.pos = self.car.sensor1 # updating the position of the first sensor (ball1) right after the car moved
            self.d2.pos = self.car.sensor2 # updating the position of the second sensor (ball2) right after the car moved
            self.d3.pos = self.car.sensor3 # updating the position of the third sensor (ball3) right after the car moved
       
            
            if wall[int(self.car.x),int(self.car.y)] > 0: # if the car is on the sand
                self.car.velocity = Vector(1, 0).rotate(self.car.angle) # it is slowed down (speed = 1)
                last_reward = -10# and reward = -10
            else: # otherwise       
                self.car.velocity = Vector(3, 0).rotate(self.car.angle) # problem
                last_reward = -0.2 # and it gets bad reward (-0.2)
                if distance < last_distance: # however if it getting close to the goal
                    last_reward = 0.1 # it still gets slightly positive reward 0.1
                        
                if (self.car.x != 0 or self.car.x !=width) and self.car.y > height-10:#if car is on the top edge of the screen                    
                    self.car.y = height - 10
                    last_reward = -10
                if (self.car.x != 0 or self.car.x !=width) and self.car.y < 10:#if car is on the bottom edge of the screen
                    self.car.y =  10
                    last_reward = -10
                if (self.car.y != 0 or self.car.y !=height) and self.car.x > width - 10:#if car is on the left edge of the screen
                    self.car.x = width - 10
                    last_reward = -10
                if (self.car.y != 0 or self.car.y !=height) and self.car.x < 10:#if car is on the right edge of the screen
                    self.car.x =10
                    last_reward = -10
                    
            if int(distance) < 6:
                self.car.velocity = Vector(0, 0)
                print("Winner")
                last_reward = 1
                #Initial_update = True
                #if c > 1:
                return self.add_widget(self.l)
                
            last_distance = distance
            
            
                
              
            
class MyPaintWidget(Widget):
      
      def on_touch_down(self, touch):
        global first_point_x, first_point_y, n, density, length
        with self.canvas:
            Color(1, 1, 0)
            d = 10
            touch.ud['line'] = Line(points=(touch.x, touch.y), width = d/1.5)
            first_point_x = int(touch.x)
            first_point_y = int(touch.y)
            #n = 0
            '''
            length = 0
            density = 0
            '''
            wall[int(touch.x),int(touch.y)] = 1
           #wall.item(int(touch.x),int(touch.y)) 
           #print(wall.item(int(touch.x),int(touch.y)))
            
      def on_touch_move(self, touch):
        global last_point_x, last_point_y, n, length, density
        
        touch.ud['line'].points += [touch.x, touch.y]
        x = int(touch.x)
        y = int(touch.y)
        wall[int(touch.x) - 10:int(touch.x) + 10,int(touch.y) - 10:int(touch.y) + 10]= 1
        last_point_x = x
        last_point_y = y
        n+=1
        #print(wall.item(int(touch.x),int(touch.y)))
  
class Car_ObjectApp(App): 
    
    def build(self):
        
        parent = Platform()
        
        #parent.start()
        Clock.schedule_interval(parent.update, 1.0 / 60.0)
        self.painter = MyPaintWidget()
        
        self.b1= Button(text='Load',font_size=10,pos=(0,0),size = (50,50))
        self.b1.bind(on_release= self.loading)
        self.b2= Button(text='Save',font_size=10,pos=(50,0),size = (50,50))
        self.b2.bind(on_release= self.saving)
        self.b3= Button(text='clear',font_size=10,pos=(100,0),size = (50,50))
        self.b3.bind(on_release= self.clear_canvas)#included a function for clear
        self.b4= Button(text='Start',font_size=10,pos=(150,0),size = (50,50))
        self.b4.bind(on_release= self.starting )
        parent.add_widget(self.painter)#adding the paint widget to the parent class
        parent.add_widget(self.b1)
        parent.add_widget(self.b2)
        parent.add_widget(self.b3)
        parent.add_widget(self.b4)
        
        #Builder.load_string(kv) 
        
        return parent
     
    def loading(self, instance):
            print("Loading")
            brain.load()
            #self.main = main(True) 
            
            
    def saving(self, instance):        
            print("Saving")
            brain.save()
            
        #if self.b3.last_touch :
            #def clear_canvas(self, obj):
            #self.painter.canvas.clear()
            #self.b3.last_touch= 0
            
    def starting(self, instance):
        global c
        print("Starting Maze-Solver")
        self.main = main(False) 
        #print(type(wall))
        #print(wall)
        c = 0
        c = c + 2
        
            
      
    def clear_canvas(self, obj):
        self.painter.canvas.clear()   
        
    
if __name__ == '__main__':
    Car_ObjectApp().run()