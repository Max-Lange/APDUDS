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
    * gully_space_input - Presents a space for the user to input the maximum
    allowable gully spacing
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


def gully_space_input() -> int:
    """Present the user with a space to input the maximum allowable gully spacing

    Returns:
        int: maximum allowable gully spacing (in [m])
    """

    try:
        space = int(input("Maximum allowable gully spacing: "))

    except ValueError:
        print("\nThe input was not in the correct format (ex: 20)\nPlease try again:\n")
        space = gully_space_input()

    return space


def greeting():
    """Present the user with a greeting, followed by a space for the user to enter the
    coordinates of the wanted bounding box, and maximum gully spacing
    """

    print("\nWelcome To APDUDS!\n\n\
    To start please input the coordinates of the bounding box of the area \n\
    for which you want the preliminary design:\n\n\
    The inputs should be in degrees latitude and longitude, for example:\n\
    Enter coordinates of the most northern point: 51.9268\n")

    coords = coords_input()

    print("\nFor creating intermediate gullies, the maximum allowable space between\
 these gullies is needed.\nPlease specify this distance (in meters) (example: 20)\n")

    space = gully_space_input()

    print("The pipe network and gully distribution for the area you selected will\
now be calculated. A figure will apear. Close this figure once you are ready to proceed.")

    return coords, space


def main():
    """Only used for testing purposes"""

    greeting()


if __name__ == "__main__":
    main()
