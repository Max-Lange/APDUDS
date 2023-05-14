"""Defining file for the variation process of APDUDS, it performs the choosing 
of parameters per variant and the calculation step.

This script requires that `numpy`, `matplotlib` and `pandas` be installed within the Python
environment you are running this script in.

This file contains the following major functions:

    * multiple_variant - Runs the multiple variants version of APDUDS
    * single_variant - Runs the single variant version of APDUDS
    * variation_design - Determines the different parameters for the parameters chosen by design
    * variation_uncerainty - Determines the different parameters for the parameters chosen by uncertainty

"""

from numpy import random as rnd
import matplotlib.pyplot as plt
from pandas import DataFrame
from attribute_calculator import attribute_calculation 
from terminal import design_choice, settings_uncertainty
from osm_extractor import splitter
from plotter import voronoi_plotter, height_contour_plotter, diameter_map


def multiple_variant(nodes: DataFrame, edges: DataFrame, settings: dict, block: bool = False):
    """Initialises the calculation step for multiple variants by determining different settings per variant.

    Args:
        nodes (DataFrame): The node data for a network
        edges (DataFrame): The conduit data for a network
        settings (dict): The parameters for a network

    Returns:
        tuple[DataFrame, DataFrame, freud.locality.voronoi]: Node and conduit data with updated
        values for the attributes, as well as a voronoi object for use in the SWMM file creation
    """
    
    rnd.seed(1)
    variants = {}
    for j in range(settings["variants"]):
        variants[f"variant_{j + 1}"] = variation_design(settings)
        nodes, edges = splitter(nodes, edges, variants[f"variant_{j + 1}"]["spacing"])
        print(f"\nStarting the attribute calculation step for variant {j + 1}...")
        nodes_variant, edges_variant, voro_variant = attribute_calculation(nodes, edges, variants[f"variant_{j + 1}"])
        print(f"Completed the attribute calculations for variant {j + 1}, plotting graphs...")

        fig = plt.figure()
        voronoi_plotter(nodes_variant, voro_variant, 221)
        height_contour_plotter(nodes_variant, edges_variant, 222, fig)
        diameter_map(nodes_variant, edges_variant, 223)
        fig.suptitle(f"Design {j + 1}")
        fig.tight_layout()
        
    print(f"\nPlease pick your favourite design, you will be able to enter the number \n\
of the design once all figures are closed.")
    plt.show(block=block)

    settings_design = design_choice(variants)

    settings = settings_uncertainty(settings_design)

    variants = {}
    for j in range(settings["variants"]):
        variants[f"variant_{j + 1}"] = variation_uncertainty(settings)
        nodes, edges = splitter(nodes, edges, variants[f"variant_{j + 1}"]["spacing"])

        print(f"\nAdjusting pipe diameter for design {j + 1}..")
        nodes_variant, edges_variant, voro_variant = attribute_calculation(nodes, edges, variants[f"variant_{j + 1}"])    

        fig = plt.figure()
        voronoi_plotter(nodes_variant, voro_variant, 221)
        height_contour_plotter(nodes_variant, edges_variant, 222, fig)
        diameter_map(nodes_variant, edges_variant, 223)
        fig.suptitle(f"Design {j + 1}")
        fig.tight_layout()
    print("\nDiameter calculations finished for all variants.")

    print(f"\nPlease pick your favourite design, you will be able to enter the number \n\
of the design once all figures are closed.")
    plt.show(block=block)

    settings_uncertainty = design_choice(variants)

    nodes, edges, voro = attribute_calculation(nodes, edges, settings_uncertainty)

    return nodes, edges, voro

def single_variant(nodes: DataFrame, edges: DataFrame, settings: dict, block: bool = False):
    """Initialises the calculation step for just one variant.

    Args:
        nodes (DataFrame): The node data for a network
        edges (DataFrame): The conduit data for a network
        settings (dict): The parameters for a network

    Returns:
        tuple[DataFrame, DataFrame, freud.locality.voronoi]: Node and conduit data with updated
        values for the attributes, as well as a voronoi object for use in the SWMM file creation
    """

    nodes, edges = splitter(nodes, edges, settings["spacing"])

    nodes, edges, voro = attribute_calculation(nodes, edges, settings)

    print("\nCompleted the attribute calculations, plotting graphs...")
    fig = plt.figure()        
    voronoi_plotter(nodes, voro, 221)
    height_contour_plotter(nodes, edges, 222, fig)
    diameter_map(nodes, edges, 223)
    fig.suptitle(f"Design {1}")
    fig.tight_layout()

    plt.show(block=block)

    return nodes, edges, voro

def variation_design(settings: dict):
    """Determines the design parameters for one iteration of the network design.

    Args:
        settings (dict): All the parameters for a network

    Returns:
        settings (dict): Selected parameters for one network
    """

    random_settings = {}
    random_settings = settings.copy()

    random_settings["spacing"] = rnd.choice(settings["spacing"], 1)[0]
    random_settings["outfalls"] = rnd.choice(settings["outfalls"], 1)
    random_settings["overflows"] = rnd.choice(settings["overflows"], rnd.random_integers(1, 3), replace=True)
    random_settings["min_depth"] = rnd.choice(settings["min_depth"], 1)[0]
    random_settings["min_slope"] = rnd.choice(settings["min_slope"], 1)[0]

    while True:
        random_settings["max_slope"] = rnd.choice(settings["max_slope"], 1)[0]
        if random_settings["max_slope"] > random_settings["min_slope"]:
            break
        else:
            continue

    return random_settings


def variation_uncertainty(settings: dict):
    """Determines the uncertain parameters for one iteration of the network design.

    Args:
        settings (dict): All the parameters for a network

    Returns:
        settings (dict): Selected parameters for one network
    """

    random_settings = {}

    random_settings = settings.copy()
    random_settings["peak_rain"] = rnd.choice(settings["peak_rain"], 1)[0]
    random_settings["perc_inp"] = rnd.choice(settings["perc_inp"], 1)[0]

    return random_settings