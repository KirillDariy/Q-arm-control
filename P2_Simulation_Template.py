ip_address = 'localhost' # Enter your IP Address here
project_identifier = 'P2B' # Enter the project identifier i.e. P2A or P2B
#--------------------------------------------------------------------------------
import sys
import time
import random
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
arm = qarm(project_identifier,ip_address,QLabs,hardware)
potentiometer = potentiometer_interface()
#--------------------------------------------------------------------------------
# STUDENT CODE BEGINS
#---------------------------------------------------------------------------------

timedelay = 1.5 # In seconds

# pickup the container off the ground
def pickup(id):
    arm.spawn_cage(id)
    arm.move_arm(0.563,0.056,0.013)
    time.sleep(timedelay)
    if id < 4: # small
        arm.control_gripper(35)
    else: # big
        arm.control_gripper(28)
    time.sleep(timedelay + 0.75)
    returnhome()

# drop off the container
def dropoff(size, colour, id): 
    if size == 1: # Small size
        if id == 1 or id == 2:
            arm.rotate_elbow(-20)
            arm.rotate_shoulder(40)
            time.sleep(timedelay)
            arm.control_gripper(-35)
        elif id == 3:
            arm.rotate_elbow(-30)
            arm.rotate_shoulder(50)
            time.sleep(timedelay)
            arm.control_gripper(-35)

    elif size == 2: # Big size
        arm.open_autoclave(colour)
        if id == 4: # Red 
            arm.move_arm(0.0, -0.388, 0.2)
        elif id == 5: #Green
            arm.move_arm(0.0, 0.388, 0.2)
        elif id == 6: # Blue
            arm.move_arm(-0.395, 0.158, 0.2)

        time.sleep(timedelay)
        arm.control_gripper(-28)
        time.sleep(timedelay+1)
        arm.open_autoclave(colour, False)

    time.sleep(timedelay)
    returnhome()
    
# Check for arm and autoclave position
def checkPos(colourList, counter):
    position = arm.effector_position()
    if arm.check_autoclave(colourList[counter]) and colourList[counter] == "red":
        arm.move_arm(0.0,-0.406,position[2])
        return True
    if arm.check_autoclave(colourList[counter]) and colourList[counter] == "green":
        arm.move_arm(0.0,0.406,position[2])
        return True
    if arm.check_autoclave(colourList[counter]) and colourList[counter] == "blue":
        arm.move_arm(-0.382,0.139,position[2])
        return True
    return False

# Return home/default position
def returnhome(): 
    arm.move_arm(0.406,0.0,0.483)

# Randomize the order of the containers being spawned
def randomizeContainer():
    myList = [1,2,3,4,5,6]
    random.shuffle(myList)
    return myList

# Turn the q-arm right using the potentiometers
def rotateRight(degree, prevdegree):
    difference = degree - prevdegree
    arm.rotate_base(difference * 200 * -1)
    return degree

# Turn the q-arm left using the potentiometers
def rotateLeft(degree, prevdegree):
    difference = prevdegree - degree
    if difference*351 < 175 and difference*351 > -175: # Checking for valid arm rotation range
        arm.rotate_base(difference * 351)
    return degree

# Main function
def main():
    # Instantiate the variables
    pickupBool = True
    counter = 0
    prevdegree1 = 0.55
    prevdegree2 = -0.45
    timerList = []
    colourList = []
    myList = randomizeContainer()
    
    arm.activate_autoclaves()
    
    # Give a colour to the randomized list of container ID's and add it to a different list
    for i in range(6):
        if myList[i] == 1 or myList[i] == 4:
            colourList.append("red")
        elif myList[i] == 2 or myList[i] == 5:
            colourList.append("green")
        elif myList[i] == 3 or myList[i] == 6:
            colourList.append("blue")
    
    while counter < 6: # Run this code until we reach the 6th container

        leftPotent = potentiometer.left()
        rightPotent = potentiometer.right()

        # Buffer to make sure that the user actually wants to select that potentiometer region
        timerList.append(leftPotent)
        runCode = False
        if timerList[:-1] == timerList[1:] and len(timerList) > 15: 
            timerList = []
            runCode = True
        elif len(timerList) > 15:
            timerList = []

        ### Left potentiometer ###
        # Pickup the container
        if leftPotent == 0.5 and rightPotent == 0.5 and pickupBool: 
            pickup(myList[counter])
            pickupBool = False
            time.sleep(timedelay)

        # Dropoff small items #ID 1-3
        elif leftPotent >= 0.55 and leftPotent < 1 and runCode and checkPos(colourList, counter) and myList[counter] < 4: 
            time.sleep(timedelay)
            dropoff(1, colourList[counter], myList[counter])
            returnhome()
            pickupBool = True
            counter += 1

        # Dropoff big items #ID 4-6
        elif leftPotent == 1 and runCode and checkPos(colourList, counter) and myList[counter] >= 4: 
            time.sleep(timedelay)
            dropoff(2, colourList[counter], myList[counter])
            returnhome()
            pickupBool = True
            counter += 1

        ### Right potentiometer ###
        # Rotate the arm to the right
        if rightPotent >= 0.55 and not pickupBool:
            prevdegree1 = rotateRight(rightPotent, prevdegree1)

        # Rotate the arm to the left
        elif rightPotent <= 0.45 and not pickupBool:
            prevdegree2 = rotateLeft(rightPotent, prevdegree2)

        # Return the arm to its home position
        elif rightPotent == 0.5:
            returnhome()
            prevdegree1 = 0.55
            prevdegree2 = -0.45
    
    arm.deactivate_autoclaves()

main()
    
#---------------------------------------------------------------------------------
# STUDENT CODE ENDS
#---------------------------------------------------------------------------------
