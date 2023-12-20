"""Defining file for all terminal interaction functions

This script defines the functions that facilitate the interaction between the
user and the program via the terminal.

This file contains the following major functions:

    * area_check - Prints a warning if an area is above a certain threshold
    * yes_no_choice - Presents a yes no [y/n] input space to the user
    * step_1_input - Create the explanations and input space for the network creatin step
    * step_2_input - Determines if the user would like to compute multiple variants
    * variant_input - User may enter input for several possible variants
    * standard_input - User may enter input for just one design
    * step_3_input - Create the explanations and input space for the SWMM file creation step
    * design_choice & uncertain_choice - User can tell system their preffered design
    * tester - Only used for testing purposes
"""
from numpy import (cos, sin, pi, array)
from vg import angle

def area_check(coords: list[float], threshold: int):
    """Checks wether a given area is larger than a certain threshold of km^2,
    and prints a warning if it is

    Args:
        coords (list[float]): north, south, east and west coordinates of an area
        threshold (int): The value to check against

    return area (float): The calculated area
    """
    def coord_vector(x, y):
        X = 6378 * cos(x * 2 * pi / 360) * cos(y * 2 * pi / 360)
        Y = 6378 * cos(x * 2 * pi / 360) * sin(y * 2 * pi / 360)
        Z = 6378 * sin(x * 2 * pi / 360)

        return array([X, Y, Z])
    
    top_right = coord_vector(coords[0], coords[2])
    bottom_right = coord_vector(coords[1], coords[2])
    top_left= coord_vector(coords[0], coords[3])

    hor_angle = angle(top_right, top_left)
    ver_angle = angle(top_right, bottom_right)   
    
    hor = hor_angle * 2 * pi / 360 * 6378
    ver = ver_angle * 2 * pi / 360 * 6378

    area = ver * hor

    if area > threshold:
        print("\nWARNING: The area you have selected may be larger than 5 km^2.\n\
This may cause a serious increase in runtime.")
        print("\nDo you wish to proceed with increased runtime? \n\
If you enter no, you may enter new coordinates.")
        choice = yes_no_choice()
        if choice == 'n':
            print("\n")
            coords = []
            coords, _ = coords_input()
    
    return area, coords



def yes_no_choice() -> str:
    """Presents the user with a yes no choice input line

    Returns:
        str: either "y" or "n", the choice of the user
    """

    try:
        choice = input("[y/n]: ").lower()

    except ValueError:
        print("\nWrong input type, please try again:")
        choice = yes_no_choice()

    if choice not in ["y", "n"]:
        print("\nWrong input type, please try again:")
        choice = yes_no_choice()

    return choice


def coords_input() -> list[float]:
    """Present the user with the input space for the bounding box coordinates

    Returns:
        list[float]: north, south, east and west coordinates
        area[float]: Area of the giving bounding box
    """

    try:
        north = float(input("Enter coordinates of the most northern point: "))
        south = float(input("Enter coordinates of the most southern point: "))
        east = float(input("Enter coordinates of the most eastern point: "))
        west = float(input("Enter coordinates of the most western point: "))
        coords = [north, south, east, west]

    except ValueError:
        print("\nThe input was not in the correct format (ex: 51.592)\nPlease try again:\n")
        coords = coords_input()

    # If north was entered in the south entry space, swap them
    if coords[0] < coords[1]:
        coords[0], coords[1] = coords[1], coords[0]

    # Same for east and west
    if coords[2] < coords[3]:
        coords[2], coords[3] = coords[3], coords[2]

    print(f"\nThe coordinates you entered are {coords}. Are these correct?")
    choice = yes_no_choice()

    if choice == "n":
        print("")
        coords = coords_input()

    area, checked_coords = area_check(coords, 5)

    return checked_coords, area


def manhole_space_input() -> int:
    """Present the user with a space to input the maximum allowable manhole spacing

    Returns:
        int: maximum allowable manhole spacing (in [m])
    """

    try:
        space = int(input("Maximum allowable manhole spacing: "))

    except ValueError:
        print("\nThe input was not in the correct format (ex: 20)\nPlease try again:\n")
        space = manhole_space_input()

    return space


def step_1_input():
    """Create the explanations and input space for the network creation step of the software

    Returns:
        tuple[list[float], int]: A list of the desired bounding box coordinates, and an integer
        value for the maximum allowable manhole spacing
        api_key[string]: The key for the google elevation API
        area[float]: Area of the given bounding box
    """


    print("\nWelcome To APDUDS!\n\n\
    To start please input the coordinates of the bounding box of the area \n\
    for which you want the preliminary design:\n\n\
    The inputs should be in degrees latitude and longitude, for example:\n\
    Enter coordinates of the most northern point: 51.9268\n")

    coords, area = coords_input()

    print(f"\nIn order for the system to use the google elevation API, an API key has to be given, please do so below. \n\
An API key can be generated from https://tinyurl.com/elevationapi")
    
    while True:
        try:
            api_key = input("API key: ")

        except ValueError:
            print(f"\n The value you entered is incorrect, please try again.")
            continue    
        else:
            break
   

    print("\nThe conduit network for the area you selected will \
now be calculated.\nA figure will appear, after which you can proceed to the next step.")

    return coords, api_key, area


def step_2_input():
    """Lets the user choose if we wants to create variants for the network of the given area or not.
    Then lets the user give the required settings.

    Returns:
        dict: The parameters for the system as given by the user
    """
    
    print("\n\nNow that the network has been generated, the user can choose wether it wants to \n\
create multiple networks for the given area or not.")
    print("\nThe iteration process works as follows. A set amount of variants are made based on \n\
design choices such as minimum depth and overflow points. From these variants you may \n\
pick one favourite with which variants for different design storms and ground \n\
imperviousness will be created. From this one network can be selected and exported as a SWMM file.")
    print("\nPlease enter wether you would like to make multiple iterations for the given area.")
    choice = yes_no_choice()

    if choice == "n":
        settings = standard_input()
    elif choice == "y":
        settings = variant_input()
 

    return settings

def variant_input():
    """Ask the user for multiple possible settings for different variations.

    Returns:
        dict: The parameters for the system as given by the user
    """


     
    settings = {}
    print("\nPlease enter the described information to enable the next set of calculation steps:")

    while True:
        try:
            settings["variants"] = int(input("How many variants would you like for the system to make (ex: 4): "))
        except ValueError:
            print("\nThe input was not in the correct format \n Please try again:\n")
            continue
        else: 
            break    
    
    print("\nPlease enter the maximum allowable spacing between manholes. \n\
(Must be positive integers seperate by a space, for example: 70 100)")
    while True:
        try:
            spacing = input("Maximum allowable manhole spacing: ").split()
            settings["spacing"] = [int(x) for x in spacing]
        except ValueError:
            print("\nThe input was not in the correct format \n\
Please try again:\n")
            continue
        else: 
            break
    
    print("\nThe index of the point you want to designate as an outfall/pumping point:\n\
(Must be positive integers seperate by a space, for example: 78 64)\n")
    while True:
        try:
            outfalls = input("Outfall point index: ").split()
            settings["outfalls"] = [int(x) for x in outfalls]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nThe indices of the points which you want to designate as overflow points:\n\
(Positive integers separate by space, for example: 23 65 118)\n")
    while True:
        try:
            overflows = input("Overflows points indices: ").split()      
            settings["overflows"] = [int(x) for x in overflows]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nThe minimum depth below the ground at which conduits can be installed:\n\
(Positive floats separate by space, for example: 1 1.1 0.9)\n")
    while True:
        try:
            min_depth = input("Minimum installation depth [m]: ").split()
            settings["min_depth"] = [float(x) for x in min_depth]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nEnter the required minimum slope for the conduits:\n\
(Should be positive decimal numbers seperate by a space, for example: 0.002 0.004)\n")
    while True:
        try:
            min_slope = input("Minimum slope [m/m]: ").split()
            settings["min_slope"] = [float(x) for x in min_slope]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nDo you want to enter a maximum allowable slope as well?")
    choice = yes_no_choice()
    if choice == "y":
        print("\nMaximum slope should always be larger than the minimum slope:\n\
(Should be a positive decimal number, for example: 0.004)")
        while True:
            try: 
                max_slope = input("Maximum slope [m/m]: ").split()
                settings["max_slope"] = [float(x) for x in max_slope]
            except ValueError:
                print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
                continue
            if(max(settings["max_slope"]) <= min(settings["min_slope"])):
                print(f"\nNone of the values you entered are larger than the minimum slope. \n\
Please try again.")
                continue
            else:
                break

    print("\nA list of the available diameters of the conduits:\n\
(Should be a series of number separated by spaces, for example: 150 300 500 1000)\n")
    while True:
        try:
            diam_list = input("List of available diameters [mm]: ").split()
            settings["diam_list"] = [int(x) / 1000 for x in diam_list]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break
    
    print("\nFor the initial peak rain and percentage inpervious ground would you like to enter \n\
user defined temporary values? If not, the system will use its default values.")
    choice = yes_no_choice()

    if choice == "n":
        print("\nThe set default values are 36 mm/h of peak rain with a 70 % \n\
ground imperviousness")
        settings["peak_rain"] = 36
        settings["perc_inp"] = 70

    elif choice == "y":
        print("\nEnter the peak rainfall value for the design storm:\n\
(Should be a positive integer, for example: 23)\n")

        while True:
            try:
                settings["peak_rain"] = int(input("The peak rainfall value [mm/h]: "))
            except ValueError:
                print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
                continue    
            else:
                break

        print("\n\nThe average percentage of impervious ground coverage of the area:\n\
Meaning the percentage of any type of surface that does not absorb rainfall \n\
(Should be a positive integer number between 0 and 100, for example: 25)\n")
        while True:
            try:
                settings["perc_inp"] = int(input("Percentage of impervious ground [%]: "))
            except ValueError:
                print(f"\n The value you entered is incorrect, please try again. \n\
    Make sure to enter in a correct format, as can be seen above in the example")
                continue    
            else:
                break
   
    return settings


def standard_input():
    """Ask the user for the standard settings value for a single network.

    Returns:
        dict: The parameters for the system as given by the user
    """
    settings = {}
    settings["variants"] = 1
    
    print("\nPlease enter the described information to enable the next set of calculation steps:")

    print("Please enter the maximum allowable spacing between manholes. \n\
(Should be a positive integer, for example: 100)")
    while True:

        try:
            settings["spacing"] = int(input("\nMaximum allowable manhole spacing: "))

        except ValueError:
            print("\nThe input was not in the correct format (ex: 20)\nPlease try again:\n")
            continue
        else: 
            break

    print("\nThe index of the point you want to designate as an outfall/pumping point:\n\
(Should be a positive integer, for example: 78)\n")
    while True:
        try:
            outfalls = input("Outfall point index: ").split()
            settings["outfalls"] = [int(x) for x in outfalls]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nThe indices of the points which you want to designate as overflow points:\n\
(Positive integers separate by space, for example: 23 65 118)\n")
    while True:
        try:
            overflows = input("Overflows points indices: ").split()      
            settings["overflows"] = [int(x) for x in overflows]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break
            

    print("\nThe minimum depth below the ground at which conduits can be installed:\n\
(Should be a positive integer or decimal number, for example: 1.1)\n")
    while True:
        try:
            settings["min_depth"] = float(input("Minimum installation depth [m]: "))
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nEnter the required minimum slope for the conduits:\n\
(Should be a positive decimal number, for example: 0.002)\n")
    while True:
        try:
            settings["min_slope"] = float(input("Minimum slope [m/m]: "))
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\n\nDo you want to enter a maximum allowable slope as well?")
    choice = yes_no_choice()
    if choice == "y":
        print("\nMaximum slope should always be larger than the minimum slope:\n\
(Should be a positive decimal number, for example: 0.004)")
        while True:
            try: 
                settings["max_slope"] = float(input("Maximum slope [m/m]: "))
            except ValueError:
                print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
                continue
            if(settings["max_slope"] <= settings["min_slope"]):
                print(f"\nThe value you entered is not larger than the minimum slope. \n\
Please try again.")
                continue
            else:
                break

    print("\nEnter the peak rainfall value for the design storm:\n\
(Should be a positive integer, for example: 23)\n")

    while True:
        try:
            settings["peak_rain"] = int(input("The peak rainfall value [mm/h]: "))
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nThe average percentage of impervious ground coverage of the area:\n\
Meaning the percentage of any type of surface that doesnt absorb rainfall \n\
(Should be a positive integer number between 0 and 100, for example: 25)\n")
    while True:
        try:
            settings["perc_inp"] = int(input("Percentage of impervious ground [%]: "))
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nA list of the available diameters of the conduits:\n\
(Should be a series of number separated by spaces, for example: 150 300 500 1000)\n")
    while True:
        try:
            diam_list = input("List of available diameters [mm]: ").split()
            settings["diam_list"] = [int(x) / 1000 for x in diam_list]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break
    
    return settings


def step_3_input(settings: dict):
    """Create the explanations and input space for the SWMM file creation step of the software
    """

    print("\n\nIf you are satisfied with the system that has been constructed,\n\
you can convert it into a System Water Management Model (SWMM) file. To do this,\n\
please give some final specifications:")

    print("\n\nA timeseries will be created from your given design storm value.\n\
Please specify the duration of this design storm in whole hours (for example: 2, max 12)\n")   
    while True:
        try:
            settings["duration"] = int(input("Design storm duration [hours]: "))
        except ValueError:
            print(f"\n The value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\n\nA name for the SWMM file. This file will be a .txt file.\n\
The filename cannot contain any spaces or quotes (for example: test_file)\n")
    settings["filename"] = input("File name: ")

    print("\n\nLastly, it is possible to show the subcatchment polygons in SWMM.\n\
Doing this for larger networks however may make the network difficult to view.\n\
Do you want to include the subcatchment polygons?\n")
    settings["polygons"] = yes_no_choice()

    print("\n\nThe file will now be created, and can be found in the main folder of \
APDUDS.\nPlease note, that in order to open this file in SWMM, you will need to select\n\
the 'all files' option in the folder explorer to be able to see the file in the directory.")

    print("\nThis concludes this use session of APDUDS, \
the software will close once the file has been created.")

    return settings

def design_choice(variants: dict):

    print("\nPlease pick your preferred variant number: \n\
(For example: 1)")
    while True:
        try:
            number = int(input("\nFavourite design: "))
            settings = variants[f"variant_{number}"]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        except KeyError:
            print("The design variant number you gave does not exist. \n\
Please try again")
            continue
        else:
            break

    return settings

def uncertain_choice(variants: dict):

    print("\nPlease pick your preferred variant number: \n\
(For example: 1)")
    while True:
        try:
            number = int(input("\n Favourite design: "))
            nodes = variants[f"nodes_{number}"]
            edges = variants[f"edges_{number}"]
            voro = variants[f"voronoi_area_{number}"]
            settings = variants[f"variant_{number}"]

        except ValueError:
            print(f"\n The value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        except KeyError:
            print("The design variant number you gave does not exist. \n\
Please try again")
            continue
        else:
            break

    return nodes, edges, voro

def settings_uncertainty(settings: dict):
    print("\nYou may now enter the to be varied in values for \n\
the peak rainfall and percentage impervious ground")
    print("\nThe value for the peak rainfall you would like to vary in:\n\
(Positive integers separate by space, for example: 23 65 118)")
    while True:
        try:
            rain = input("\nThe peak rainfall value [mm/h]: ").split()
            settings["peak_rain"] = [int(x) for x in rain]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    print("\nThe average percentage of impervious ground coverage of the area:\n\
(Positive integers separate by space, for example: 25 33 50)\n")
    while True:
        try:
            perc_imp = input("Percentage of impervious ground [%]: ").split()
            settings["perc_inp"] = [int(x) for x in perc_imp]
        except ValueError:
            print(f"\nThe value you entered is incorrect, please try again. \n\
Make sure to enter in a correct format, as can be seen above in the example")
            continue    
        else:
            break

    return settings


def tester():
    """Only used for testing purposes"""
    print("The terminal script has run")

if __name__ == "__main__":
    tester()
