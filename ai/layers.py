"""Local neural-network layers and activation helpers for Rubiks AI."""

import math

import numpy as np


class Affine:
    def __init__(self,ips,ops):
        self.W = np.random.randn(ops,ips).astype('f') / math.sqrt(ips / 2)
        self.B = np.random.randn(ops).astype('f')
        self.B[:] = 0
        self.dW = np.zeros_like(self.W,dtype = 'f')
        self.dB = np.zeros_like(self.B,dtype = 'f')
        self.x = np.empty((0,0),dtype = 'f')
        self.dx = np.empty((0,0),dtype = 'f')
        self.out = np.empty((0,0),dtype = 'f')


    def forward(self,x):
        self.x = x
        self.out = self.W @ x
        self.out += self.B.reshape(-1,1)

        return self.out

    def backward(self,dO):
        self.dx = self.W.T @ dO
        self.dW = dO @ self.x.T
        self.dB = np.sum(dO,axis = 1)

        return self.dx

def relu(x):
    y = x.copy()
    y[y<0] = 0

    return y

class ReLU:
    def __init__(self):
        self.out = np.empty((0,0),dtype = 'f')

    def forward(self,x):
        self.out = relu(x)
        return self.out

    def backward(self,dO):
        dO = dO * np.sign(self.out)
        return dO

def huber(x):
    y = x ** 2 / 2
    y[y>0.5] = abs(x[y>0.5]) - 0.5

    return y


def hard_sigmoid(x):
    y = x.copy()
    y[y > 1] = 1
    y[y < -1] = -1

    return y

class Hard_Sigmoid:
    def __init__(self):
        self.out = np.empty((0,0),dtype = 'f')

    def forward(self,x):
        self.out = hard_sigmoid(x)
        return self.out

    def backward(self,dO):
        dO[self.out == 1] = 0
        dO[self.out == -1] = 0
        return dO

def sigmoid(x):
    return np.where(x > 40,1.0,np.exp(x) / (1 + np.exp(x)))

class Sigmoid:
    def __init__(self):
        self.out = np.empty((0,0),dtype = 'f')

    def forward(self,x):
        self.out = sigmoid(x)
        return self.out

    def backward(self,dO):
        dO *= self.out * (1.0 - self.out)
        return dO


class Batch_Normalization:
    def __init__(self,size):
        self.size = size
        self.m = np.zeros(size,dtype = 'f')
        self.s = np.ones(size,dtype = 'f')
        self.g = np.random.uniform(0.5,2,(size,)).astype('f')
        self.b = np.random.uniform(-0.5,0.5,(size,)).astype('f')
        self.dg = None
        self.db = None
        self.m_batch = np.zeros(size,dtype = 'f')
        self.s_batch = np.zeros(size,dtype = 'f')
        self.x_bar = None

        self.N = 0

        self.train_m = None
        self.train_s = None
        self.x = None
        self.y = None

    def forward(self,x,loss = False):
        if loss:
            self.x = x
            self.train_m = np.average(x,axis = 1)
            self.train_s = np.std(x,axis = 1)
            self.x_bar = (x - self.train_m.reshape(-1,1)) / (self.train_s.reshape(-1,1) + 1.0e-7)
            self.y = self.g.reshape(-1,1) * self.x_bar + self.b.reshape(-1,1)

            self.m_batch += self.train_m
            self.s_batch += self.train_s
            self.N += 1

            return self.y

        x_bar = (x - self.m.reshape(-1,1)) / (self.s.reshape(-1,1) + 1.0e-7)
        return self.g.reshape(-1,1) * x_bar + self.b.reshape(-1,1)

    def backward(self,dO):
        self.dg = np.sum(self.x_bar * dO,axis = 1)
        self.db = np.sum(dO,axis = 1)

        return self.g.reshape(-1,1) / (self.train_s.reshape(-1,1) + 1.0e-7) * (dO- (self.db.reshape(-1,1) + self.x_bar * self.dg.reshape(-1,1)) / self.x.shape[1])

    def set_ms(self):
        self.m[:] = self.m_batch / self.N
        self.s[:] = self.s_batch / self.N

        self.N = 0
        self.m_batch[:] = 0
        self.s_batch[:] = 0
