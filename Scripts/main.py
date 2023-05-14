"""Main script of APDUDS. Running this script (with either main or tester) starts
the entire software.

This script requires that `matplotlib` and `pandas` be installed within the Python
environment you are running this script in, as well as all the packages required
by the modules `osm_extractor`, `plotter`, `terminal`, `swmm_formater` and `attribute_calculator`.

This file contains the following functions:

    * step_1 - Runs the network creation step of the software
    * step_2 - Runs the attribute calculation step of the software
    * step_3 - Runs the SWMM file creation step of the software
    * main - Starts the software in it's entirity. Run this function to run the entire software
    * tester - Only used for testing, can also be used for a terminal-skipping run of the software
"""

import warnings
from pandas import DataFrame
from numpy import loadtxt, random
from swmm_formater import swmm_file_creator
from osm_extractor import extractor, fill_nan, cleaner, splitter
from plotter import network_plotter, voronoi_plotter, height_contour_plotter, diameter_map
from terminal import step_1_input, step_2_input, step_3_input, area_check, design_choice, settings_uncertainty
from attribute_calculator import attribute_calculation, variation_design, variation_uncertainty
from matplotlib import pyplot as plt
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.simplefilter(action='ignore', category=UserWarning)


def step_1(coords: list[float], key: str, block: bool = True):
    """Preform the network creation step of the software by running the appropriate functions.
    Also display some graphs which are relevent to the results of these functions

    Args:
        coords (list[float]): The north, south, east and west coordinates of the desired area
        block (bool, optional): Decides wether displaying the graph pauses the run.
        Defaults to False.

    Returns:
        tuple[DataFrame, DataFrame]: The node and conduit data of the created network
    """

    print("\nStarting the OpenStreetMap download. This may take some time, please only close the \
software after 5 minutes of no response....")
    nodes, edges = extractor(coords, key)

    print("Completed the OpenStreetMap download, interpolating several missing elevation values...")

    elevation_nodes, elevation_edges = fill_nan(nodes, edges)

    print("Completede filling the missing values, starting the data cleaning")

    filtered_nodes, filtered_edges = cleaner(elevation_nodes, elevation_edges)

    print("Completed the data cleaning, plotting graphs...")
    _ = plt.figure()
    network_plotter(filtered_nodes, filtered_edges, 111, numbered=True)
    plt.show(block=block)

    return filtered_nodes, filtered_edges

def step_2(nodes: DataFrame, edges: DataFrame, settings: dict, block: bool = False):
    """Preform the attribute calculation step of the software by running the appropiate functions.
    Also display some graphs which are relevent to the results of these functions

    Args:
        nodes (DataFrame): The node data for a network
        edges (DataFrame): The conduit data for a network
        settings (dict): The parameters for a network

    Returns:
        tuple[DataFrame, DataFrame, freud.locality.voronoi]: Node and conduit data with updated
        values for the attributes, as well as a voronoi object for use in the SWMM file creation
    """
 
    
    if "variants" in settings:
        random.seed(1)
        variants = {}
        for j in range(settings["variants"]):
            print("\n Starting the variation process...")
            variants[f"variant_{j+1}"] = variation_design(settings)
            nodes, edges = splitter(nodes, edges, variants[f"variant_{j+1}"]["spacing"])
            print("\nStarting the attribute calculation step...")
            nodes_variant, edges_variant, voro_variant = attribute_calculation(nodes, edges, variants[f"variant_{j+1}"])
            print("Completed the attribute calculations, plotting graphs...")

            fig = plt.figure()
            voronoi_plotter(nodes_variant, voro_variant, 221)
            height_contour_plotter(nodes_variant, edges_variant, 222, fig)
            diameter_map(nodes_variant, edges_variant, 223)
            fig.suptitle(f"Design {j + 1}")
            fig.tight_layout()

        plt.show(block=block)

        settings = design_choice(variants)

        settings = settings_uncertainty(settings)

        variants = {}
        for j in range(settings["variants"]):
            print("\n Starting the variation process...")
            variants[f"variant_{j+1}"] = variation_uncertainty(settings)
            nodes, edges = splitter(nodes, edges, variants[f"variant_{j+1}"]["spacing"])
            print("\nStarting the attribute calculation step...")
            nodes_variant, edges_variant, voro_variant = attribute_calculation(nodes, edges, variants[f"variant_{j+1}"])
            print("Completed the attribute calculations, plotting graphs...")

            fig = plt.figure()
            voronoi_plotter(nodes_variant, voro_variant, 221)
            height_contour_plotter(nodes_variant, edges_variant, 222, fig)
            diameter_map(nodes_variant, edges_variant, 223)
            fig.suptitle(f"Design {j + 1}")
            fig.tight_layout()

        plt.show(block=block)

        settings = design_choice(variants)
        nodes, edges, voro = attribute_calculation(nodes, edges, settings)

    else:
        nodes, edges = splitter(nodes, edges, settings["spacing"])
        print("\nStarting the attribute calculation step...")
        nodes, edges, voro = attribute_calculation(nodes, edges, settings)
        print("Completed the attribute calculations, plotting graphs...")

        fig = plt.figure()
        
        voronoi_plotter(nodes, voro, 221)
        height_contour_plotter(nodes, edges, 222, fig)
        diameter_map(nodes, edges, 223)
        fig.suptitle(f"Design {1}")
        fig.tight_layout()

        plt.show(block=block)

    

    return nodes, edges, voro

def step_3(nodes: DataFrame, edges: DataFrame, voro, settings: dict):
    """Preform the SWMM file creation step of the software by running the appropriate functions.

    Args:
        nodes (DataFrame): The node data for a network
        edges (DataFrame): The conduit data for a network
        voro (freud.locality.voronoi): Voronoi object of the nodes of a network
        settings (dict): The parameters for a network
    """

    print("\nStarting the SWMM file creation...")
    swmm_file_creator(nodes, edges, voro, settings)
    print("Completed the SWMM file creation.")


def main():
    """Running this function starts the software in its entirety.
    Run this function if you want to use the software in the intended way
    """

    coords, api_key = step_1_input()
    nodes, edges = step_1(coords, api_key)


    settings = step_2_input()

    nodes, edges, voro = step_2(nodes, edges, settings)

    settings = step_3_input(settings)
    step_3(nodes, edges, voro, settings)



def tester():
    """Only used for testing, but can also be used as a way to run the program as intended,
    while skipping the terminal interaction stage.
    """

    test_coords = [51.9291, 51.92076, 4.8381, 4.8163] #Grootammers

    api_key = loadtxt('api_key.txt', dtype=str)


    area_check(test_coords, 5)
    nodes, edges = step_1(test_coords, api_key)

    # Groot Ammers
    # test_settings = {"spacing": 100,
    #                  "outfalls":[108],
    #                  "overflows":[92, 30],
    #                  "min_depth":1.1,
    #                  "min_slope":1/500,
    #                  "peak_rain": 36,
    #                  "perc_inp": 50,
    #                  "diam_list": [0.25, 0.5, 0.6, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3],
    #                  "filename": "test_swmm",
    #                  "max_slope": 1/450,
    #                  "duration": 2,
    #                  "polygons": "n"}
    
    test_settings = {"variants": 2,
                     "spacing": [100, 150],
                     "outfalls":[108, 3, 115],
                     "overflows":[132, 89, 69, 92, 30, 75],
                     "min_depth": [1, 1.4, 1.2],
                     "min_slope": [0.002, 0.003],
                     "peak_rain": 36,
                     "perc_inp": 50,
                     "diam_list": [0.25, 0.5, 0.6, 0.75, 1.0, 1.25, 1.5, 2.0, 2.5, 3],
                     "filename": "test_swmm",
                     "max_slope": [0.004, 0.006],
                     "duration": 2,
                     "polygons": "n"}
    
    # nodes, edges = splitter(nodes, edges, test_settings["spacing"])

    nodes, edges, voro = step_2(nodes, edges, test_settings, block=True)

    step_3(nodes, edges, voro, test_settings)


if __name__ == "__main__":
    tester()
