# get inputs
# map out terrain, get: my_land (list of all x,y points for surface); self.slopes (list of self.slopes for each section)
# identify landing pad, get: land_left,land_mid,land_right,land_height
# create distance function for easy calculations
# def toLand():
import sys
import math

# Constants
using_vscode = True  # Use True to run the code in VSCode
GRAVITY = 3.711
THRUST_MAX = 4

# Fake inputs (for testing purposes only)
fake_input0 = 7
fake_input1 = [
    "0 100",
    "1000 500",
    "1500 1500",
    "3000 1000",
    "4000 150",
    "5500 150",
    "6999 800",
]
fake_input2 = "2500 2700 0 0 550 0 0"

# Class for the Lander
class Lander:
    def __init__(
        self,
        x=None,
        y=None,
        velocity_x=None,
        velocity_y=None,
        fuel=None,
        rotate=None,
        power=None,
    ):
        # Set initial values
        self.lim_x, self.lim_y = 20, 40  # Limit coordinates for the lander
        self.surface = []  # List of surface points
        self.slopes = []  # List of slopes for each section
        self.obstacles = []  # List of obstacles in the landing area
        self.stopme = False  # Flag to stop the simulation
        self.time = 0  # Time elapsed in the simulation
        self.sequence = None  # Sequence of actions for the lander
        self.land_xleft = None  # X-coordinate of the left boundary of the landing area
        self.land_xright = (
            None  # X-coordinate of the right boundary of the landing area
        )
        self.land_x = None  # X-coordinate of the center of the landing area
        self.land_y = None  # Y-coordinate of the landing area
        self.land_xrad = None  # Radius of the landing area
        self.direction = None  # Direction of approach ("LEFT" or "RIGHT")

        # Read the input and populate the surface and slopes lists
        surface_n = fake_input0 if using_vscode else int(input())
        for i in range(surface_n):
            self.surface.append(
                [
                    int(j)
                    for j in (
                        fake_input1[i].split() if using_vscode else input().split()
                    )
                ]
            )
            if i >= 1:
                prev, this = self.surface[-2], self.surface[-1]
                self.slopes.append(round((this[1] - prev[1]) / (this[0] - prev[0]), 5))
                if this[1] == prev[1] and abs(this[0] - prev[0]) >= 1000:
                    # If the slope is undefined (flat surface), set the landing area
                    print(
                        f"x from {prev[0]} to {this[0]} at y={prev[1]}",
                        file=sys.stderr,
                        flush=True,
                    )
                    self.land_xleft = min(prev[0], this[0])
                    self.land_xright = max(prev[0], this[0])
                    self.land_x = (prev[0] + this[0]) // 2
                    self.land_y = prev[1]
                    self.land_xrad = self.land_xright - self.land_x
                    landing_index = i
        print("Surface = ", self.surface, file=sys.stderr, flush=True)

        # Loop through all points on the surface
        for k, point in enumerate(self.surface):
            # If the point is within the landing zone and not at the landing y-coordinate
            if (self.land_xleft <= point[0] <= self.land_xright) and point[
                1
            ] != self.land_y:
                # Add the point and its index to the list of obstacles
                self.obstacles.append(point + [k])

        # If there are any obstacles
        if len(self.obstacles) > 0:
            # Initialize leftmost and rightmost points as very far to the right
            self.leftmost, self.rightmost = [9999, 9999], [9999, 9999]

            # Loop through all obstacles and find the leftmost and rightmost ones relative to the landing zone
            for k, point in enumerate(self.obstacles):
                if abs(point[0] - self.land_xleft) <= abs(
                    self.leftmost[0] - self.land_xleft
                ):
                    self.leftmost = point
                if abs(point[0] - self.land_xright) <= abs(
                    self.rightmost[0] - self.land_xright
                ):
                    self.rightmost = point

            # Print information about the obstacles and bounds to the error stream
            print(
                f"Obstacles = {self.obstacles}, left/right bounds = {self.leftmost} and {self.rightmost}",
                file=sys.stderr,
                flush=True,
            )

            # Determine the direction of approach based on the location of the leftmost obstacle
            if self.leftmost[2] < landing_index:
                self.direction = "RIGHT"
                leftof = self.rightmost
                rightof = self.surface[landing_index + 1]
            else:
                self.direction = "LEFT"
                leftof = self.surface[landing_index - 2]
                rightof = self.leftmost

            # Calculate the slope of the lines connecting the landing zone to the leftmost, mid, and rightmost obstacles
            self.leftbound = (
                0
                if leftof[0] == self.land_xleft
                else (leftof[1] - self.land_y) / (leftof[0] - self.land_xleft)
            )
            self.midbound = (
                0
                if rightof[0] == self.land_x
                else (leftof[1] - self.land_y) / (leftof[0] - self.land_x)
            )
            self.rightbound = (
                0
                if rightof[0] == self.land_xright
                else (rightof[1] - self.land_y) / (rightof[0] - self.land_xright)
            )

            # Print information about the angle of approach and bounds to the error stream
            print(
                f"angle of approach should be {self.direction}",
                self.leftbound,
                self.midbound,
                self.rightbound,
                file=sys.stderr,
                flush=True,
            )

    def spelunk(self):
        # Calculate the three boundary lines
        leftline = self.leftbound * (self.x - self.land_xleft + 10) + self.land_y
        midline = self.midbound * (self.x - self.land_x + 10) + self.land_y
        rightline = self.rightbound * (self.x - self.land_xright + 10) + self.land_y

        # Debugging statements
        print(
            "spelunk", self.x, self.y, leftline, rightline, file=sys.stderr, flush=True
        )

        # Check if the lander is in the strike zone
        if rightline <= self.y <= leftline or rightline >= self.y >= leftline:
            print(
                "WE'RE IN THE STRIKEZONE!",
                min(self.leftbound, self.rightbound),
                self.velocity_y / self.velocity_x,
                max(self.leftbound, self.rightbound),
                file=sys.stderr,
                flush=True,
            )

            # Decide whether to thrust or not
            if (
                min(self.leftbound, self.rightbound)
                <= self.velocity_y / self.velocity_x
            ):
                return 0, 4
            elif self.velocity_y / self.velocity_x <= max(
                self.leftbound, self.rightbound
            ):
                return 0, 3
            else:
                return 0, 3

        # Check if the lander is in the danger zone
        elif leftline <= self.y <= midline or leftline >= self.y >= midline:
            print("WE'RE IN THE DANGERZONE!", file=sys.stderr, flush=True)
            return 0, 4

        # Check if the lander is going the wrong way
        elif (
            self.y >= midline or self.x <= self.land_xright
        ) and self.y > self.rightmost[1]:
            print("WE'RE GOING THE WRONG WAY!", file=sys.stderr, flush=True)
            return 90, 4

        # Otherwise, take action based on the lander's velocity
        else:
            if abs(self.velocity_x) >= self.lim_x:
                return (22 if self.velocity_x > 0 else -22), 4
            return None

    def refresh(self):
        # Debugging statement
        print("refreshing", file=sys.stderr, flush=True)

        # Get the latest values of the lander's state
        if not using_vscode:
            (
                self.x,
                self.y,
                self.velocity_x,
                self.velocity_y,
                self.fuel,
                self.rotate,
                self.power,
            ) = [int(j) for j in input().split()]

        # Call the Control method to make decisions based on the current state
        if not self.stopme:
            self.Control()

    def distance(self, x1, y1, x0=None, y0=None):
        if x0 is None:
            x0 = self.x
        if y0 is None:
            y0 = self.y
        distance_x = x1 - x0
        distance_y = y1 - y0
        distance_to_point = math.sqrt(distance_x**2 + distance_y**2)
        print(
            "distancestuff",
            x1,
            y1,
            x0,
            y0,
            [distance_to_point, distance_x, distance_y],
            file=sys.stderr,
            flush=True,
        )
        return [distance_to_point, distance_x, distance_y]

    def Control(self):
        # Print debug message
        print("controlling", file=sys.stderr, flush=True)

        # Initialization phase
        if self.time == 0:
            print("time", file=sys.stderr, flush=True)
            self.sequence = None
            self.phase = None

            # Initialize input if not using VSCode
            if not using_vscode:
                (
                    self.x,
                    self.y,
                    self.velocity_x,
                    self.velocity_y,
                    self.fuel,
                    self.rotate,
                    self.power,
                ) = [int(j) for j in input().split()]

            # Set start positions and calculate distance to travel
            self.x_start, self.y_start = self.x, self.y
            self.velocity_x_start, self.velocity_y_start = (
                self.velocity_x,
                self.velocity_y,
            )
            x_to_travel, y_to_travel = (
                abs(abs(self.land_x - self.x_start) - self.land_xrad),
                self.y - self.land_y,
            )
            print(
                f"self.x_start={self.x_start},self.y_start={self.y_start},self.velocity_x_start={self.velocity_x_start},self.velocity_y_start={self.velocity_y_start},x_to_travel={x_to_travel},y_to_travel={y_to_travel}",
                file=sys.stderr,
                flush=True,
            )

        # Initialize sequence and phase
        if self.sequence is None:
            print("self.sequence 1", file=sys.stderr, flush=True)
            self.sequence = "drift_x"
            self.phase = 1
            self.new_theta = (-1 if self.land_x > self.x else 1) * abs(
                round(math.degrees(math.acos((self.gravity) / self.thrust_max)))
            )
            new_ax = 4 * math.sin(math.degrees(self.new_theta))
            time_to_speed = abs((self.lim_x - abs(self.velocity_x)) / new_ax)
            print(
                f"a_x = {new_ax} angle = {self.new_theta} time to speed = {time_to_speed}",
                file=sys.stderr,
                flush=True,
            )

        # Choose the next action based on the sequence
        if self.sequence == "drift_x":
            new_angle, new_thrust = self.drift_x()
        elif self.sequence == "slow_x":
            new_angle, new_thrust = self.slow_x()
        elif self.sequence == "rise":
            new_angle, new_thrust = self.rise()
        elif self.sequence == "Landing":
            new_angle, new_thrust = self.landing()

        # Check if the lander has fallen into a danger zone
        fall = self.spelunk()
        if fall is not None:
            new_angle, new_thrust = fall

        # Increment the time step and print the new action
        if not using_vscode:
            self.time += 1
            print(new_angle, new_thrust)
        else:
            self.Move(new_angle, new_thrust)

    def drift_x(self):
        new_angle = 0  # initialize new_angle
        new_thrust = 4  # initialize new_thrust

        if self.phase == 1:
            # Check if the rocket is close to the maximum x velocity limit
            if abs(abs(self.velocity_x) - self.lim_x) <= 3:
                self.phase = 2  # If so, move to phase 2
            # Check if the rocket is exceeding the x velocity limit and within 1000 units of the landing zone
            elif (
                abs(self.velocity_x) > self.lim_x
                and abs(self.distance(self.land_x, self.land_y)[1]) <= 1000
            ):
                self.sequence = "slow_x"  # If so, start a new sequence and return the result of the slow_x method
                return self.slow_x()
            else:
                # Determine the new angle based on the rocket's velocity and distance from the landing zone
                new_angle = self.new_theta * (
                    -1 if (abs(self.velocity_x) > self.lim_x) else 1
                )
                distances = self.distance(self.land_x, self.land_y)
                if (
                    abs(distances[2]) < abs(distances[1])
                    and abs(distances[1]) >= self.land_xrad
                ):
                    new_angle = 0  # If the rocket is oriented towards the landing zone, set new_angle to 0

                # Print debug information
                print(
                    "phase 1", self.rotate, self.new_theta, file=sys.stderr, flush=True
                )

        elif self.phase == 2:
            # Print debug information
            print("self.phase 2!", file=sys.stderr, flush=True)

            # Check if the rocket is close enough to the landing zone to move to phase 3
            d_phase_1 = self.land_xrad - 500
            if d_phase_1 + 500 >= abs(self.land_x - self.x):
                print("This is pretty dangerous, let's be careful", file=sys.stderr, flush=True)
                print(
                    "self.phase 3\nPHASE 3 self.phase 3\nPHASE 3 self.phase 3 self.phase 3\nPHASE 3 self.phase 3\nPHASE 3",
                    file=sys.stderr,
                    flush=True,
                )
                self.phase = 3
            else:
                # Determine the new thrust based on the rocket's y velocity
                if abs(self.velocity_y) >= self.lim_y - self.lim_y * 0.25:
                    new_thrust = 4 if self.velocity_y < 5 else 3
                elif abs(self.velocity_y) <= self.lim_y // 2:
                    new_thrust = 4 if self.velocity_y < 0 else 3
                else:
                    new_thrust = 4

        elif self.phase == 3:
            # Print debug information
            print("phase 3", file=sys.stderr, flush=True)

            # Determine the new angle based on the rocket's x and y velocities
            if abs(self.velocity_x) > 2:
                try:
                    new_angle = -round(
                        math.degrees(math.atan(self.velocity_x / (self.velocity_y)))
                    )
                except ZeroDivisionError:
                    new_angle = 0 if self.velocity_y > 0 else 0

                # Start a new sequence and return the result of the slow_x method
                self.sequence = "slow_x"
                return self.slow_x()
            else:
                # Set new_angle to 0 and start the landing sequence
                new_angle = 0
                print("LANDING self.sequence COMMENCE", file=sys.stderr, flush=True)
                self.sequence = "Landing"
                return self.landing()
        return (new_angle, new_thrust)

    def slow_x(self):
        # Check if current x velocity is greater than the limit
        if abs(self.velocity_x) >= self.lim_x:
            # Slow down the lander and print status
            print("Slowing", file=sys.stderr, flush=True)

            # Calculate new angle based on current velocity
            try:
                new_angle = -round(
                    math.degrees(math.atan(-self.velocity_x / abs(self.velocity_y)))
                )
            except ZeroDivisionError:
                new_angle = 0 if self.velocity_y > 0 else 0

            # Adjust thrust based on current angle and rotation
            new_thrust = (
                4
                if self.rotate >= -5
                and new_angle >= -5
                or self.rotate <= 5
                and new_angle <= 5
                else 0
            )

        # Check if lander needs to reverse direction
        elif (
            self.land_x > self.x
            and self.velocity_x > 0
            or self.land_x < self.x
            and self.velocity_x < 0
        ) and abs(self.land_x - self.x) >= self.land_xrad:
            # Reverse the lander and print status
            print("Reversing", file=sys.stderr, flush=True)

            # Calculate new angle based on current velocity
            try:
                new_angle = -round(
                    math.degrees(math.atan(self.velocity_x / (self.velocity_y)))
                )
                # Add or subtract 5 degrees to the new angle for small adjustments
                if new_angle > 5:
                    new_angle -= 5
                elif new_angle < 5:
                    new_angle += 5
            except ZeroDivisionError:
                new_angle = 0 if self.velocity_y > 0 else 0

            # Adjust thrust based on current angle and rotation
            new_thrust = (
                4
                if self.rotate >= -5
                and new_angle >= -5
                or self.rotate <= 5
                and new_angle <= 5
                else 0
            )

        # Lander is within landing range and needs to land
        elif self.land_xleft <= self.x <= self.land_xright:
            self.sequence = "Landing"
            return self.landing()

        # Lander is within range but does not need to land, drift instead
        else:
            print(
                "replaced the slow sequence with drift!",
                file=sys.stderr,
                flush=True,
            )
            self.sequence, self.phase = "drift_x", 1
            return self.drift_x()

        # Return new angle and thrust
        return (new_angle, new_thrust)

    def landing(self):
        # Print debug information
        print("landing!", file=sys.stderr, flush=True)

        # Calculate new landing angle
        if self.impact() <= 500 or self.velocity_y == 0:
            new_angle = 0
        else:
            new_angle = -round(
                math.degrees(math.atan(self.velocity_x / (self.velocity_y)))
            )

        # Calculate new landing thrust
        if abs(self.velocity_y) < self.lim_y and -self.velocity_y > 1:
            new_thrust = 1
        else:
            if abs(self.distance(self.land_x, self.land_y)[2]) > 1000:
                if abs(self.velocity_y) <= self.lim_y:
                    new_thrust = 3
                else:
                    new_thrust = 4
            elif abs(self.distance(self.land_x, self.land_y)[1]) <= 100:
                new_thrust = 4
            else:
                new_thrust = 2 if self.velocity_y > -5 else 4

        # Return tuple of new angle and thrust
        return (new_angle, new_thrust)

    def rise(self):
        # Print debug information
        print("Rising!", file=sys.stderr, flush=True)

        if self.land_y + 500 >= self.y:
            # If the lander is within 500 units of the landing area, keep the angle at 0 and use full thrust to rise
            new_angle = 0
            new_thrust = 4
        else:
            # Otherwise, switch to drifting in the x direction
            self.sequence, self.phase = "drift_x", 1
            return self.drift_x()

        # Return tuple of new angle and thrust
        return (new_angle, new_thrust)

    def quadratic(self, a, b, c):
        if a != 0:
            # If the quadratic formula can be used, solve for the roots of the equation
            first = -b / (2 * a)
            second = b**2 - 4 * a * c
            if second < 0:
                # If the square root of a negative number is attempted, return None
                print("ERROR: b is too small", file=sys.stderr, flush=True)
                return None
            else:
                second = math.sqrt(second) / 2 * a
                answers = [first - second, first + second]
                answers.sort(reverse=True)
                return answers
        else:
            # If the equation is linear, solve for the root
            if b != 0:
                return [-c / b]
            else:
                # If the equation is a constant, print an error message and return the constant
                print(
                    "ERROR: You did not provide a variable to be solved for.",
                    file=sys.stderr,
                    flush=True,
                )
                return [c]

    def y_at_path(
        self,
        this_angle=None,  # Optional parameter for the angle of the rocket
        this_thrust=None,  # Optional parameter for the thrust of the rocket
        this_vx=None,  # Optional parameter for the velocity x of the rocket
        this_vy=None,  # Optional parameter for the velocity y of the rocket
        this_x=None,  # Optional parameter for the x coordinate of the rocket
        this_y=None,  # Optional parameter for the y coordinate of the rocket
        that_x=None,  # Optional parameter for the x coordinate of the target
        that_y=None,  # Optional parameter for the y coordinate of the target
    ):
        # Set default values if optional parameters are not provided
        this_angle = self.rotate if this_angle is None else this_angle
        this_thrust = self.power if this_thrust is None else this_thrust
        this_vx = self.velocity_x if this_vx is None else this_vx
        this_vy = self.velocity_y if this_vy is None else this_vy
        this_x = self.x if this_x is None else this_x
        this_y = self.y if this_y is None else this_y
        that_x = self.land_x if that_x is None else that_x
        that_y = self.land_y if that_y is None else that_y

        # Calculate the coefficients for the quadratic equation
        a = this_thrust * math.sin(math.radians(this_angle)) / 2
        b = this_vx
        c = this_x - that_x

        # Solve the quadratic equation to get the time of impact
        time_solutions = self.quadratic(a, b, c)

        # Calculate the y coordinate at each time of impact
        answers = []
        for solution in time_solutions:
            y = (
                that_y
                + solution * this_vy
                + solution**2
                * (this_thrust * math.cos(math.radians(this_angle)) - self.gravity)
                / 2
            )
            answers.append(y)

        # Print the calculated y coordinates for debugging purposes
        print(answers, file=sys.stderr, flush=True)

        # Return the calculated y coordinates
        return answers

    def Move(self, new_angle, new_thrust):
        # Update the rotation angle
        self.rotate = (
            new_angle
            if abs(self.rotate - new_angle) <= 15
            else (self.rotate + 15 if new_angle > self.rotate else self.rotate - 15)
        )

        # Update the power level
        new_thrust = self.power + (
            1 if new_thrust > self.power else (0 if new_thrust == self.power else -1)
        )
        self.power = min(self.fuel, new_thrust)
        self.fuel = max(self.fuel - self.power, 0)

        # Update the velocity
        self.velocity_x = self.velocity_x + self.power * math.sin(
            math.radians(-self.rotate)
        )
        self.velocity_y = (
            self.velocity_y
            + self.power * math.cos(math.radians(-self.rotate))
            - self.gravity
        )

        # Update the position
        self.x += round(self.velocity_x, 3)
        self.y += round(self.velocity_y, 3)
        self.time += 1

        # Print current state
        print(
            f"t={self.time}, x={self.x}, y={self.y}, vx={self.velocity_x}, vy={self.velocity_y}, f={self.fuel}, r={self.rotate}, p={self.power}",
            file=sys.stderr,
            flush=True,
        )

        # Check for an impact
        result = self.impact()
        if result:
            if result == "success":
                # Landing success message
                print("You landed! Good-bye", file=sys.stderr, flush=True)
                self.stopme = True
            else:
                # Go back to the control method to try again
                self.Control()
        else:
            # Impact failure message
            print("You are dead. Good-bye", file=sys.stderr, flush=True)
            self.stopme = True


def impact(self):
    # Check if the lander is out of bounds
    if self.x < 0 or self.x > 6999 or self.y < 0 or self.y > 3000:
        print("OUT OF BOUNDS! x =", self.x, "y =", self.y, file=sys.stderr, flush=True)
        return False

    # Check if the lander crashes or lands on the surface
    for i in range(len(self.surface) - 1):
        # Check if the lander is within the bounds of the current surface segment
        if self.surface[i][0] <= self.x <= self.surface[i + 1][0]:
            # Calculate the height of the surface at the lander's x position
            y_at_land_x = self.surface[i][1] + self.slopes[i] * (
                self.x - self.surface[i][0]
            )
            # Calculate the clearance between the lander and the surface
            clearance = self.y - y_at_land_x

            # If the lander crashes, print a message and return False
            if clearance <= 0:
                if (
                    abs(self.velocity_x) > self.lim_x
                    or abs(self.velocity_y) > self.lim_y
                ):
                    print(
                        f"CRASH! x,y=({self.x},{self.y}) (vx,vy) = ({self.velocity_x},{self.velocity_y}) y_at_land_x = {y_at_land_x}",
                        file=sys.stderr,
                        flush=True,
                    )
                    print(f"{i} {self.slopes}", file=sys.stderr, flush=True)
                    return False
                elif self.slopes[i] == 0:
                    # If the lander lands successfully, print a message and return True
                    print(
                        "LANDED",
                        self.velocity_x,
                        self.velocity_y,
                        self.x,
                        self.y,
                        file=sys.stderr,
                        flush=True,
                    )
                    return True
                else:
                    # If the lander crashes, print a message and return False
                    print(
                        "CRASH!",
                        self.velocity_x,
                        self.velocity_y,
                        self.x,
                        self.y,
                        file=sys.stderr,
                        flush=True,
                    )
                    return False
            else:
                # If the lander is still in the air, return the clearance
                return clearance


if __name__ == "__main__":
    # Create a new Lander object
    lander = Lander()

    # Run the simulation loop
    while 1:
        # Get the input parameters and update the lander state
        # input_list = [int(i) for i in input().split()]
        lander.refresh()

        # Check if the simulation should stop
        if lander.stopme:
            break


"""
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
"""
