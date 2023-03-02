import sys
import math


class Locations:
    def __init__(self, x, y):
        self.x = x
        self.y = y
class Borders:
    def __init__(self, MinX, MaxX, MinY, MaxY):
        self.MinX = MinX
        self.MaxX = MaxX
        self.MinY = MinY
        self.MaxY = MaxY

def Search(bomb_dir):
    global Bat, Bounds
    if Bounds.MinY != Bounds.MaxY:
        if "U" in bomb_dir:
            Bounds.MaxY = Bat.y - 1
        elif "D" in bomb_dir:
            Bounds.MinY = Bat.y + 1
    if Bounds.MinX != Bounds.MaxX:
        if "L" in bomb_dir:
            Bounds.MaxX = Bat.x - 1
        elif "R" in bomb_dir:
            Bounds.MinX = Bat.x + 1
    Bat.x = (Bounds.MinX + Bounds.MaxX)//2
    Bat.y = (Bounds.MinY + Bounds.MaxY)//2


# w: width of the building.
# h: height of the building.
w, h = [int(i) for i in input().split()]
print("w: ",w,"h: ",h, file=sys.stderr, flush=True)
n = int(input())  # maximum number of turns before game over.
x0, y0 = [int(i) for i in input().split()]
Bounds = Borders(0,w,0,h)
Bat = Locations(x0, y0)



# game loop
while True:
    # the direction of the bombs from batman's current location (U, UR, R, DR, D, DL, L or UL)
    bomb_dir = input()
    Search(bomb_dir)
    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)

    # the location of the next window Batman should jump to.
    print("{0} {1}".format(Bat.x, Bat.y))
