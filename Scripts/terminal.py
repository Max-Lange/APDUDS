"""Defining file for all terminal interaction functions

This script defines the functions that facilitate the interaction between the
user and the program via the terminal. It gives the user the space to input the
wanted settings, present them with moments to check if their entered data (or
resulting graphs) check out, and allows them to go back to previous steps.

This file can also be imported as a module and contains the following
functions:

    * yes_no_choice - Presents a yes no [y/n] input space to the user
    * coords_input - Presents a space for the user to input the wanted coords of the
    desired bounding box
    * manhole_space_input - Presents a space for the user to input the maximum
    allowable manhole spacing
    * greeting - Presents the user with the program greeting, and contains the first input step
"""


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
    """Present the user with option to input the coordinates of a desired
    bounding box, and also ask the user if the want to proceed.

    Returns:
        list: north, south, east and west coordinates
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


def greeting():
    """Present the user with a greeting, followed by a space for the user to enter the
    coordinates of the wanted bounding box, and maximum manhole spacing
    """

    print("\nWelcome To APDUDS!\n\n\
    To start please input the coordinates of the bounding box of the area \n\
    for which you want the preliminary design:\n\n\
    The inputs should be in degrees latitude and longitude, for example:\n\
    Enter coordinates of the most northern point: 51.9268\n")

    coords = coords_input()

    print("\nFor creating intermediate manholes, the maximum allowable space between\
 these manholes is needed.\nPlease specify this distance (in meters) (example: 20)\n")

    space = manhole_space_input()

    print("\nThe pipe network and manhole distribution for the area you selected will \
now be calculated.\n A set of figures will appear. \
Close these figures once you are ready to proceed.")

    return coords, space

def step_2_input():
    """Present the user with the input space for the burring depth parameters
    """

    print("\nNow that the network has been generated, some attributes can be calculated.\n\
Please enter the described information to enable these calculation steps:")

    print("\n\nPlease enter the index of the points you want to designate as outfall points:\n\
(Should be positive integers seperated by single spaces, for example: 36 118 2)\n")
    outfalls = input("Outfall point index ").split()
    outfalls = [int(x) for x in outfalls]

    print("\n\nEnter the minimum depth below the ground at which pipes can be installed:\n\
(Should be a positive integer or decimal number, for example: 1.1)\n")
    min_depth = float(input("Minimum installation depth [m]: "))

    print("\n\nEnter the minimum slope for the pipes:\n\
(Should be a decimal number between (but not including!) 0 and 1, for example: 0.002)\n")
    min_slope = float(input("Minimum slope [-]: "))

    print("\n\nEnter the design storm rainfall:\n\
(Should be a positive integer, for example: 70)\n")
    rainfall = int(input("The design storm rainfall [L/s/ha]: "))

    print("\n\nThe average percentage of inpervious ground coverage of the area:\n\
(Should be a positive integer number between 0 and 100, for example: 25)\n")
    perc_inp = int(input("Percentage of impervious ground [%]: "))

    print("\n\nA list of the available diameters of the conduits:\n\
(Should be a series of number seperated by spaces, for example: 150 300 500 1000)\n")
    diam_list = input("List of available diameters: ").split()
    diam_list = [int(x) / 1000 for x in diam_list]

    return {"outfalls":outfalls, "min_depth":min_depth, "min_slope":min_slope,
            "rainfall":rainfall, "perc_inp": perc_inp, "diam_list": diam_list}

def step_3_input():
    """Give explanation and facilitate the input space for the swmm file creation step
    """

    print("\n\nIf you are satisfied with the system that has been constructed, \
you can convert it into a System Water Management Model (SWMM) file. To do this, \
please give a name for the file:\n")

    filename = input("File name (ex: test_file): ")

    print("\nThe file will now be created, and can be found in the main folder of \
APDUDS.\nPlease note, that in order to open this file in SWMM, you will need to select\n\
the 'all file' option in the folder explorer to be able to select the file.")

    print("\nThis concludes this use case of APDUDS, the software will now close.")

    return filename

def tester():
    """Only used for testing purposes"""

    step_3_input()


if __name__ == "__main__":
    tester()
