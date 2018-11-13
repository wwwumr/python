import Tkinter as tk
from time import sleep,clock
from random import randrange
import gc, sys, winsound, threading
from collision import *
from consts import *

class Sprite:
    def __init__(self,_id,x,y,w,h):
        self.children = []
        self.parent = None
        self.x, self.y = x, y
        self.id = _id
        self.type = canvas.type(_id)
        self.width = w
        self.height = h
    def getBound(self):
        return int(self.x-self.width/2)/SIZE, int(self.x+self.width/2)/SIZE,\
               int(self.y-self.height/2)/SIZE, int(self.y+self.height/2)/SIZE
    def move(self):
        if not self.parent:
            self.ax, self.ay = self.x, self.y
        for child in self.children:
            child.ax, child.ay = child.x+self.ax, child.y+self.ay
            if -WIDTH < child.ax < WIDTH*2 or isinstance(child,Coin):
                child.move()
        if self.id:
            if hasattr(self,"playFrame"): self.playFrame()
            if self.type == "image":
                if hasattr(self,"seq"):
                    for img in self.seq:
                        canvas.coords(img,self.ax,self.ay)
                else: canvas.coords(self.id,self.ax,self.ay)
            elif self.type == "text":
                canvas.coords(self.id,self.ax,self.ay)
            else:
                canvas.coords(self.id,
                              self.ax,self.ay,
                              self.ax+self.width,self.ay+self.height)
    def addChild(self,child):
        self.children.append(child)
        child.parent = self
    def removeChild(self,child):
        for i in range(len(child.children)):
            child.removeChild(child.children[0])
        self.children.remove(child)
        canvas.delete(child.id)
        child.parent = None

class Clip(Sprite):
    def __init__(self,ids,x,y,w,h):
        self.seq = ids
        self.frame = 0
        self.range = (0,len(ids))
        self.play = False
        self.dx = 0
        self.rate = 1
        Sprite.__init__(self,self.seq[self.frame],x,y,w,h)
        canvas.itemconfig(self.id,state="normal")
    def gotoAndStop(self,frame):
        self.frame = frame
        self.play = False
        self.changeFrame()
    def changeFrame(self):
        canvas.itemconfig(self.id,state="hidden")
        self.id = self.seq[self.frame]
        canvas.itemconfig(self.id,state="normal")
    def setRange(self,start,end):
        self.range = start,end
        self.play = True
        self.frame = start
        self.changeFrame()
    def playFrame(self):
        if self.play:
            self.dx += 1
            if self.dx >= self.rate:
                self.frame += int(self.dx//self.rate)
                self.dx %= self.rate
                if self.frame >= self.range[1]:
                    self.frame -= self.range[1]-self.range[0]
                self.changeFrame()

class Stage(Sprite):
    def __init__(self,width,height):
        self.maxX = float("inf")
        self.background = []
        Sprite.__init__(self,
                        canvas.create_rectangle(0,HEIGHT-height,width,HEIGHT,
                                                fill=BG[style],outline=""),
                        0,HEIGHT-height,width,height)
    def addBg(self,bg):
        self.background.append(bg)
        self.addChild(bg)
    def lowerBg(self):
        for sprite in self.background:
            canvas.lower(sprite.id)
        canvas.lower(self.id)

class Hero(Clip):
    def __init__(self,r,c):
        imgs = [PhotoImage(source) for source in HERO]
        images = [canvas.create_image(INIT_POS,0,image=img,
                                      anchor="center",state="hidden") \
                  for img in imgs]
        Clip.__init__(self,images,
                      SIZE*c+SIZE/2,SIZE*(r+1)-imgs[0].height()/2,
                      30,32)
        self.label = {'ls':0,'lj':1,'lrs':2,'lre':6,'lcs':6,'lce':8,'ld':8}
        self.num = len(HERO)/4
        self.cur = 1
        self.vx = 0
        self.vy = 0
        self.max = SPEED
        self.d = 0
        self.t = 0
        self.trans = False
        self.win = False
        self.invin = 0
        self.run = False
        self.climb = False
        self.land = True
        self.large = False
        self.combo = 1
        self.comboTime = 0
        self.state = 0
        self.nextScene = 0
        self.die = False
        self.start = False
        self.gotoAndStop(self.getFrame('ls'))
    def jump(self):
        self.vy = -BOUNCE
        self.land = False
        self.gotoAndStop(self.getFrame('lj'))
    def smallJump(self):
        self.vy = -SMALL_BOUNCE
        self.land = False
        self.gotoAndStop(self.getFrame('ls'))
    def fall(self):
        if self.frame != self.getFrame('lj') and not self.climb:
            self.land = False
            self.gotoAndStop(self.getFrame('ls'))
    def stand(self):
        self.vy = 0
        if self.land or self.state:
            return
##        if self.land:
##            return
##        self.vy = 0
        if self.run:
            self.setRange(self.getFrame('lrs'),self.getFrame('lre'))
        else:
            self.gotoAndStop(self.getFrame('ls'))
        self.land = True
    def squat(self):
        if not self.large:
            return
        self.gotoAndStop(self.getFrame('ld'))
        self.y += 16
    def switch(self,direction):
        if (direction+1)/2 != self.cur:
            if self.land:
                self.cur = 1-self.cur
                self.setRange(self.getFrame('lrs'),self.getFrame('lre'))
            elif self.frame == self.getFrame('lj'):
                self.cur = 1-self.cur
                self.gotoAndStop(self.getFrame('lj'))
            else:
                self.cur = 1-self.cur
                self.gotoAndStop(self.getFrame('ls'))
        elif self.land and not self.run:
            self.setRange(self.getFrame('lrs'),self.getFrame('lre'))
        self.run = True
    def stop(self):
        self.run = False
        if self.land: self.gotoAndStop(self.getFrame('ls'))
    def startClimb(self):
        self.vx = 0
        self.vy = 0
        self.x = flag.x-15
        self.climb = True
        self.cur = 1
        self.setRange(self.getFrame('lcs'),self.getFrame('lce'))
    def endClimb(self):
        self.climb = False
        self.x = flag.x+15
        self.cur = 0
        self.gotoAndStop(self.getFrame('lcs'))
        self.state = 4
    def getItem(self,effect):
        global score,coin
        if effect == 0:
            score += 200
            coin += 1
        elif effect == 1:
            getScore(1000,self.x,self.y-self.height*2,False)
            if not self.large:
                self.large = True
                self.t = 0
                self.trans = True
                self.y -= 16
        else:
            print "other"
    def bigger(self):
        if self.play:
            self.setRange(self.range[0]+self.num*2,
                            self.range[1]+self.num*2)
        else:
            self.gotoAndStop(self.frame+self.num*2)
    def smaller(self):
        if self.play:
            self.setRange(self.range[0]-self.num*2,
                            self.range[1]-self.num*2)
        else:
            self.gotoAndStop(self.frame-self.num*2)
    def destroy(self):
        if not self.die and not self.invin:
            if self.large:
                self.large = False
                self.t = 0
                self.height = 32
                self.invin = INVIN_TIME
                self.smaller()
            else:
                self.die = True
                for _id in self.seq:
                    canvas.lift(_id)
                self.vx,self.vy = 0,-12
    def update(self):
        global flag
        if self.invin: self.invin -= 1
        if self.trans:
            self.t += 1
            if self.t == 20:
                self.trans = False
                self.bigger()
                self.height = 64
            elif self.t%4 == 0:
                self.bigger()
            elif self.t%4 == 2:
                self.smaller()
                canvas.coords(self.id,self.parent.x+self.x,
                                self.parent.y+self.y+16)
        elif self.state:
            self.d += 1
            if self.state == 1:
                self.y += 1
                if self.d == SIZE*3:
                    switchScene(self.nextScene)
            elif self.state == 2:
                self.x += 1
                self.vx = 1
                if self.d == SIZE*3:
                    switchScene(self.nextScene)
            elif self.state == 3:
                self.y -= 1
                if self.d == SIZE*2:
                    self.state = 0
                    self.d = 0
            elif self.state == 4:
                if self.d == 10:
                    self.state = 0
                    listener.cur = 1
                    listener.right = True
                    self.switch(1)
        elif self.climb:
            self.y += 6
            if self.y > stage.height-SIZE*3-self.height/2:
                self.y = stage.height-SIZE*3-self.height/2
            flag.children[0].y += 6
            if flag.children[0].y >= \
               flag.height/2-flag.children[0].height/2-SIZE:
                self.endClimb()
                flag.children[0].gotoAndStop(0)
                flag = None
        else:
            self.x += self.vx
            self.x = max(min(self.x,self.parent.width-self.width/2),
                         -self.parent.x+self.width/2)
            #if not self.land:
            self.vy += G
            self.vy = min(self.vy,FALL_SPEED)
            self.y += self.vy
            if self.y > stage.height:
                self.large = False
                self.invin = 0
                self.destroy()
            if self.comboTime:
                self.comboTime -= 1
                if self.comboTime == 0:
                    self.combo = 1
    def getFrame(self,s):
        return self.label[s]+self.cur*self.num+self.large*self.num*2
    def playFrame(self):
        if self.play:
            if self.climb: self.dx += 3
            else: self.dx += abs(self.vx)
            if self.dx >= HERO_RATE:
                self.frame += int(self.dx//HERO_RATE)
                self.dx %= HERO_RATE
                if self.frame >= self.range[1]:
                    self.frame -= self.range[1]-self.range[0]
                self.changeFrame()

class Flag(Sprite):
    def __init__(self,c):
        img = PhotoImage(FLAG[0])
        Sprite.__init__(self,canvas.create_image(INIT_POS,0,
                                                 image=img,anchor="center"),
                        c*SIZE+SIZE/2,stage.height-SIZE*2-img.height()/2,
                        img.width(),img.height())
        imgs = [PhotoImage(source) for source in FLAG[:0:-1]]
        images = [canvas.create_image(INIT_POS,0,image=img,
                                      anchor=anchor,state="hidden") \
                  for img,anchor in zip(imgs,['w','e'])]
        self.addChild(Clip(images,0,-self.height/2+40,
                           imgs[0].width(), imgs[0].height()))

class Item(Clip):
    def __init__(self,name,r,c):
        imgs = [PhotoImage(source) for source in name]
        ids = [canvas.create_image(INIT_POS,0,image=img,
                                   anchor="center",state="hidden") \
               for img in imgs]
        x = c*SIZE+SIZE/2
        y = (r+1)*SIZE-img.height()/2
        Clip.__init__(self,ids,x,y,imgs[0].width(),imgs[0].height())
        self.vx = 0
        self.dy = 0
        self.oy = y
        self.init = True
    def update(self):
        if self.init:
            self.y += self.vy
            self.dy += self.vy
            if self.dy <= -SIZE*2:
                self.vy = -self.vy
            elif self.dy >= 0:
                self.vy = 0
                self.y = self.oy
                self.init = False
    def destroy(self):
        hero.getItem(self.effect)
        self.parent.removeChild(self)
        items.remove(self)
        dynamics.remove(self)

class Coin(Item):
    def __init__(self,r,c,static=False):
        if static:
            Item.__init__(self,COIN,r,c)
            self.rate = 8
        else:
            Item.__init__(self,ITEM,r,c)
            self.vy = -12
        self.setRange(0,4)
        self.static = static
        if static:
            self.vy = 0
            self.init = False
        self.effect = 0
    def update(self):
        global score
        if not self.static:
            Item.update(self)
            if not self.init:
                self.destroy()
                getScore(200,self.x,self.y,False)
                score -= 200

class Large(Item):
    def __init__(self,r,c):
        Item.__init__(self,LARGE,r,c)
        self.effect = 1
        self.vx = ITEM_SPEED
        self.vy = -1
        self.land = True
    def update(self):
        if self.init:
            self.y += self.vy
            self.dy += self.vy
            if self.dy <= -SIZE:
                self.vy = 0
                self.init = False
                self.gotoAndStop(1)
        else:
            self.x += self.vx
            if not self.land:
                self.vy += G
                self.vy = min(self.vy,FALL_SPEED)
                self.y += self.vy

class Enemy(Clip):
    def __init__(self,name,r,c):
        imgs = [PhotoImage(source) for source in name]
        ids = [canvas.create_image(INIT_POS,0,image=img,
                                   anchor="center",state="hidden") \
               for img in imgs]
        x = c*SIZE+SIZE/2
        y = (r+1)*SIZE-imgs[0].height()/2
        Clip.__init__(self,ids,x,y,imgs[0].width(),imgs[0].height())
        self.rate = ENEMY_RATE
        self.setRange(0,2)
        self.vx = -ENEMY_SPEED
        self.cur = 0
        self.vy = 0
        self.land = True
        self.die = False
        self.start = False
    def destroy(self):
        if not self.die:
            for _id in self.seq:
                canvas.lift(_id)
            self.die = True
            self.vy = -5
            self.gotoAndStop(5)
    def delete(self):
        self.parent.removeChild(self)
        enemies.remove(self)
        dynamics.remove(self)
    def switch(self):
        self.vx = -self.vx
        self.cur = 1-self.cur
        self.setRange(self.cur*2,(self.cur+1)*2)

class Mushroom(Enemy):
    def __init__(self,r,c):
        Enemy.__init__(self,MUSHROOM,r,c)
        self.flat = False
        self.t = 0
    def update(self):
        if not self.start: return
        elif self.flat:
            self.t += 1
            if self.t == 20:
                self.delete()
        else:
            self.x += self.vx
            self.vy += G
            self.vy = min(self.vy,FALL_SPEED)
            self.y += self.vy
            if self.ax < -WIDTH or self.y > stage.height:
                self.delete()
    def treaded(self):
        self.flat = True
        self.die = True
        self.gotoAndStop(4)

class Tortoise(Enemy):
    def __init__(self,r,c,red=False):
        Enemy.__init__(self,[TORTOISE,RED_TORTOISE][red],r,c)
        self.hide = False
        self.red = red
    def update(self):
        if not self.start: return
        self.x += self.vx
        self.vy += G
        self.vy = min(self.vy,FALL_SPEED)
        self.y += self.vy
        if self.ax < -WIDTH/2 or self.ax > WIDTH*3/2 or self.y > stage.height:
            self.delete()
    def treaded(self):
        self.gotoAndStop(4)
        self.hide = True
        self.height = 32
    def switch(self):
        self.vx = -self.vx
        self.cur = 1-self.cur
        if not self.hide: self.setRange(self.cur*2,(self.cur+1)*2)

class Frog(Enemy):
    def __init__(self,r,c):
        Enemy.__init__(self,FROG,r,c)
        self.t = 0
        self.jumpTime = randrange(20,40)
    def treaded(self):
        self.vx = 0
        self.vy = max(self.vy,0)
    def update(self):
        if not self.start: return
        self.vy += G
        self.vy = min(self.vy,FALL_SPEED)
        self.y += self.vy
        if self.land:
            if self.frame > 3:
                self.setRange(self.cur*2,(self.cur+1)*2)
                self.vx = 0
            self.t += 1
            if self.t == self.jumpTime:
                self.gotoAndStop(4+self.cur)
                self.land = False
                self.t = 0
                self.jumpTime = randrange(20,40)
                self.vy = -randrange(10,20)
                self.vx = (1-self.cur*2)*self.vy/5
            return
        self.x += self.vx
        if self.ax < -WIDTH or self.y > stage.height:
            self.delete()
    def switch(self):
        self.cur = 1-self.cur
        self.vx = -self.vx
        self.setRange(self.cur*2,(self.cur+1)*2)

class Flower(Enemy):
    def __init__(self,r,c):
        Enemy.__init__(self,FLOWER,r,c)
        self.y += 2*SIZE
        self.width -= FLOWER_WIDTH
        self.height -= FLOWER_HEIGHT
        self.vy = -1
        self.d = 0
    def update(self):
        if not self.start: return
        self.y += self.vy
        self.d += self.vy
        if self.d <= -3*SIZE or self.d >= 0:
            self.vy = -self.vy
    def switch(self):
        pass

class Barrier(Sprite):
    def __init__(self,_id,x,y,w,h):
        Sprite.__init__(self,_id,x,y,w,h)
        self.c = (self.x-self.width/2)/SIZE
        self.r = (self.y-self.height/2)/SIZE

class Wall(Barrier):
    def __init__(self,x,y,ground = False):
        img = PhotoImage(WALL[ground])
        Barrier.__init__(self,
                         canvas.create_image(INIT_POS,0,
                                             image=img,
                                             anchor="center"),
                         x,y,img.width(),img.height())

class Tube(Barrier):
    def __init__(self,r,c):
        Barrier.__init__(self,0,c*SIZE+SIZE/2,r*SIZE+SIZE/2,SIZE,SIZE)

class Pipe(Sprite):
    def __init__(self,r,c,d,k):
        img = PhotoImage(TUBE[d][k])
        if d == 0:
            x,y = c*SIZE-SIZE/2,r*SIZE
        else:
            x,y = c*SIZE,r*SIZE-SIZE/2
        Sprite.__init__(self,canvas.create_image(INIT_POS,0,image=img,anchor="center"),
                        x,y,img.width(),img.height())
        
class Block(Barrier):
    def __init__(self,x,y,i):
        if i == 'x':
            img = PhotoImage(BLOCK[1+(terrain[y/SIZE-1][x/SIZE]!=0)*2])
            _id = canvas.create_image(INIT_POS,0,image=img,anchor="center",
                                      state="normal")
        elif i == 'y':
            img = PhotoImage(BLOCK[1])
            _id = canvas.create_image(INIT_POS,0,image=img,anchor="center",
                                      state="hidden")
        else:
            img = PhotoImage(BLOCK[i not in 'ab'])
            imgs = [img,PhotoImage(BLOCK[2])]
            self.seq = [canvas.create_image(INIT_POS,0,image=img,
                                            anchor="center",state=state) \
                        for img,state in zip(imgs,["normal","hidden"])]
            _id = self.seq[0]
            self.frame = 0
        Barrier.__init__(self,_id,
                         x,y,img.width(),img.height())
        self.vy = 0
        self.oy = y
        self.item = i
        self.times = 5
        self.pvy = [-16,0]
        self.broken = False
    def pushUp(self):
        if self.item == 'x' and hero.large:
            for i,pos in zip([0,1,1,0],["se","sw","ne","nw"]):
                self.addChild(Sprite(canvas.create_image
                                     (-100,0,image=PhotoImage(PIECES[i]),
                                      anchor=pos),
                                     0,0,0,0))
            self.broken = True
            canvas.itemconfig(self.id,state="hidden")
            terrain[self.y/SIZE][self.x/SIZE] = 0
        elif self.item != 'x' and self.frame == 0 and not self.vy:
            if self.item in 'ace':
                item = Coin(self.r-1,self.c)
                stage.addChild(item)
                items.append(item)
                dynamics.append(item)
        if self.item == 'e':
            self.times -= 1
        else:
            self.times = 0
        self.y = self.oy
        self.vy = -4
        self.dy = 0
        for enemy in enemies:
            if enemy.die: continue
            l,r,u,d = enemy.getBound()
            if d == self.y/SIZE:
                if self.x/SIZE in range(l,r+1):
                    enemy.destroy()
                    getScore(100,enemy.x,enemy.y)
        for item in items:
            if isinstance(item,Coin) and not item.static: continue
            l,r,u,d = item.getBound()
            if d == self.y/SIZE:
                if self.x/SIZE in range(l,r+1):
                    if isinstance(item,Coin):
                        stage.removeChild(item)
                        items.remove(item)
                        dynamics.remove(item)
                        item = Coin(self.r-1,self.c)
                        stage.addChild(item)
                        items.append(item)
                        dynamics.append(item)
                    elif isinstance(item,Large):
                        item.vy = -SMALL_BOUNCE
    def update(self):
        if self.broken:
            for i,child in enumerate(self.children):
                if i%2 == 0: child.x -= 4
                else: child.x += 4
                child.y += self.pvy[i/2]
            for i in range(2):
                self.pvy[i] += G
            if self.children[0].y > stage.height:
                self.parent.removeChild(self)
                dynamics.remove(self)
        elif self.vy:
            self.y += self.vy
            self.dy += self.vy
            if self.dy <= -self.height/2:
                self.vy = -self.vy
            elif self.dy >= 0:
                self.vy = 0
                self.y = self.oy
                if self.item != 'x' and self.times <= 0:
                    self.frame = 1
                    canvas.itemconfig(self.seq[0],state="hidden")
                    canvas.itemconfig(self.seq[1],state="normal")
                    dynamics.remove(self)
                    if self.item in 'bd':
                        item = Large(self.r,self.c)
                        stage.addChild(item)
                        items.append(item)
                        dynamics.append(item)
                        for _id in item.seq:
                            canvas.lower(_id)
                        canvas.lower(stage.id)

class DynamicText(Sprite):
    def __init__(self,x,y,text,d):
        self.d = d
        self.t = 0
        self.s = 0
        _id = canvas.create_text(x,y,text=text,fill="#ffffff",
                                 font=("Fixedsys",12))
        Sprite.__init__(self,_id,x,y,0,0)
    def update(self):
        if self.s < self.d:
            self.y -= 2
            self.s += 2
        else:
            self.t += 1
            if self.t == 15:
                self.parent.removeChild(self)
                dynamics.remove(self)

class KeyboardHandler:
    def __init__(self):
        self.run = False
    def onPress(self,e):
        if hero.state or hero.trans or not self.run or paused: return
        
        if e.keysym == "Left":
            hero.switch(-1)
            if not self.left:
                self.cur = -1
                self.left = True
        elif e.keysym == "Right":
            hero.switch(1)
            if not self.right:
                self.cur = 1
                self.right = True
        elif e.keysym == "Up":
            if not self.up and hero.land:
                hero.jump()
                self.lift = True
                self.t = 0
            self.up = True
        elif e.keysym == "Down":
            hero.squat()
            self.down = True
    def onRelease(self,e):
        global paused
        if e.keysym == 'p':
            paused = not paused
        if hero.state or not self.run or paused: return
        
        if e.keysym == "Left":
            self.left = False
            if self.right:
                hero.switch(1)
                self.cur = 1
            else:
                hero.stop()
                self.cur = 0
        elif e.keysym == "Right":
            self.right = False
            if self.left:
                hero.switch(-1)
                self.cur = -1
            else:
                hero.stop()
                self.cur = 0
        elif e.keysym == "Up":
            self.up = False
            self.lift = False
        elif e.keysym == "Down":
            self.down = False
    def update(self):
        if hero.state or hero.trans: return
        
        if self.cur == -1:
            if hero.vx > -hero.max: hero.vx -= hero.max/ACCEL
            else: hero.vx = -hero.max
        elif self.cur == 1:
            if hero.vx < hero.max: hero.vx += hero.max/ACCEL
            else: hero.vx = hero.max
            l,r,u,d = hero.getBound()
            for args in exits:
                if d == args[0]+1 and r == args[1]:
                    if args[2] == 1:
                        hero.stop()
                        hero.y = d*SIZE-hero.height/2
                        hero.state = 2
                        hero.switch(1)
                        hero.nextScene = args[3]
                        return
                    elif args[2] == 2:
                        PlaySound(WIN)
                        stage.removeChild(hero)
                        hero.state = -1
                        hero.parent = stage
                        hero.win = True
        else:
            if abs(hero.vx) < hero.max/ACCEL: hero.vx = 0
            elif hero.vx > 0: hero.vx -= hero.max/ACCEL
            else: hero.vx += hero.max/ACCEL
        if self.lift:
            if self.t < JUMP_TIME and hero.vy < 0:
                self.t += 1
                hero.vy = -BOUNCE
            else:
                self.lift = False
        if self.down and hero.land:
            l,r,u,d = hero.getBound()
            for args in exits:
                if args[2] == 0 and d == args[0] and r == args[1]:
                    hero.stop()
                    if hero.large:
                        hero.gotoAndStop(hero.getFrame('ld'))
                    hero.state = 1
                    hero.nextScene = args[3]
                    return
    def reset(self):
        self.left = False
        self.right = False
        self.cur = 0
        self.up = False
        self.lift = False
        self.down = False
        self.t = 0

def PhotoImage(filename):
    key = style+filename[:-4]
    if key in images:
        return images[key]
    img = tk.PhotoImage(file="%s%s/%s" %(IMAGE,style,filename))
    images[key] = img
    return img

def PlaySound(filename):
    thread = threading.Thread(target=winsound.PlaySound,
                              args=(AUDIO+filename,
                                    winsound.SND_FILENAME|winsound.SND_ASYNC))
    thread.setDaemon(True)
    thread.start()

def main(_root):
    global root,frame,canvas,closed,paused,mid,listener,heroIcon
    root = _root
    frame = tk.Frame(root)
    frame.pack()
    canvas = tk.Canvas(frame,width=WIDTH,height=HEIGHT)
    mid = tk.Canvas(frame,width=WIDTH,height=HEIGHT,bg="#000000")
    mid.create_text(WIDTH/2,HEIGHT/2,fill="#eeeeee",
                    text="NAN",
                    anchor="s",font=("Fixedsys",36,"bold"))
    mid.create_text(WIDTH/2-20,HEIGHT/2,fill="#eeeeee",
                    text="NAN",
                    anchor="nw",font=("Fixedsys",24,"bold"))
    heroIcon = tk.PhotoImage(file="%sbright/%s" %(IMAGE,HERO[9]))
    mid.create_image(WIDTH/2-20,HEIGHT/2,image=heroIcon,anchor="ne",
                     state="normal")
    
    closed = False
    paused = False
    root.protocol("WM_DELETE_WINDOW",winClose)
    listener = KeyboardHandler()
    canvas.bind_all("<KeyPress>", listener.onPress)
    canvas.bind_all("<KeyRelease>", listener.onRelease)
    init()
    while True:
        startGame()
        loop()
        if closed: return
        if life == 0:
            PlaySound(LOSE)
            canvas.forget()
            mid.pack()
            mid.itemconfig(1,text="GAME OVER")
            mid.itemconfig(2,text="")
            mid.itemconfig(3,state="hidden")
            if wait(3,mid.update): return
            close()
            return int(score+0.5),coin

def winClose():
    global closed
    closed = True
    PlaySound(EMPTY)
    root.destroy()

def close():
    global frame,canvas,mid,listener
    global stage, hero, style, scoreText, coinText, worldText, timeText, coinIcon
    global dynamics, terrain, images, blocks, enemies, items, exits, flag
    canvas.forget()
    mid.forget()
    frame.forget()
    del frame,canvas,mid,listener
    del stage, hero, style, scoreText, coinText, worldText, timeText, coinIcon
    del dynamics, terrain, images, blocks, enemies, items, exits, flag
    gc.collect()

def init():
    global scene, score, coin, life, world, time
    world = MAP
    score = coin = 0
    scene = 0
    life = 3
    time = 400

def startGame():
    global time
    if time == 0 and hero.die: timeUp = True
    else: timeUp = False
        
    createScene()
    listener.run = False
    mid.pack()

    if timeUp:
        mid.itemconfig(1,text="TIME UP")
        mid.itemconfig(2,text="")
        mid.itemconfig(3,state="hidden")
        if wait(3,mid.update): return
    mid.itemconfig(1,text="WORLD%s" %world[-3:])
    mid.itemconfig(2,text=" x %d" %life)
    mid.itemconfig(3,state="normal")
    if wait(3,mid.update): return
    mid.forget()
    canvas.pack()
    if hero.state == 4:
        hero.max /= 2
        listener.run = False
    else: listener.run = True
    time = 400
    PlaySound(BGM)

def createScene():
    global stage, hero, style, scoreText, coinText, worldText, timeText, coinIcon
    global dynamics, terrain, images, blocks, enemies, items, exits, flag
    images = { }
    f = open(world+"_%d.txt"%scene,'r')
    style = f.readline()[:-1]
    lines = f.readlines()
    stage = Stage((len(lines[0])-1)*SIZE,len(lines)*SIZE)
    flag = None
    terrain = []
    dynamics = []
    blocks = []
    enemies = []
    items = []
    exits = []
    tubes = []
    lines[-1] = lines[-1]+'\n'
    for r,l in enumerate(lines):
        terrain.append([0]*len(l))
        for c,s in enumerate(l[:-1]):
            if s == '0':
                terrain[r][c] = 1
                stage.addChild(Wall(c*SIZE+SIZE/2,r*SIZE+SIZE/2,True))
            elif s == '1':
                terrain[r][c] = 1
                stage.addChild(Wall(c*SIZE+SIZE/2,r*SIZE+SIZE/2))
            elif s == '2':
                terrain[r][c] = 1
                tube = Tube(r,c)
                stage.addChild(tube)
                i = r-1
                if lines[i][c] in '<>^|CD':
                    terrain[r][c] = terrain[r][c-1] = 1
                    tube.addChild(Pipe(0,0,0,0))
                while lines[i][c] in '<>^|CD':
                    terrain[i][c] = terrain[i][c-1] = 1
                    tube.addChild(Pipe(i-r,0,0,2-(lines[i][c]=='|')))
                    if lines[i][c] == '<':
                        hero = Hero(i-1,c)
                        hero.state = 3
                        hero.x -= SIZE/2
                        hero.y += SIZE*2
                        stage.addChild(hero)
                        dynamics.append(hero)
                    else:
                        if lines[i][c] in ">D":
                            exits.append((i,c,0,scene+1))
                        if lines[i][c] in 'CD':
                            enemy = Flower(i,c-0.5)
                            stage.addChild(enemy)
                            dynamics.append(enemy)
                            enemies.append(enemy)
                    i -= 1
                j = c-2
                if lines[r][j] in '<>^-':
                    terrain[r-1][c-1] = terrain[r][c-1] = 1
                    tube.addChild(Pipe(0,-1,1,0))
                while lines[r][j] in '<>^-':
                    terrain[r-1][j] = terrain[r][j] = 1
                    tube.addChild(Pipe(0,j-c,1,2-(lines[r][j]=='-')))
                    if lines[r][j] == '>':
                        exits.append((r,j,1,scene+1))
                    j -= 1
                tubes.append(tube)
            elif s == '3':
                flag = Flag(c)
                stage.addChild(flag)
                for _id in hero.seq:
                    canvas.lift(_id)
                terrain[r][c] = 1
                stage.addChild(Wall(c*SIZE+SIZE/2,r*SIZE+SIZE/2))
                stage.addBg(Sprite(canvas.create_image
                                   (0,0,image=PhotoImage(CASTLE),anchor="s"),
                                   (c+6)*SIZE+SIZE/2,(r+1)*SIZE,0,0))
                exits.append((r,c+7,2))
            elif s == '*':
                item = Coin(r,c,True)
                stage.addChild(item)
                items.append(item)
                dynamics.append(item)
            elif s in '{[':
                hero = Hero(r,c)
                stage.addChild(hero)
                dynamics.append(hero)
                if s == '[':
                    stage.addBg(Sprite(canvas.create_image
                                       (0,0,
                                        image=PhotoImage(CASTLE),anchor="s"),
                                       c*SIZE+SIZE/2,(r+1)*SIZE,0,0))
                    hero.state = 4
            elif s in 'abcdex':
                block = Block(c*SIZE+SIZE/2,r*SIZE+SIZE/2,s)
                blocks.append(block)
                terrain[r][c] = -len(blocks)
                stage.addChild(block)
                dynamics.append(block)
            elif s in 'ABDE':
                if s == 'A':
                    enemy = Mushroom(r,c)
                elif s in 'BD':
                    enemy = Tortoise(r,c,s=='D')
                elif s == 'E':
                    enemy = Frog(r,c)
                stage.addChild(enemy)
                dynamics.append(enemy)
                enemies.append(enemy)
    for image in LARGE+ITEM+PIECES:
        PhotoImage(image)
    blocks.reverse()

    if style == "bright":
        pos = 0
        while pos < stage.width:
            for x,y,i in CLOUD_POS[:-1]:
                stage.addBg(Sprite(canvas.create_image
                                   (0,0,
                                    image=PhotoImage(CLOUD[i]),anchor="ne"),
                                   pos+x,y,0,0))
            pos += CLOUD_POS[-1][0]-CLOUD_POS[0][0]
        pos = 0
        while pos < stage.width:
            for c,i in MOUNT_POS[:-1]:
                stage.addBg(Sprite(canvas.create_image
                                   (0,0,
                                    image=PhotoImage(MOUNT[i]),anchor="s"),
                                   (pos+c+0.5)*SIZE,stage.height-SIZE*2,0,0))
            pos += MOUNT_POS[-1][0]-MOUNT_POS[0][0]
            
    for _id in hero.seq:
        canvas.lower(_id)
    stage.lowerBg()
    for tube in tubes:
        for child in tube.children:
            canvas.lift(child.id)

    scoreText = canvas.create_text(20,20,fill="#eeeeee",
                                   text="NAN",
                                   anchor="nw",font=("Fixedsys",16,"bold"))
    coinText = canvas.create_text(160,20,fill="#eeeeee",
                                  text="NAN",
                                  anchor="nw",font=("Fixedsys",16,"bold"))
    worldText = canvas.create_text(300,20,fill="#eeeeee",
                                   text="WORLD\n %s " %world[-3:],
                                   anchor="nw",font=("Fixedsys",16,"bold"))
    timeText = canvas.create_text(440,20,fill="#eeeeee",
                                  text="NAN",
                                  anchor="nw",font=("Fixedsys",16,"bold"))
    coinIcon = Clip([canvas.create_image(160,40,
                                         image=PhotoImage(source),
                                         anchor="nw",state="hidden") \
                     for source in SYM],
                    160,40,0,0)
    coinIcon.setRange(0,4)
    coinIcon.rate = 8
    rollStage()
    stage.move()
    canvas.update()
    listener.reset()

def loop():
    global life,score,coin,time,scene,world
    clockTime = clock()
    while True:
        sleep(max(INTERVAL-clock()+clockTime,0))
        clockTime = clock()
        if closed: return
        
        canvas.itemconfig(scoreText,text="MARIO\n%06d" %score)
        canvas.itemconfig(coinText,text="\n  x%02d" %coin)
        canvas.itemconfig(timeText,text="TIME\n%03d" %time)
        
        if paused:
            canvas.update()
            continue
        elif hero.win:
            x = hero.getBound()[0]*SIZE+SIZE/2
            canvas.update()
            if time > 5:
                ranNum = randrange(3,5)
                time -= ranNum
                score += ranNum*100
            elif time > 0:
                score += time*100
                time = 0
            else:
                scene = 0
                world = world[:-1]+str(int(world[-1])+1)
                break
            continue
        
        elif time > 0: time -= INTERVAL
        else:
            time = 0
            canvas.itemconfig(timeText,text="TIME\n%03d" %0)
            hero.destroy()
        
        if hero.trans:
            hero.update()
            canvas.update()
            continue
        
        for s in dynamics:
            s.update()
        listener.update()
        checkCollision()
        rollStage()
        stage.move()
        coinIcon.move()
        canvas.update()
        
        if hero.die: break
        
    if hero.die:
        PlaySound(DIE)
        hero.gotoAndStop(hero.getFrame('ld'))
        listener.reset()
        listener.run = False
        stage.children = [hero]
        if wait(0.5): return
        while hero.y-hero.height/2+stage.y < HEIGHT+12*SIZE:
            sleep(INTERVAL)
            if closed: return
            hero.update()
            stage.move()
            canvas.update()
        
        life -= 1
        
    elif hero.win:
        sign = Sprite(canvas.create_image(0,0,image=PhotoImage(CAS_FLAG),
                                          anchor="s"),
                      x,stage.height-158,0,0)
        canvas.lower(sign.id)
        canvas.lower(stage.id)
        stage.addChild(sign)
        while sign.y > HEIGHT-SIZE*2-158:
            sleep(INTERVAL)
            if closed: return
            sign.y -= 5
            stage.move()
            canvas.update()
        if wait(1): return
        
    canvas.delete("all")
    canvas.forget()

def getScore(basis,x,y,combo=True):
    global score
    if combo: bonus = basis*hero.combo
    else: bonus = basis
    score += bonus
    hero.combo += 1
    hero.comboTime = COMBO_TIME
    text = DynamicText(x,y,str(bonus),15)
    stage.addChild(text)
    dynamics.append(text)

def checkCollision():
    global score,time
    jump = False
    for enemy in enemies:
        if enemy.die:
            continue
        elif not enemy.start:
            if enemy.ax < WIDTH+SIZE*2:
                enemy.start = True
            else: continue
        
        if isinstance(enemy,Flower):
            if hero.state:
                enemy.vy = 0
            elif rectCollision(hero,enemy):
                hero.destroy()
            continue
        
        l,r,u,d = enemy.getBound()
        result = terrainCollision(enemy,(l,r,u,d),terrain)
        if result[0]: enemy.switch()
        if result[1]:
            enemy.vy = 0
            enemy.land = True
            enemy.y = d*SIZE-enemy.height/2
        else:
            enemy.land = False
        if isinstance(enemy,Tortoise) and enemy.red and not enemy.hide and \
           (enemy.vx < 0 and (terrain[u][l] or not terrain[d][l]) or \
            enemy.vx > 0 and (terrain[u][r] or not terrain[d][r])):
            enemy.switch()

        result = enemyCollision(hero,enemy)
        if isinstance(enemy,Tortoise) and enemy.hide:
            for _enemy in enemies:
                if isinstance(_enemy,Flower) or _enemy is enemy or \
                   _enemy.die or not _enemy.start:
                    continue
                if rectCollision(enemy,_enemy):
                    if isinstance(_enemy,Tortoise) and _enemy.hide:
                       if(enemy.x < _enemy.x and enemy.vx > _enemy.vx or \
                          enemy.x > _enemy.x and enemy.vx < _enemy.vx):
                            enemy.vx,_enemy.vx = _enemy.vx,enemy.vx
                    else:
                        if abs(enemy.vx) > abs(_enemy.vx):
                            _enemy.vx = enemy.vx/2
                            _enemy.destroy()
                            getScore(400,_enemy.x,_enemy.y)
                        else:
                            if _enemy.x > enemy.x:
                                _enemy.x = enemy.x+(enemy.width+_enemy.width)/2
                            else:
                                _enemy.x = enemy.x-(enemy.width+_enemy.width)/2
                            enemy.vx = -enemy.vx
                            if enemy.vx > 0 and _enemy.vx >= 0 or \
                               enemy.vx < 0 and _enemy.vx <= 0:
                                _enemy.switch()
            if hero.state: continue
            if result == 1:
                enemy.vx = (enemy.x-hero.x)/2
                jump = True
                hero.y = enemy.y-(enemy.height+hero.height)/2
                getScore(100,enemy.x,enemy.y)
            elif result == -1:
                if enemy.vx >= 0 and hero.vx > 0 or \
                   enemy.vx <= 0 and hero.vx < 0:
                    if hero.vx > 0 and hero.x < enemy.x or \
                       hero.vx < 0 and hero.x > enemy.x:
                        enemy.vx = hero.vx*1.5
                    else:
                        enemy.vx = hero.vx
                else:
                    hero.destroy()
        else:
            if hero.state: continue
            if result == 1:
                hero.y = enemy.y-(enemy.height+hero.height)/2
                enemy.treaded()
                jump = True
                if isinstance(enemy,Frog):
                    time += 1
                    text = DynamicText(hero.x,hero.y-hero.height/2,"+1s",15)
                    stage.addChild(text)
                    dynamics.append(text)
                else:
                    getScore(100,enemy.x,enemy.y)
            elif result == -1:
                if isinstance(enemy,Frog):
                    hero.large = hero.invin = False
                    time = 0
                    canvas.itemconfig(timeText,text="TIME\n%03d" %0)
                hero.destroy()
    if hero.trans: return
    elif jump: hero.smallJump()
    for item in items:
        if item.init:
            continue
        l,r,u,d = item.getBound()
        if hasattr(item,"land"):
            result = terrainCollision(item,(l,r,u,d),terrain)
            if result[0]: item.vx = -item.vx
            if result[1]:
                item.vy = 0
                item.land = True
                item.y = d*SIZE-item.height/2
            else:
                item.land = False

        if rectCollision(hero,item):
            item.destroy()

    if hero.state: return
    
    l,r,u,d = hero.getBound()
    result = terrainCollision(hero,(l,r,u,d),terrain)
    if result[0] == -1:
        hero.vx = 0
        hero.x = (l+1)*SIZE+hero.width/2+1
    elif result[0] == 1:
        hero.vx = 0
        hero.x = r*SIZE-hero.width/2-1
    if result[1] == -1:
        hero.vy = -hero.vy
        hero.y = (u+1)*SIZE++hero.height/2
        for j in range(l,r+1):
            if terrain[u][j] < 0:
                blocks[terrain[u][j]].pushUp()
    elif result[1] == 1:
        hero.stand()
        hero.y = d*SIZE-hero.height/2
    else:
        hero.fall()

    if flag and not hero.climb and rectCollision(hero,flag):
        PlaySound(CLIMB)
        hero.startClimb()
        listener.run = False
        listener.reset()
        flag.children[0].gotoAndStop(1)
        bonus = (flag.y+flag.height/2-hero.y)//30*100
        score += bonus
        text = DynamicText(flag.x+30,flag.y-flag.height/2+bonus*0.3,
                           str(int(bonus)),bonus*0.3)
        stage.addChild(text)
        dynamics.append(text)

def switchScene(_scene):
    global scene
    scene = _scene
    large = hero.large
    destroyScene()
    createScene()
    listener.run = True
    if large:
        hero.large = True
        hero.y -= 16
        hero.height = 64
        hero.bigger()

def destroyScene():
    canvas.delete("all")

def rollStage():
    stage.x = SIZE*7.5-hero.x
    stage.maxX = max(min(stage.maxX, stage.x),WIDTH-stage.width)
    if stage.x < WIDTH-stage.width:
        stage.x = WIDTH-stage.width
    elif stage.x > min(stage.maxX,0):
        stage.x = min(stage.maxX,0)
    stage.y = HEIGHT/2-hero.y
    if stage.y > 0:
        stage.y = 0
    elif stage.y < HEIGHT-stage.height:
        stage.y = HEIGHT-stage.height

def wait(t,func=None):
    for i in range(int(t/INTERVAL)):
        if closed:
            return True
        sleep(INTERVAL)
        if func: func()
    return False

if __name__ == '__main__':
    MAP = ".%s" %MAP
    AUDIO = ".%s" %AUDIO
    IMAGE = ".%s" %IMAGE
    print main(tk.Tk()),"GAME OVER"
    if not closed: winClose()
