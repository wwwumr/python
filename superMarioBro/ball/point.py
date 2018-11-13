# -*- coding: cp936 -*-
#Point�࣬������Ϊ��
#1 ��ͨ���ڼ���ĵ�
#2 ������а���ʱ�롢��͹�Ե����Եĵ�
#3 ·�������㷨�еĽڵ�
class Point:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.parent = self.poly = None
        self.clock = self.id = 0
        self.concave = self.skip = False

    def toTuple(self):
        return (self.x, self.y)
        
    #���������
    #
    #p1==p2�����ж������Ƿ���ͬ
    #�˷������غ�����in��list�����ú���delete()Ҳ��Ӱ��
    def __eq__(self, p):
        if self.x == p.x and self.y == p.y:
            return True
        return False
    #p1!=p2�������෴
    def __ne__(self, p):
        if p and self.x == p.x and self.y == p.y:
            return False
        return True

    #p1-p2���ڼ�����������
    def __sub__(self, p):
        return ((self.x-p.x)**2 + (self.y-p.y)**2) ** 0.5
