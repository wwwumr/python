# -*- coding: cp936 -*-
#������
#���ڼ���㡢�߶Ρ����ߡ�ֱ��֮��ĸ��ֹ�ϵ
#�Լ�ȷ���ϡ�����ֱ�߷��̡���������ʽ�Ȼ�������

from point import Point
from functools import wraps
import sys

#�����Ƿ��ڶ������
def checkPointPoly(point,poly):
    flag = True
    centerPoint = poly.centerPoint
    lines = poly.lines
    for line in lines:
        product = f(line, point) * f(line, centerPoint)
        if product < 0:
            flag = False #�ڶ������
    return flag

#�����Ƿ���һ���߶���������չR�γɵľ�����
def checkPointSegment(l,p1,p2,r,q):
    dC = r*(l[0]**2+l[1]**2)**0.5
    l1 = (l[0],l[1],l[2]-dC)
    l2 = (l[0],l[1],l[2]+dC)
    if checkSign(f(l1,q),f(l2,q)):
        return False
    return True

#����͹�����ĳ�ߵĴ�ֱ���ķ���
def getPerpendicularVector(l,c):
    if f(l,c) > 0:
        return (l[0],l[1])
    return (-l[0],-l[1])

#����ĳ�㳯ĳһ�����ƶ�һ�ξ���õ��ĵ�
def getMovePoint(p,v,d=0):
    if d: #�����˾��룬�������ƶ�
        m = (v[0]**2+v[1]**2)**0.5
        return Point(p.x+v[0]/m*d,p.y+v[1]/m*d)
    return Point(p.x+v[0],p.y+v[1])

#��������߶��Ƿ��ཻ
def checkSegmentSegment(l1,p1,q1,l2,p2,q2):
    if checkSign(f(l1,p2),f(l1,q2)) or checkSign(f(l2,p1),f(l2,q1)):
        return False
    return True

#ȷ��ֱ�߷���
def determineLinearEquation(p1, p2):
    x1, y1, x2, y2 = p1.x, p1.y, p2.x, p2.y
    if x1 == x2:
        if y1 == y2:
            sys.stderr.write("Error: determineLinearEquation(p1, p2) gets two same points: (%s, %s).\n"\
                             %(x1, y1))
            return None
        A, B = 1, 0
    else:
        A, B = y1-y2, x2-x1
    C = -A*x1-B*y1
    return (A,B,C)

#����ֱ�߷���
def f(coe, point):
    return coe[0]*point.x + coe[1]*point.y + coe[2]

#��ֱ�߽���
def getIntersection(l1, l2):
    D = float(l1[0]*l2[1] - l2[0]*l1[1])
    if D == 0:
        sys.stderr.write("Error: getIntersection(l1, l2) gets two same line: %sx + %sy = %s"\
                         %l1)
        return None
    Dx = l1[1]*l2[2] - l2[1]*l1[2]
    Dy = l1[2]*l2[0] - l2[2]*l1[0]
    return Point(Dx/D, Dy/D)

#����㵽ֱ�߾���ƽ��
def getDistanceSquare(l,p):
    return f(l,p)**2/(l[0]**2+l[1]**2)

#��������ʽ
#|p1.x p1.y 1|
#|p2.x p2.y 1|
#|p3.x p3.y 1|
def calculateDeterminant(p1, p2, p3):
    return p1.x*(p2.y-p3.y) - p1.y*(p2.x-p3.x) + p2.x*p3.y - p3.x*p2.y

#����һ������ʽ
def determinant(D):
    n = len(D)
    if n == 1: return D[0][0]
    return sum((-1)**i*D[0][i]*determinant([r[:i]+r[i+1:] for r in D[1:]]) \
               for i in range(n))

#����ķ����������Է���η�����
def solveEquationSet(A):
    D = [r[:-1] for r in A]
    _D = determinant(D)
    if _D == 0:
        sys.stderr.write("Error: The equation set has no solutions")
        return
    solutions = []
    for i in range(len(A)):
        for j in range(len(A)):
            D[j][i] = A[j][-1]
        _Dx = determinant(D)
        solutions.append(float(_Dx)/_D)
        for j in range(len(A)):
            D[j][i] = A[j][i]
    return solutions

#�ж��Ƿ�ͬ�Ż�Ϊ��
def checkSign(n1,n2):
    if n1 >= 0 and n2 >= 0 or n1 <= 0 and n2 <= 0:
        return True
    return False
