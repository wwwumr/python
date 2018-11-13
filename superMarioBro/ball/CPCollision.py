# -*- coding: cp936 -*-
from point import Point
from element import Poly
from geometry import *

def CPCollision(c,g):
    m = Point(c.x,c.y) #����
    #�����жϣ�����㲻����չ������ڣ�ֱ�ӷ���False
    if not checkPointPoly(m,g.epoly):
        return False
    #��֪������չ������ڣ�������������Ƿ�����չ�߶���
    p = g.poly #ͼ��g�Ķ����
    n = Point(c.x-c.vx,c.y-c.vy) #��һ��ʱ�̵�����
    v = determineLinearEquation(m,n) #�ٶ�ֱ��
    for i in range(p.n):
        p1,p2 = p.endpoints[i],p.endpoints[i+1]
        l = p.lines[i]
        if checkPointSegment(l,p1,p2,c.r,m):
            #��֪������չ�߶��ڣ�����������˶��켣�Ƿ����߶��ཻ
            mm = getMovePoint(m,getPerpendicularVector(l,p.centerPoint),c.r)
            nm = getMovePoint(mm,(-c.vx,-c.vy))
            if checkSegmentSegment(determineLinearEquation(mm,nm),mm,nm,l,p1,p2):
                #��֪��ײ���������߶Σ�����ı�����ٶ�
                unit = (l[0]**2+l[1]**2)**0.5
                cos = l[0]/unit
                sin = l[1]/unit
                c.vn = c.vx*cos+c.vy*sin
                c.vp = -c.vx*sin+c.vy*cos
                c.vn = -c.vn
                c.vx = c.vn*cos-c.vp*sin
                c.vy = c.vn*sin+c.vp*cos
                return True
            #������ײ���������߶εĶ˵㣬�������ǲ��������ŵ���������
    #��û������ĳһ�߶Σ����������Ƿ������ĳһ��
    for q in p.vertices:
        if m-q < c.r:
            #��֪����������һ�㣬����ı�����ٶ�
            #�ⷽ���飬��������ײ�ĽǶȣ���t��һ�����������ã�
            #      A    B    t
            #~   | r    0    vx  q.x-c.x|
            #A = | 0    r    vy  q.y-c.y|
            #    |r*vx r*vy  0    v*proj|
            _v = (c.vx**2+c.vy**2)*0.5 #�ٶȵ�ģ
            proj = (c.r**2-getDistanceSquare(v,q))**0.5 #�뾶���ٶȷ����ϵ�ͶӰ
            A,B,t = solveEquationSet([[c.r,0,c.vx,q.x-c.x],
                                      [0,c.r,c.vy,q.y-c.y],
                                      [c.vx*c.r,c.vy*c.r,0,_v*proj]])
            unit = (A**2+B**2)**0.5
            #print unit #unitӦ�ýӽ���1
            cos = A/unit
            sin = B/unit
            c.vn = c.vx*cos+c.vy*sin
            c.vp = -c.vx*sin+c.vy*cos
            c.vn = -c.vn
            c.vx = c.vn*cos-c.vp*sin
            c.vy = c.vn*sin+c.vp*cos
            return True
        
    #���ʲô��û��������ʵ������Ѿ��ܵ�������
    return False
