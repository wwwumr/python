from Tkinter import*
from time import*
from random import*
import os
import sys
import winsound,threading



def PlaySound(filename):
    thread = threading.Thread(target=winsound.PlaySound,
                              args=(filename,
                                    winsound.SND_FILENAME|winsound.SND_ASYNC))
    thread.setDaemon(True)
    thread.start()
    
global runmusic
runmusic = "./gamesound/run.wav"
global victorymusic
victorymusic = "./gamesound/victory.wav"
global defeat
defeat = "./gamesound/defeat.wav"
    
class thing:
    def __init__(self,x,y,vx,vy,h):
        self.x=x
        self.y=y
        self.vx=vx
        self.vy=vy
        self.h=h
    def renew(self,t0):
        self.x=self.x+t0*self.vx
        self.y=self.y+t0*self.vy
        if self.y>=475 or self.y<=25:
            self.vy=-self.vy
        if self.x<=-10:
            self.x,self.y=825,50*randrange(11)
            self.vx,self.vy=0,0
        app.c.coords(self.h,self.x,self.y)
    def change(self,t0):
        self.x=self.x+t0*self.vx
        self.y=self.y+t0*self.vy
        if self.y>=480 or self.y<=20:
            self.vy=-self.vy
        if self.x<=10 or self.x>=790:
            self.vx=-self.vx
        self.vx,self.vy=0.8*self.vx,0.8*self.vy
        app.c.coords(app.human1,self.x,self.y)
        app.c.coords(app.human21,self.x,self.y)
    def prop(self,u):
        if ((u.x-self.x)**2+(u.y-self.y)**2)<=1245:
            self.x=825
            self.y=50
            app.c.coords(self.h,self.x,self.y)
    def showUp(self):
        self.x,self.y=randrange(25,775),randrange(25,475)
        app.c.coords(self.h,self.x,self.y)



class App:
    def __init__(self):
        self.root=Tk()
        self.w1 = unicode('天天酷跑','gb2312')
        self.root.title(self.w1)
        self.c=Canvas(self.root,height=490,width=800,bg='white')
        self.c1=Canvas(self.root,height=427,width=800,bg='white')
        self.c2=Canvas(self.root,height=340,width=550,bg='white')
        self.c3=Canvas(self.root,height=450,width=800,bg='white')
        self.c1.pack()
        self.pict1=PhotoImage(file="./gamepic/beijing1.gif")
        self.pict2=PhotoImage(file="./gamepic/beijing2.gif")
        self.pict3=PhotoImage(file="./gamepic/shengli.gif")
        self.pict4=PhotoImage(file="./gamepic/shibai.gif")
        self.pic1 = PhotoImage(file ="./gamepic/stage.gif")
        self.w2 = unicode('开始','gb2312')
        self.w3 = unicode('游戏说明','gb2312')
        self.w4 = unicode('关闭','gb2312')
        self.but1=Button(self.c1,text=self.w2,relief = FLAT,command = start,bg = 'orange')
        self.but2=Button(self.c1,text=self.w3,relief = FLAT,command = text,bg = 'red')
        self.but3=Button(self.c1,text=self.w4,relief = FLAT,command = close,bg = 'yellow')
        self.but4=Button(self.c2,text=self.w4,relief = FLAT,command = back,bg = 'yellow')
        self.but5=Button(self.c3,text=self.w4,relief = FLAT,command = close,bg = 'gray')
        self.but1.place(relx=0.1,rely=0.7,anchor=S)
        self.but2.place(relx=0.1,rely=0.8,anchor=S)
        self.but3.place(relx=0.1,rely=0.9,anchor=S)
        self.c.create_image(0,0,image =self.pic1)
        self.c1.create_image(0,0,image = self.pict1,anchor='nw')
        self.c2.create_image(275,170,image = self.pict2)
        self.flag=0
        self.accelerate=50
        self.score=0
        self.life=3
        self.t=0
        self.t0=0.01
        self.speed=100
        self.c.bind('<KeyPress>',updown)
        self.c.bind('<KeyRelease>',updownend)
        self.lab1=Label(self.root,text='0')
        self.lab2=Label(self.root,text='0')
        self.lab3=Label(self.root,text='0')
        self.lab4=Label(self.c3,text='0',fg='red',bg='white',width=10)
        self.lab5=Label(self.c3,text='0',fg='red',bg='white',width=10)
        self.pic3 = PhotoImage(file ="./gamepic/monster1.gif")
        self.pic4 = PhotoImage(file ="./gamepic/monster2.gif")
        self.pic5 = PhotoImage(file ="./gamepic/tp.gif")
        self.a1=self.c.create_image(800,50,image = self.pic3)
        self.a2=self.c.create_image(800,50,image = self.pic3)
        self.a3=self.c.create_image(800,50,image = self.pic3)
        self.a4=self.c.create_image(800,50,image = self.pic3)
        self.b1=self.c.create_image(800,50,image = self.pic4)
        self.b2=self.c.create_image(800,50,image = self.pic4)
        self.b3=self.c.create_image(800,50,image = self.pic4)
        self.d1=self.c.create_image(800,50,image = self.pic5)
        self.d2=self.c.create_image(800,50,image = self.pic5)
        self.pic2 = PhotoImage(file ="./gamepic/man1.gif")
        self.pic21 = PhotoImage(file ="./gamepic/man2.gif")
        self.human1=self.c.create_image(50,250,image = self.pic2)
        self.human21=self.c.create_image(50,250,image = self.pic21)
        self.pic6 = PhotoImage(file ="./gamepic/shield.gif")
        self.shield=self.c.create_image(850,50,image = self.pic6)
        self.pic7 = PhotoImage(file ="./gamepic/rocket.gif")
        self.rocket=self.c.create_image(850,50,image = self.pic7)
        self.pic8 = PhotoImage(file ="./gamepic/magnet.gif")
        self.magnet=self.c.create_image(850,50,image = self.pic8)
        self.pic9 = PhotoImage(file ="./gamepic/coin.gif")
        self.coin=self.c.create_image(850,50,image = self.pic9)
        self.pic10 = PhotoImage(file ="./gamepic/coins.gif")
        self.coins=self.c.create_image(850,50,image = self.pic10)
        self.pic11 = PhotoImage(file ="./gamepic/diamond.gif")
        self.diamond=self.c.create_image(850,50,image = self.pic11)
    def loop(self):
        while not self.flag==1:
            if self.flag==0:
                self.c1.update()
            elif self.flag==2:
                self.c2.update()
            sleep(0.1)
        main()
def start():
    app.c1.pack_forget()
    app.but1.place_forget()
    app.but2.place_forget()
    app.but3.place_forget()
    app.c.grid(row=1,columnspan=3)
    app.c.focus_set()
    app.lab1.grid(row=0,column=0)
    app.lab2.grid(row=0,column=1)
    app.lab3.grid(row=0,column=2)
    app.flag=1
    PlaySound(runmusic)
    
def text():
    app.c1.pack_forget()
    app.but1.place_forget()
    app.but2.place_forget()
    app.but3.place_forget()
    app.c2.pack()
    app.but4.place(relx=0.8,rely=0.95,anchor=S)
    app.flag=2
def back():
    app.c2.pack_forget()
    app.but4.place_forget()
    app.c1.pack()
    app.but1.place(relx=0.1,rely=0.7,anchor=S)
    app.but2.place(relx=0.1,rely=0.8,anchor=S)
    app.but3.place(relx=0.1,rely=0.9,anchor=S)
def close():
    os._exit(1)
#'a' is an obstacle ,'d' is a door
#the cases when you lose
def over(u,v,t,flag,flag0,t2):
    if ((u.x-v.x)**2+(u.y-v.y)**2)<=1245 and t-flag>=0.7:
        app.life=app.life-1
        flag=t
    if app.life <= 0:
        if flag0==0:
            t2=t
        flag0=1
        app.c.grid_forget()
        app.lab1.grid_forget()
        app.lab2.grid_forget()
        app.lab3.grid_forget()
        app.c3.pack()
        app.c3.create_image(400,230,image = app.pict4)
        app.lab4['text']=str(t2)
        app.lab5['text']=str(app.score)
        app.lab4.place(relx=0.21,rely=0.8,anchor=S)
        app.lab5.place(relx=0.21,rely=0.91,anchor=S)
        app.but5.place(relx=0.5,rely=0.85,anchor=S)
    return flag,t2,flag0
    
# the act of human
lr=ud=0
def updown(event):
    global lr,ud
    if event.keysym=='Right': lr=1
    elif event.keysym=='Left': lr=-1
    elif event.keysym=='Up': ud=1
    elif event.keysym=='Down':ud=-1
def updownend(event):
    global lr,ud
    if event.keysym=='Right' or event.keysym=='Left': lr=0
    elif event.keysym=='Up' or event.keysym=='Down': ud=0
def updownupdate():
    if lr==1 and human.x<=790:
        if human.vx<=50:
            human.vx=50
        human.vx=human.vx+app.accelerate
    elif lr==-1 and human.x>=10:
        if human.vx>=-50:
            human.vx=-50
        human.vx=human.vx-app.accelerate
    if ud==1 and human.y>=10:
        if human.vy>=-50:
            human.vy=-50
        human.vy=human.vy-app.accelerate
    elif ud==-1 and human.y<=490:
        if human.vy<=50:
            human.vy=50
        human.vy=human.vy+app.accelerate
#the act of doors
def convey(u,v,z,flag1,t):
    if ((u.x-v.x)**2+(u.y-v.y)**2)<=1245 and (t-flag1)>=0.7:
        u.y=z.y
        app.c.coords(u.h,u.x,u.y)
        flag1=t
    return flag1
# the act of shield
def myshield(u,v):
    if (u.x-v.x)**2+(u.y-v.y)**2<=1245:
        app.life=app.life+1
# the act of magnet
def mymagnet(u,v,t,t0,flag2,l):
    if t<=0.5:
        t0=0
    if (u.x-v.x)**2+(u.y-v.y)**2<=1245:
        flag2=1
        t0=t
    if t-t0<=15:
        for i in l:
            if i.x<=800 and i.x>=0 and i.y<=500 and i.y>=0 and flag2==1:
                i.vx=u.x-i.x
                i.vy=u.y-i.y
                i.renew(0.01)
    else:
        flag2=0
    return flag2,t0
#the act of rocket
def myrocket(u,v,t,t1,flag3):
    if t<=0.5:
        t1=0
    if ((u.x-v.x)**2+(u.y-v.y)**2)<=1245:
        flag3=1
        t1=t
    if flag3==1:
        app.c.coords(v.h,825,50)
        if t-t1<=15:
            app.accelerate=100
        else:
            app.accelerate=50
            flag3=0
    return flag3,t1
#the act of money
def mycoin(u,v):
    if ((u.x-v.x)**2+(u.y-v.y)**2)<=1245:
        app.score=app.score+10
def mycoins(u,v):
    if ((u.x-v.x)**2+(u.y-v.y)**2)<=1245:
        app.score=app.score+100
def mydiamond(u,v):
    if ((u.x-v.x)**2+(u.y-v.y)**2)<=1245:
        app.score=app.score+1000
def turnUp(t):
    if abs(t%10)<=0.01:
        app.speed=1.15*app.speed                               
    if abs(t%2)<=0.01:
        a1.vx=-2*app.speed                                
    if abs(t%2-0.5)<=0.01:
        a2.vx=-2*app.speed                                    
    if abs(t%2-1)<=0.01:
        a3.vx=-2*app.speed
    if abs(t%2-1.5)<=0.01:
        a4.vx=-2*app.speed
    if abs(t%15)<0.01:
        b1.vx,b1.vy=-app.speed,2*app.speed
    if abs(t%15-5)<0.01:
        b2.vx,b2.vy=-app.speed,2*app.speed
    if abs(t%15-10)<0.01:
        b3.vx,b3.vy=-app.speed,2*app.speed
    if abs(t%7)<0.01:
        d1.vx=-1.5*app.speed
        d2.vx=-1.5*app.speed
    if t>=20 and abs(t%10)<=0.01:
        app.l3[randrange(6)].showUp()
    if abs(t%13)<=0.01:
        coins.showUp()
    if abs(t%6)<=0.01:
        coin.showUp()
    if abs(t%30-6)<=0.01:
        diamond.showUp()                                
def hit(t,t0,t1,t2,flag0,flag,flag1,flag2,flag3):
    for i in app.l1:
        flag,t2,flag0=over(human,i,t,flag,flag0,t2)
        i.renew(app.t0)                                
    for i in app.l2:
        flag1=convey(human,d1,d2,flag1,t)
        flag1=convey(human,d2,d1,flag1,t)
        i.renew(app.t0)                                        
    myshield(human,shield)
    flag2,t0=mymagnet(human,magnet,t,t0,flag2,app.l4)
    flag3,t1=myrocket(human,rocket,t,t1,flag3)
    mycoin(human,coin)
    mycoins(human,coins)                                    
    mydiamond(human,diamond)
    for i in app.l3:
        i.prop(human)                                
    app.c.update()
    
    return t0,t1,t2,flag0,flag,flag1,flag2,flag3
def remind():
    app.lab1['text']='life:%d'%(app.life)
    app.lab2['text']='time:%0.2f'%(app.t)
    app.lab3['text']='score:%d'%(app.score)

def humanbeing(t):
    if abs(t%0.4)<=0.01:
        human.h=app.human1
        app.c.itemconfig(app.human1,state='normal')
        app.c.itemconfig(app.human21,state='hidden')
    if abs(t%0.4-0.2)<=0.01:
        human.h=app.human21
        app.c.itemconfig(app.human21,state='normal')
        app.c.itemconfig(app.human1,state='hidden')
def main():
    t0,t1,t2=0,0,0
    flag0,flag,flag1,flag2,flag3=0,0,0,0,0
    while app.t<=120 and app.life > 0:
        updownupdate()
        humanbeing(app.t)
        app.t=app.t+0.01   
        turnUp(app.t)
        t0,t1,t2,flag0,flag,flag1,flag2,flag3=hit(app.t,t0,t1,t2,flag0,flag,flag1,flag2,flag3)
        remind()
        human.change(app.t0)
        app.c.update()
        sleep(0.01)
    if app.life> 0:
        PlaySound(victorymusic)
        app.c.grid_forget()
        app.lab1.grid_forget()
        app.lab2.grid_forget()
        app.lab3.grid_forget()
        app.c3.pack()
        app.c3.create_image(400,230,image = app.pict3)
        app.but5.place(relx=0.5,rely=0.85,anchor=S)
        app.lab4['text']=str(app.t)
        app.lab5['text']=str(app.score)
        app.lab4.place(relx=0.21,rely=0.8,anchor=S)
        app.lab5.place(relx=0.21,rely=0.91,anchor=S)
    if app.life <=0:    
        PlaySound(defeat)    
    while True:
        app.c.update()
app=App()
a1=thing(825,50*randrange(11),0,0,app.a1)
a2=thing(825,50*randrange(11),0,0,app.a2)
a3=thing(825,50*randrange(11),0,0,app.a3)
a4=thing(825,50*randrange(11),0,0,app.a4)
d1=thing(825,50*randrange(11),0,0,app.d1)
d2=thing(825,50*randrange(11),0,0,app.d2)
b1=thing(825,50*randrange(11),0,0,app.b1)
b2=thing(825,50*randrange(11),0,0,app.b2)
b3=thing(825,50*randrange(11),0,0,app.b3)
human=thing(50,250,0,0,app.human1)
shield=thing(825,50,0,0,app.shield)
rocket=thing(825,50,0,0,app.rocket)
magnet=thing(825,50,0,0,app.magnet)
coin=thing(825,50,0,0,app.coin)
coins=thing(825,50,0,0,app.coins)
diamond=thing(825,50,0,0,app.diamond)
app.l1=[a1,a2,a3,a4,b1,b2,b3]
app.l2=[d1,d2]
app.l3=[shield,rocket,magnet,coin,coins,diamond]
app.l4=[coin,coins,diamond]
app.loop()
