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
from numpy import concatenate as concatenate
import matplotlib.pyplot as plt
from pandas import DataFrame
from attribute_calculator import attribute_calculation 
from terminal import design_choice, uncertain_choice, settings_uncertainty
from osm_extractor import splitter
from plotter import voronoi_plotter, height_contour_plotter_datum, height_contour_plotter_local, diameter_map


def multiple_variant(nodes: DataFrame, edges: DataFrame, settings: dict, area: float, block: bool = False):
    """Initialises the calculation step for multiple variants by determining different settings per variant.

    Args:
        nodes (DataFrame): The node data for a network
        edges (DataFrame): The conduit data for a network
        settings (dict): The parameters for a network
        area (float): The given area of the network

    Returns:
        tuple[DataFrame, DataFrame, freud.locality.voronoi]: Node and conduit data with updated
        values for the attributes, as well as a voronoi object for use in the SWMM file creation
    """
    
    
    variants_design = {}
    rnd.seed(1)
    for j in range(settings["variants"]):
        variants_design[f"variant_{j + 1}"] = variation_design(settings, area)
        nodes_split, edges_split = splitter(nodes, edges, variants_design[f"variant_{j + 1}"]["spacing"])
        print(f"\nStarting the attribute calculation step for variant {j + 1}...")
        variants_design[f"nodes_{j +1 }"], variants_design[f"edges_{j + 1}"], variants_design[f"voronoi_area_{j + 1}"] \
            = attribute_calculation(nodes_split, edges_split, variants_design[f"variant_{j + 1}"])
        print(f"Completed the attribute calculations for variant {j + 1}, plotting graphs...")

        fig = plt.figure()
        voronoi_plotter(variants_design[f"nodes_{j + 1}"], variants_design[f"voronoi_area_{j + 1}"], 221)
        height_contour_plotter_local(variants_design[f"nodes_{j + 1}"], variants_design[f"edges_{j + 1}"], 222, fig)
        height_contour_plotter_datum( variants_design[f"nodes_{j + 1}"], variants_design[f"edges_{j + 1}"], 224, fig)
        diameter_map(variants_design[f"nodes_{j + 1}"], variants_design[f"edges_{j + 1}"], 223)
        variant_settings = variants_design[f"variant_{j + 1}"].copy()
        fig.suptitle(f"Design variant {j + 1} \n spacing: {variant_settings['spacing']}; min_slope: {variant_settings['min_slope']}; min_depth: {variant_settings['min_depth']}")
        fig.tight_layout()
        
    print(f"\nPlease pick your favourite design, you will be able to enter the number \n\
of the design once all figures are closed.")
    plt.show(block=block)

    settings_design = design_choice(variants_design)

    settings = settings_uncertainty(settings_design)

    variants_uncertain = {}
    for j in range(settings["variants"]):
        variants_uncertain[f"variant_{j + 1}"] = variation_uncertainty(settings)
        nodes, edges = splitter(nodes, edges, variants_uncertain[f"variant_{j + 1}"]["spacing"])

        print(f"\nAdjusting pipe diameter for uncertainties in rainfall and percentage impervious ground, design {j + 1}..")
        variants_uncertain[f"nodes_{j + 1}"], variants_uncertain[f"edges_{j + 1}"], variants_uncertain[f"voronoi_area_{j + 1}"] \
            = attribute_calculation(nodes, edges, variants_uncertain[f"variant_{j + 1}"])    

        fig = plt.figure()
        voronoi_plotter(variants_uncertain[f"nodes_{j + 1}"], variants_uncertain[f"voronoi_area_{j + 1}"], 221)
        height_contour_plotter_local( variants_uncertain[f"nodes_{j + 1}"], variants_uncertain[f"edges_{j + 1}"], 222, fig)
        height_contour_plotter_datum( variants_uncertain[f"nodes_{j + 1}"], variants_uncertain[f"edges_{j + 1}"], 224, fig)
        diameter_map(variants_uncertain[f"nodes_{j + 1}"], variants_uncertain[f"edges_{j + 1}"], 223)
        variant_settings = variants_uncertain[f"variant_{j + 1}"].copy()
        diam_max = variants_uncertain[f"edges_{j + 1}"]["diameter"].max()
        diam_min = variants_uncertain[f"edges_{j + 1}"]["diameter"].min()
        fig.suptitle(f"Uncertainty variant {j + 1} \n peak_rain: {variant_settings['peak_rain']}; perc_inp: {variant_settings['perc_inp']}; \
max_diam: {diam_max}; min_diam: {diam_min}")
     
        fig.tight_layout()
    print("\nDiameter calculations finished for all variants.")

    print(f"\nPlease pick your favourite design, you will be able to enter the number \n\
of the design once all figures are closed.")
    plt.show(block=block)

    nodes, edges, voro = uncertain_choice(variants_uncertain)

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
    height_contour_plotter_local(nodes, edges, 222, fig)
    height_contour_plotter_datum(nodes, edges, 224, fig)
    diameter_map(nodes, edges, 223)
    fig.suptitle(f"Design {1}")
    fig.tight_layout()

    plt.show(block=block)

    return nodes, edges, voro

def variation_design(settings: dict, area: float):
    """Determines the design parameters for one iteration of the network design.

    Args:
        settings (dict): All the parameters for a network
        area (float): Area of the bounding box of the network

    Returns:
        settings (dict): Selected parameters for one network
    """

    random_settings = {}
    random_settings = settings.copy()

    random_settings["spacing"] = rnd.choice(settings["spacing"], 1)[0]
    random_settings["outfalls"] = rnd.choice(settings["outfalls"], 1, replace=True)
    random_settings["min_depth"] = rnd.choice(settings["min_depth"], 1)[0]
    random_settings["min_slope"] = rnd.choice(settings["min_slope"], 1)[0]

    if area > 4:    #If area larger than 4 km^2 pick between 2 and 4 overflows
        random_settings["overflows"] = rnd.choice(settings["overflows"], \
                                                  rnd.random_integers(2, min(4, len(settings["overflows"]))), replace=True)
    elif area > 1:  #If between 1 and 3 km^2 pick between 1 and 3
        random_settings["overflows"] = rnd.choice(settings["overflows"], rnd.random_integers(1, 3), replace=True)
    else:           #Else pick 1 overflow
        random_settings["overflows"] = rnd.choice(settings["overflows"], 1, replace=True)
    
    if "max_slope" in settings:
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
    random_settings["peak_rain"] = rnd.choice(settings["peak_rain"], 1, replace=False)[0]
    random_settings["perc_inp"] = rnd.choice(settings["perc_inp"], 1, replace=False)[0]

    return random_settings