import random as r
import time
import matplotlib.pyplot as p

class item:
    def __init__(self,weight,value,timecreated):
        self.weight = weight
        self.value = value
        self.timecreated = time.time()
    def __repr__(self):
        return f'Weight: {self.weight} Value: {self.value}'

items = [item(r.randint(1,100),r.randint(1,100),time.time()) for i in range(50)]
#items = [item(7,9),item(4,5),item(10,2),item(5,5),item(10,7)]

def Cw(items,target_W):

    bag = {0:[0,[]]} ## - Tracks Cw for various W - ##

    for W in range(1,target_W+1):
        max_val = [0,[]]
        for item in items:
            
            if item.weight <= W:
                for i in range(item.weight,W+1):
                    if item not in bag[i-item.weight][1]:
                        r = i-item.weight
                        temp = [item.value+bag[r][0],[item]+bag[r][1]]
                        if max_val[0] < temp[0]:
                            max_val = temp
        bag[W] = max_val

    return bag[target_W]

def Cw2(items,W):

    if W == 0 or len(items) == 0:
        return 0
    if items[-1].weight > W:
        return Cw2(items[0:-1],W)
    return max(items[-1].value+Cw2(items[0:-1],W-items[-1].weight),Cw2(items[0:-1],W))

times = {}

while 1:
    W = r.randint(5,100)
    w = 100
    items = [item(r.randint(1,w),r.randint(1,w),time.time()) for i in range(r.randint(1,100))]
    x = Cw(items,W)
    print(x)
    y = Cw2(items,W)
    print(y)
    if x[0] != y:
        print('OH GOOD LAWD THERES AN ERROR!!!! FINALLY, ABOUT TIME.')
        break

##for i in range(200):
##    times[i] = 0
##    print(i)
##    time_before = time.time()
##    Cw(items,i)
##    times[i] += 10 * (time.time() - time_before)

##    for y in range(10):
##        time_before = time.time()
##        Cw(items,i)
##        times[i] += time.time() - time_before
##    times[i] = times[i]*10
##
##p.plot(times.keys(),times.values())
##p.show()
