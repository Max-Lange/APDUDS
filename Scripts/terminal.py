"""Defining file for all terminal interaction functions

This script defines the functions that facilitate the interaction between the
user and the program via the terminal.

This file contains the following major functions:

    * area_check - Prints a warning if an area is above a certain threshold
    * yes_no_choice - Presents a yes no [y/n] input space to the user
    * step_1_input - Create the explanations and input space for the network creatin step
    * step_2_input - Create the explanations and input space for the attribute calculation step
    * step_3_input - Create the explanations and input space for the SWMM file creation step
    * tester - Only used for testing purposes
"""

def area_check(coords: list[float], threshold: int):
    """Checks wether a given area is larger than a certain threshold of km^2,
    and prints a warning if it is

    Args:
        coords (list[float]): north, south, east and west coordinates of an area
        threshold (int): The value to check against
    """

    vert = abs(coords[0] - coords[1]) * (40075 / 360)
    hor = abs(coords[2] - coords[3]) * (40075 / 360)

    area = vert * hor

    if area > threshold + 10:
        print("\n WARNING: The area you have selected may be larger than 5 km^2.\n\
This may cause a serious increase in runtime.")


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

    return coords


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
    """


    print("\nWelcome To APDUDS!\n\n\
    To start please input the coordinates of the bounding box of the area \n\
    for which you want the preliminary design:\n\n\
    The inputs should be in degrees latitude and longitude, for example:\n\
    Enter coordinates of the most northern point: 51.9268\n")

    coords = coords_input()

    print("\nFor creating intermediate manholes, the maximum allowable space between\
 these manholes is needed.\nPlease specify this distance (in meters) (example: 100)\n")

    space = manhole_space_input()

    print("\nThe conduit network and manhole distribution for the area you selected will \
now be calculated.\n A set of figures will appear. \
Close these figures once you are ready to proceed.")

    return coords, space


def step_2_input():
    """Create the explanations and input spaces for the attribute calculations step of the
    software

    Returns:
        dict: The parameters for the system as given by the user
    """

    settings = {}

    print("\nNow that the network has been generated, some attributes can be calculated.\n\
Please enter the described information to enable the next set of calculation steps:")

    print("\nThe index of the point you want to designate as an outfall/pumping point:\n\
(Should be a positive integer, for example: 78)\n")
    outfalls = input("Outfall point index: ").split()
    settings["outfalls"] = [int(x) for x in outfalls]

    print("\n\nThe indicies of the points which you want to designate as overflow points:\n\
(Positive integers seperate by space, for examle: 23 65 118)\n")
    overflows = input("Overflows points indicies: ").split()
    settings["overflows"] = [int(x) for x in overflows]

    print("\n\nThe minimum depth below the ground at which conduits can be installed:\n\
(Should be a positive integer or decimal number, for example: 1.1)\n")
    settings["min_depth"] = float(input("Minimum installation depth [m]: "))

    print("\n\nEnter the required minimum slope for the conduits:\n\
(Should be a postive decimal number, for example: 0.002)\n")
    settings["min_slope"] = float(input("Minimum slope [m/m]: "))

    print("\n\nDo you want to enter a maxmimum allowable slope as well?")
    choice = yes_no_choice()

    if choice == "y":
        print("\n\nMaximum slope should always be larger than the minimum slope\n")
        settings["max_slope"] = float(input("Maximum slope [m/m]: "))

    print("\n\nEnter the peak rainfall for the design storm:\n\
(Should be a positive integer, for example: 70)\n")
    settings["peak_rain"] = int(input("The peak rainfall [L/s/ha]: "))

    print("\n\nThe average percentage of inpervious ground coverage of the area:\n\
(Should be a positive integer number between 0 and 100, for example: 25)\n")
    settings["perc_inp"] = int(input("Percentage of impervious ground [%]: "))

    print("\n\nA list of the available diameters of the conduits:\n\
(Should be a series of number seperated by spaces, for example: 150 300 500 1000)\n")
    diam_list = input("List of available diameters [mm]: ").split()
    settings["diam_list"] = [int(x) / 1000 for x in diam_list]

    return settings


def step_3_input():
    """Create the explanations and input space for the SWMM file creation step of the software
    """

    settings = {}

    print("\n\nIf you are satisfied with the system that has been constructed,\n\
you can convert it into a System Water Management Model (SWMM) file. To do this,\n\
please give some final specifications:")

    print("\n\nA timeseries will be created from your given design storm value.\n\
Please specify the duration of this design storm in whole hours (for example: 2, max 12)\n")
    settings["duration"] = int(input("Design storm duration [hours]: "))

    print("\n\nAlso specify the total amount of rain that will fall (for example: 23)\n")
    settings["total_rain"] = int(input("Total rainfall [mm]: "))

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
the software will close once the file hase been created.")

    return settings


def tester():
    """Only used for testing purposes"""
    print("The terminal script has run")

if __name__ == "__main__":
    tester()
