#get inputs
#map out terrain, get: my_land (list of all x,y points for surface); self.slopes (list of self.slopes for each section)
#identify landing pad, get: land_left,land_mid,land_right,land_height
#create distance function for easy calculations

import sys
import math

# Constants
using_vscode=False # Use True to run the code in VSCode
# Fake inputs (for testing purposes only)
fake_input0=7
fake_input1=["0 100", "1000 500", "1500 1500", "3000 1000", "4000 150", "5500 150", "6999 800"]
fake_input2="2500 2700 0 0 550 0 0"



# Class for the Lander
class Lander:
    def __init__(self, x=None, y=None, velocity_x=None, velocity_y=None, fuel=None, rotate=None, power=None):

        self.lim_x,self.lim_y=20,40 # Limit velocity for the lander
        self.gravity = 3.711 # Gravity const
        self.thrust_max = 4  # Max thrust accel
        self.surface = []    # List of surface points
        self.slopes = []     # List of slopes for each section
        self.obstacles=[]    # List of obstacles in the landing area
        self.stopme = False  # Flag to stop the simulation

        self.time = 0
        self.sequence=None
        surface_n = fake_input0 if using_vscode else int(input())
        for i in range(surface_n):
            self.surface.append([int(j) for j in (fake_input1[i].split() if using_vscode else input().split())])
            if i>=1:
                prev,this = self.surface[-2],self.surface[-1]
                self.slopes.append(round((this[1]-prev[1])/(this[0]-prev[0]),5))
                if this[1]==prev[1] and abs(this[0]-prev[0])>=1000:
                    print(f"x from {prev[0]} to {this[0]} at y={prev[1]}", file=sys.stderr, flush=True)
                    self.land_xleft = min(prev[0],this[0])
                    self.land_xright = max(prev[0],this[0])
                    self.land_x = (prev[0]+this[0])//2
                    self.land_y = prev[1]
                    self.land_xrad = self.land_xright - self.land_x
                    landing_index = i
        print("Surface = ", self.surface, file=sys.stderr, flush=True)
        for k,point in enumerate(self.surface):
            if self.land_xleft <= point[0] <= self.land_xright and point[1] != self.land_y:
                self.obstacles.append(point+[k])
        if len(self.obstacles)>0:
            self.leftmost, self.rightmost = [9999,9999],[9999,9999]
            for k,point in enumerate(self.obstacles):
                if abs(point[0]-self.land_xleft) <= abs(self.leftmost[0]-self.land_xleft):
                    self.leftmost = point
                if abs(point[0]-self.land_xright) <= abs(self.rightmost[0]-self.land_xright):
                    self.rightmost = point
            print(f"Obstacles = {self.obstacles}, left/right bounds = {self.leftmost} and {self.rightmost}", file=sys.stderr, flush=True)
            if self.leftmost[2] < landing_index:                
                self.direction = "RIGHT"
                leftof=self.rightmost
                rightof=self.surface[landing_index+1]
            else:
                self.direction = "LEFT"
                leftof=self.surface[landing_index-2]
                rightof=self.leftmost#self.surface[landing_index+1]


            self.leftbound = 0 if leftof[0]==self.land_xleft else (leftof[1]-self.land_y)/(leftof[0]-self.land_xleft)

            self.midbound = (0 if rightof[0]==self.land_x else (leftof[1]-self.land_y)/(leftof[0]-self.land_x))
            self.rightbound = 0 if rightof[0]==self.land_xright else (rightof[1]-self.land_y)/(rightof[0]-self.land_xright)
            print(f"angle of approach should be {self.direction}", self.leftbound, self.midbound, self.rightbound, file=sys.stderr, flush=True)
        # try:
        #     self.x,self.y,self.velocity_x,self.velocity_y,self.fuel,self.rotate,self.power=[int(j) for j in fake_input2.split()]
        # except:
        #     self.x,self.y,self.velocity_x,self.velocity_y,self.fuel,self.rotate,self.power=[int(j) for j in input().split()]
        # self.x_start, self.y_start = self.x, self.y
    def spelunk(self):

        # leftline = self.leftbound*(self.x-self.land_xleft)+self.land_y
        # # leftline = self.land_xleft
        # midline = self.midbound*(self.x-self.land_xright)+self.land_y
        # rightline = self.rightbound*(self.x-self.land_xright)+self.land_y
        leftline = self.leftbound*(self.x-self.land_xleft+10)+self.land_y
        # leftline = self.land_xleft
        midline = self.midbound*(self.x-self.land_x+10)+self.land_y
        rightline = self.rightbound*(self.x-self.land_xright+10)+self.land_y
        print("spelunk", self.x, self.y, leftline, rightline,  file=sys.stderr, flush=True)
        if rightline <= self.y <= leftline or rightline >= self.y >= leftline:
            print("WE'RE IN THE STRIKEZONE!",min(self.leftbound, self.rightbound),self.velocity_y/self.velocity_x,max(self.leftbound, self.rightbound),  file=sys.stderr, flush=True)
            if min(self.leftbound, self.rightbound) <= self.velocity_y/self.velocity_x:
                return 0, 4
            elif self.velocity_y/self.velocity_x <= max(self.leftbound, self.rightbound):
                return 0,3
            
                # if abs(self.velocity_x) < self.lim_x and abs(self.velocity_y) < self.lim_y:
                #     return 0, 3
                # else:
                #     return 0, 4
            else:
                return 0, 3
        elif leftline <= self.y <= midline or leftline >= self.y >= midline:
            print("WE'RE IN THE DANGERZONE!",  file=sys.stderr, flush=True)
            return 0, 4
        elif (self.y >= midline or self.x <= self.land_xright) and self.y > self.rightmost[1]:
            print("WE'RE GOING THE WRONG WAY!",  file=sys.stderr, flush=True)
            return 90, 4
        else:
            if abs(self.velocity_x) >= self.lim_x:
                return (22 if self.velocity_x > 0 else -22), 4
            return None
        

        

    def refresh(self):
        #updates self values per round
        print("refreshing", file=sys.stderr, flush=True)
        if not using_vscode:
            self.x,self.y,self.velocity_x,self.velocity_y,self.fuel,self.rotate,self.power=[int(j) for j in input().split()]
        
        # self.x,self.y,self.velocity_x,self.velocity_y,self.fuel,self.rotate,self.power=[int(j) for j in input().split()]
        if not self.stopme:
            self.Control()

    def distance(self, x1, y1, x0=None, y0=None):
        if x0 is None:
            x0=self.x
        if y0 is None:
            y0=self.y
        distance_x = x1 - x0
        distance_y = y1 - y0
        distance_to_point = math.sqrt(distance_x**2+distance_y**2)
        print("distancestuff", x1,y1,x0,y0, [distance_to_point, distance_x, distance_y], file=sys.stderr, flush=True)
        return [distance_to_point, distance_x, distance_y]
    def NewControl(self):
        # controls which self.sequence we will perform.
        #   checks trajectory:
        #   if trajectory (projected) intersect with landing pad, calculate impact speeds if we have a full cancellation burn
        #       if impact speeds are too high, we need to slow:
        #           find out which is more of a problem: velocity_x or velocity_y
        #           if velocity_x, we must maintain velocity_y while bleeding velocity_x
        #              
        #           if this slowing puts us off target, we must either wait or readjust.
        #       if impact speeds are AIGHT, we initiate full burn:
                    # theta=-round(math.round(math.atan(velocity_x/velocity_y)) if velocity_y!=0 else 0
        #   if trajectory (projected) does NOT intersect with landing pad, find out the problems:
            #coming up short
                # check if we started on the left or on the right of the pad, then check if we landed to the left or right.
                #if (start_x < land_left and crash_x < land_left) or (start_x > land_right and crash_x>land_right):
                    #if abs(velocity_x) > limit_x:
                        #depending on how far above limit x the velocity is with relation to distance to the landing point, we might want to initiate the slowing drift
                        #ultimately, we need need to increase velocity_y
                    #if abs(velocity_x) <= limit_x:
                        #well, then we do an accelerating drift.
                        #I suppose we could check how long it would take to reach that x position at this speed.
                        #check against fuel?
                        #We might be too low
            #we went too far
                #well, then we really need to initiate this stopping self.sequence at some point.
                #if 
                #find the stopping time and required distances.
                #


                #if velocity_y is too low
                #if velocity_y is too high
                    #then we float away?
                #if velocity_x is too low
                #if velocity_x is too high

                #elif projected_x <landing_left

        # store the previous self.sequence in memory to avoid a fucking TON of variables
        #

        self.time += 1
        try:
            print(new_angle, new_thrust)
        except NameError:
            print("0 4")
    def Control(self):
        print("controlling", file=sys.stderr, flush=True)
        if self.time==0:
            print("time", file=sys.stderr, flush=True)
            self.sequence = None
            self.phase = None
            if using_vscode:
                self.x,self.y,self.velocity_x,self.velocity_y,self.fuel,self.rotate,self.power=[int(j) for j in fake_input2.split()]
            self.x_start, self.y_start = self.x, self.y
            self.velocity_x_start, self.velocity_y_start = self.velocity_x, self.velocity_y
            x_to_travel,y_to_travel=abs(abs(self.land_x-self.x_start)-self.land_xrad),self.y-self.land_y
            print(f"self.x_start={self.x_start},self.y_start={self.y_start},self.velocity_x_start={self.velocity_x_start},self.velocity_y_start={self.velocity_y_start},x_to_travel={x_to_travel},y_to_travel={y_to_travel}", file=sys.stderr, flush=True)
        # abs(self.land_x-self.x) = abs(abs(self.land_x-self.x))
        # y_to_surface = self.impact()
        # d_to_land = abs(abs(self.land_x-self.x)) 
        if self.sequence is None:
            print("self.sequence 1", file=sys.stderr, flush=True)
            self.sequence = "drift_x"
            self.phase = 1
            self.new_theta = (-1 if self.land_x > self.x else 1)*abs(round(math.degrees(math.acos((self.gravity)/self.thrust_max))))
            new_ax = 4*math.sin(math.degrees(self.new_theta))
            time_to_speed = abs((self.lim_x - abs(self.velocity_x))/new_ax)
            print(f"a_x = {new_ax} angle = {self.new_theta} time to speed = {time_to_speed}", file=sys.stderr, flush=True)
        if self.sequence=="drift_x":
            new_angle,new_thrust = self.drift_x()
        elif self.sequence=="slow_x":
            new_angle,new_thrust = self.slow_x()
        elif self.sequence=="rise":
            new_angle,new_thrust = self.rise()
        elif self.sequence=="Landing":
            new_angle,new_thrust = self.landing()
        fall = self.spelunk()
        if fall is not None:
            new_angle, new_thrust = fall
        if not using_vscode:
            self.time+=1
            print(new_angle, new_thrust)
        else:
            self.Move(new_angle,new_thrust)
    def drift_x(self):
        if self.phase==1:
            if abs(abs(self.velocity_x)-self.lim_x)<=3:
                self.phase = 2
            elif abs(self.velocity_x)>self.lim_x and abs(self.distance(self.land_x,self.land_y)[1])<=1000:
                self.sequence="slow_x"
                return self.slow_x()
            else:
                new_angle=self.new_theta*(-1 if (abs(self.velocity_x)>self.lim_x) else 1)
                distances = self.distance(self.land_x,self.land_y)
                if abs(distances[2]) < abs(distances[1]) and abs(distances[1])>=self.land_xrad:
                    new_angle = 0
                
                print("phase 1", self.rotate, self.new_theta, file=sys.stderr, flush=True)

                new_thrust = 4
                # else:
                #     new_thrust = 4
        if self.phase==2:
            
            print("UH", abs(abs(self.land_x-self.x)-self.land_xrad),abs(abs(self.land_x-self.x_start)-self.land_xrad)//2, file=sys.stderr, flush=True)
            print("UH", abs(self.distance(self.land_x,self.land_y)[1]),abs(self.land_x-self.x)//2, file=sys.stderr, flush=True)
            
            try:
                if d_phase_1>0:
                    pass
            except NameError:
                d_phase_1=self.land_xrad-500
            if d_phase_1+500 >= abs(self.land_x-self.x):
                print("This is dangerous. Be careful", file=sys.stderr, flush=True)
                print("self.phase 3\nPHASE 3 self.phase 3\nPHASE 3 self.phase 3 self.phase 3\nPHASE 3 self.phase 3\nPHASE 3", file=sys.stderr, flush=True)
                self.phase=3
            else:
                print("self.phase 2!", file=sys.stderr, flush=True)
                # if timers[0] >= timers[1]:
                #     new_angle = 0
                #     if self.rotate != new_angle:
                #         new_thrust=0
                #     else:
                #         if abs(self.velocity_y)>=self.lim_y//2 and self.velocity_y<=self.lim_y//2:
                #             new_thrust = 4
                #             timers[1]+=1
                #         elif self.velocity_y>=0:
                #             new_thrust=0
                #         elif abs(self.velocity_y)<=self.lim_y:
                #             new_thrust=3
                # else:
                new_angle=0
                if abs(self.velocity_y)>=self.lim_y-self.lim_y*.25:
                    new_thrust=4 if self.velocity_y<5 else 3
                elif abs(self.velocity_y)<=self.lim_y//2:
                    new_thrust=4 if self.velocity_y<0 else 3
                else:
                    new_thrust=4

        if self.phase==3:
            print("phase 3", file=sys.stderr, flush=True)
            new_thrust=4
            if abs(self.velocity_x)>2:
                # new_angle=(self.new_theta*(-1 if self.x>self.land_x else 1))//2
                try:
                    new_angle = -round(math.degrees(math.atan(self.velocity_x/(self.velocity_y))))
                except ZeroDivisionError:
                    new_angle = (0 if self.velocity_y> 0 else 0)
            # elif abs(self.velocity_x)<=1 and abs(self.velocity_x)>0:
            #     new_angle=(self.new_theta*(-1 if self.x>self.land_x else 1))//4
                self.sequence = "slow_x"
                return self.slow_x()
            else:
                new_angle=0
                print("LANDING self.sequence COMMENCE", file=sys.stderr, flush=True)
                self.sequence = "Landing"
                return self.landing()
        return(new_angle, new_thrust)
    def slow_x(self):
        if (abs(self.velocity_x)>=self.lim_x):
            print("Slowing", file=sys.stderr, flush=True)
            #this was the working line before# new_angle=round(self.new_theta*(-.75 if (abs(self.velocity_x)>(self.lim_x)) else -0.5))#*(2 if abs(self.distance(self.land_x,self.land_y)[1])<=self.land_xrad*2 and abs(self.velocity_x)>=2*self.lim_x else 1)
            try:
                # new_angle = round(math.degrees(math.atan(((-1 if self.velocity_y< 0 else 1)*abs(self.velocity_y-self.lim_y))/((-1 if self.velocity_x> 0 else 1)*abs(self.velocity_x-self.lim_x)))))
                new_angle = -round(math.degrees(math.atan(-self.velocity_x/abs(self.velocity_y))))
                # if new_angle>5:
                #     new_angle-=5
                # elif new_angle<5:
                #     new_angle+=5
            except ZeroDivisionError:
                new_angle = (0 if self.velocity_y> 0 else 0)
            # new_angle=22*(-1 if self.x>self.land_x else 1)
            new_thrust=4 if self.rotate>=-5 and new_angle>=-5 or self.rotate<=5 and new_angle<=5  else 0
        elif (self.land_x>self.x and self.velocity_x>0 or self.land_x<self.x and self.velocity_x<0) and abs(self.land_x-self.x)>=self.land_xrad:
            print("Reversing", file=sys.stderr, flush=True)
            #this was the working line before# new_angle=round(self.new_theta*(-.75 if (abs(self.velocity_x)>(self.lim_x)) else -0.5))#*(2 if abs(self.distance(self.land_x,self.land_y)[1])<=self.land_xrad*2 and abs(self.velocity_x)>=2*self.lim_x else 1)
            try:
                # new_angle = round(math.degrees(math.atan(((-1 if self.velocity_y< 0 else 1)*abs(self.velocity_y-self.lim_y))/((-1 if self.velocity_x> 0 else 1)*abs(self.velocity_x-self.lim_x)))))
                new_angle = -round(math.degrees(math.atan(self.velocity_x/(self.velocity_y))))
                if new_angle>5:
                    new_angle-=5
                elif new_angle<5:
                    new_angle+=5
            except ZeroDivisionError:
                new_angle = (0 if self.velocity_y> 0 else 0)
            # new_angle=22*(-1 if self.x>self.land_x else 1)
            new_thrust=4 if self.rotate>=-5 and new_angle>=-5 or self.rotate<=5 and new_angle<=5  else 0
        else:
            if self.land_xleft<=self.x<=self.land_xright:
                self.sequence = "Landing"
                return self.landing()
            else:
                print("replaced the slow sequence with drift!", file=sys.stderr, flush=True)
                self.sequence, self.phase = "drift_x", 1
                return self.drift_x()
        return(new_angle, new_thrust)
    def landing(self):
        print("landing!", file=sys.stderr, flush=True) 
        new_angle=0 if self.impact()<=500 or self.velocity_y==0 else -round(math.degrees(math.atan(self.velocity_x/(self.velocity_y)))) #or abs(self.velocity_x)<=self.lim_x//2
        new_thrust=1 if abs(self.velocity_y)<self.lim_y and -self.velocity_y>1 else 3
        if abs(self.distance(self.land_x,self.land_y)[2])>1000:
            if abs(self.velocity_y)<=self.lim_y:
                new_thrust = 3
            else:
                if abs(self.velocity_y)>=self.lim_y:
                    new_thrust = 4
                else:
                    new_thrust = 3
        elif abs(self.distance(self.land_x,self.land_y)[1])<=100:
            new_thrust=4
        else:
            new_thrust=2 if self.velocity_y>-5 else 4
        return(new_angle, new_thrust)
    def rise(self):
        print("Rising!", file=sys.stderr, flush=True)
        if self.land_y+500>=self.y:# or self.y-self.land_y<=500:
            new_angle = 0
            new_thrust=4
        else:
            self.sequence, self.phase = "drift_x", 1
            return self.drift_x()
        return(new_angle, new_thrust)
    def Hover(self):
        pass
    def Slam(self):
        pass
    # def Landing(self):
    #     pass
    def Climb(self):
        pass
    def Stop(self):
        pass
    def quadratic(self, a,b,c):
        if a!=0:
            first=-b/(2*a)
            second = b**2-4*a*c
            if second < 0:
                print("ERRROR, b is too small", file=sys.stderr, flush=True)
                return(None)
            else:
                second = math.sqrt(second)/2*a
                answers = [first-second, first+second]
                answers.sort(reverse=True)
                return answers
        else:
            if b!=0:
                return [-c/b]
            else:
                return [c]
    def y_at_path(self,this_angle=None,this_thrust=None, this_vx=None, this_vy=None, this_x=None, this_y=None, that_x=None, that_y=None):
        this_angle = self.rotate if this_angle is None else this_angle
        this_thrust = self.power if this_thrust is None else this_thrust
        this_vx= self.velocity_x if this_vx is None else this_vx
        this_vy= self.velocity_y if this_vy is None else this_vy
        this_x= self.x if this_x is None else this_x
        this_y= self.y if this_y is None else this_y
        that_x= self.land_x if that_x is None else that_x
        that_y= self.land_y if that_y is None else that_y
        a,b,c = this_thrust*math.sin(math.radians(this_angle))/2, this_vx, this_x-that_x
        time_solutions = self.quadratic(a,b,c)
        answers = []
        # print(time_solutions)
        for solution in time_solutions:
            answers.append(that_y + solution*this_vy + solution**2*(this_thrust*math.cos(math.radians(this_angle))-self.gravity)/2)
        print(answers, file=sys.stderr, flush=True)
        return
    def Move(self, new_angle, new_thrust):
            # x, y, velocity_x, velocity_y, fuel, rotate, power, new_angle, new_thrust = [i for i in input_list]
            # print(x, y, velocity_x, velocity_y, fuel, rotate, power, new_angle, new_thrust, file=sys.stderr, flush=True)
            self.rotate=new_angle if abs(self.rotate-new_angle)<=15 else (self.rotate+15 if new_angle>self.rotate else self.rotate-15)
            new_thrust = self.power+(1 if new_thrust>self.power else (0 if new_thrust==self.power else -1))
            self.power=min(self.fuel,new_thrust)
            self.fuel=max(self.fuel-self.power,0)
            

            self.velocity_x=self.velocity_x+self.power*math.sin(math.radians(-self.rotate))
            self.velocity_y=self.velocity_y+self.power*math.cos(math.radians(-self.rotate))-self.gravity

            self.x+=round(self.velocity_x,3)
            self.y+=round(self.velocity_y,3)
            self.time+=1
            print(f"t={self.time}, x={self.x}, y={self.y}, vx={self.velocity_x}, vy={self.velocity_y}, f={self.fuel}, r={self.rotate}, p={self.power}", file=sys.stderr, flush=True)
            # print(self.slopes, file=sys.stderr, flush=True)
            result = self.impact()
            if result:
                if result=="success":
                    print("You landed! Good-bye", file=sys.stderr, flush=True)
                    self.stopme = True
                else:
                    # params=[self.x, self.y, self.velocity_x, self.velocity_y, self.fuel, self.rotate, self.power]
                    self.Control()
            else:
                print("You are dead. Good-bye", file=sys.stderr, flush=True)
                self.stopme = True
    def impact(self):
        if self.x<0 or self.x>6999 or self.y<0 or self.y>3000:
            print("OUT OF BOUNDS! x =",self.x,"y =",self.y, file=sys.stderr, flush=True)
            return False
        for i in range(len(self.surface)-1):
            if self.surface[i][0]<=self.x<=self.surface[i+1][0]:
                # print("WeRHere",self.slopes[i],self.surface[i][0],self.x,self.surface[i+1][0], file=sys.stderr, flush=True)
                y_at_land_x = self.surface[i][1]+self.slopes[i]*(self.x-self.surface[i][0])
                # print(y_at_land_x, file=sys.stderr, flush=True)
                clearance = self.y-y_at_land_x
                if clearance<=0:
                    if abs(self.velocity_x)>self.lim_x or abs(self.velocity_y)>self.lim_y:
                        print(f"CRASH! x,y=({self.x},{self.y}) (vx,vy) = ({self.velocity_x},{self.velocity_y}) y_at_land_x = {y_at_land_x}", file=sys.stderr, flush=True)
                        print(f"{i} {self.slopes}", file=sys.stderr, flush=True)
                        return False
                    elif self.slopes[i]==0:
                        print("LANDED",self.velocity_x,self.velocity_y,self.x,self.y, file=sys.stderr, flush=True)
                        return True
                    else:
                        print("CRASH!",self.velocity_x,self.velocity_y,self.x,self.y, file=sys.stderr, flush=True)
                        return False
                else:
                    return clearance


lander = Lander()
while 1:
    # input_list = [int(i) for i in input().split()]
    lander.refresh()
    if lander.stopme:
        break
