# -*- coding: cp936 -*-
#���
#ֱ�ߡ����ߡ��߶���Ԫ���ʾ�����ڱ���ⷶΧ֮��
#Ϊ���⵼��ѭ�������಻�ڱ������

import math
from geometry import *

class Poly:
    def __init__(self, args, reverse=False):
        if reverse:
            self.vertices = args[::-1]
        else:
            self.vertices = args[:]
        self.n = len(self.vertices)
        self.lines = []
        self.init()
    def init(self):
        self.endpoints = self.vertices[:]
        self.endpoints.append(self.endpoints[0])
        #���㼸�����ģ�˳�������߷���
        sumX = sumY = 0
        for i in range(self.n):
            v = self.vertices[i]
            v.poly =  self
            v.id = i
            sumX += v.x
            sumY += v.y
            self.lines.append(determineLinearEquation(self.endpoints[i],
                                                      self.endpoints[i+1]))
        self.centerPoint = Point(sumX/self.n, sumY/self.n)
    def getOut(self, i): #����
        if i == self.n-1:
            return 0
        return i+1
    def getIn(self, i): #���
        if i == 0:
            return self.n-1
        return i-1
