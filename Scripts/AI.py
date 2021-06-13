
# Importing the python libraries

import numpy as np
import random
import os
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torch.autograd as autograd
from torch.autograd import Variable

# Creating the architecture of the Neural Network

class Network(nn.Module):
    
    def __init__(self, input_size,output_size ):
        super(Network,self). __init__()
        self.input_size = input_size
        self.output_size = output_size
        self.fc1 = nn.Linear(input_size, 50)
        self.fc2 = nn.Linear(50, output_size)
    
    def forward(self, state):
        x = F.relu(self.fc1(state))
        q_values = self.fc2(x)
        return q_values

# Implementing Experience Replay

class Experience_Replay(object):
    
    def __init__(self, capacity):
        self.capacity = capacity
        self.memory = []
    
    def push(self, event):
        self.memory.append(event)
        if len(self.memory) > self.capacity:
            del self.memory[0]
    
    def sample(self, batch_size):
        samples = random.sample(self.memory, batch_size)
        return samples

# Implementing Deep Q Learning

class Dqn(object):
    
    def __init__(self, inputs, actions, gamma):
        self.gamma = gamma
        self.reward_window = []
        self.model = Network(inputs, actions)
        self.memory = Experience_Replay(100000)
        self.optimizer = optim.Adam(self.model.parameters(), lr = 0.001)
        self.last_state = torch.Tensor(inputs).unsqueeze(0)
        self.last_action = 0
        self.last_reward = 0 
    
    def select_action(self, state):
        probs = F.softmax(self.model(state), dim=0)# T=100
        action = probs.multinomial(1)
        return action.data[0,0]
    
    def training(self, current_state, next_state, reward, action):
        outputs = self.model(current_state)#.gather(1, batch_action.unsqueeze(1)).squeeze(1)
        next_outputs = self.model(next_state)#.detach().max(1)[0]   
        target_q_values = self.gamma*next_outputs + reward
        td_loss = F.smooth_l1_loss(outputs, target_q_values)
        self.optimizer.zero_grad()
        td_loss.backward()
        self.optimizer.step()
    
    def update(self, last_reward, new_signal):
        new_state = torch.Tensor(new_signal).float().unsqueeze(0)
        self.memory.push(self.last_state, new_state,torch.Tensor(self.last_action).float().unsqueeze(0),torch.Tensor(self.last_reward).float().unsqueeze(0))
        action = self.select_action(new_state)
        if len(self.memory.memory) > 100:
           current_state, next_state, reward, action = self.memory.samples(100)
           self.training(current_state, next_state, reward, action)
        self.last_action = action
        self.last_state = new_state
        self.last_reward = last_reward
        self.reward_window.append(last_reward)
        if len(self.reward_window) > 1000:
            del self.reward_window[0]
        return action
    
    def score(self):
        return sum(self.reward_window)/(len(self.reward_window)+1.)
    
    def save(self):
        torch.save({'state_dict': self.model.state_dict(),
                    'optimizer' : self.optimizer.state_dict(),
                   }, 'last_brain.pth')
    
    def load(self):
        if os.path.isfile('last_brain.pth'):
            print("=> loading checkpoint... ")
            checkpoint = torch.load('last_brain.pth')
            self.model.load_state_dict(checkpoint['state_dict'])
            self.optimizer.load_state_dict(checkpoint['optimizer'])
            self.model.eval()
            print("done !")
            
        else:
            print("no checkpoint found...")