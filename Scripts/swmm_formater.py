"""Defining file for creating a swmm file

This script requires that `pandas` be installed within the Python
environment you are running this script in.

This file contains the following major functions:

    * swmm_file_creator - Creates a txt file of the networkwhich can be used in the swmm software
    * tester - Only used for testing purposes
"""

from datetime import datetime
import pandas as pd

def swmm_file_creator(nodes: pd.DataFrame, edges: pd.DataFrame, voro, settings: dict):
    """Creates a .txt file which follows the System Water Management Model format (SWMM),
    so that the created network can be used in that software

    Args:
        nodes (DataFrame): The node data of a network
        edges (DataFrame): The conduit data of a network
        voro (freud.locality.voronoi): voronoi object of the nodes of a network
        settings (dict): Parameters for a network
        filename (str): Desired name for the SWMM file
    """

    with open(f"{settings['filename']}.txt", 'w', encoding="utf8") as file:

        title = create_title()
        file.write('\n'.join(title))

        date = datetime.today().strftime('%m/%d/%Y')
        options = create_options(date)
        file.write('\n'.join(options))

        evaporation = create_evaporation()
        file.write('\n'.join(evaporation))

        raingage = create_raingage()
        file.write('\n'.join(raingage))

        subcatchments = create_subcatchments(nodes, settings)
        file.write('\n'.join(subcatchments))

        subareas = create_subcatchement_subareas(nodes)
        file.write('\n'.join(subareas))

        infiltration = create_subcatchement_infiltration(nodes)
        file.write('\n'.join(infiltration))

        junctions = create_junctions(nodes)
        file.write('\n'.join(junctions))

        outfalls = create_outfalls(nodes)
        file.write('\n'.join(outfalls))

        conduits = create_conduits(edges)
        file.write('\n'.join(conduits))

        xsections = create_cross_section(edges)
        file.write('\n'.join(xsections))

        timeseries = create_timeseries(settings, date)
        file.write('\n'.join(timeseries))

        report = create_report()
        file.write('\n'.join(report))

        tags = create_tags()
        file.write('\n'.join(tags))

        map_settings = create_map_settings(nodes)
        file.write('\n'.join(map_settings))

        coordinates = create_junctions_coordinates(nodes)
        file.write('\n'.join(coordinates))

        if settings["polygons"] == "y":
            polygons = create_subcatchment_polygons(nodes, voro)
            file.write('\n'.join(polygons))

        symbols = create_symbols(nodes)
        file.write('\n'.join(symbols))


def create_title():
    """Returns a list of strings for the title section"""

    title = ["[TITLE]",
             ";;Project Title/Notes",
             "\n"]
    return title


def create_options(date: str):
    """Returns a list of strings for the options section"""

    options = ["[OPTIONS]",
               ";;Option             Value",
               "FLOW_UNITS           CMS",
               "INFILTRATION         HORTON",
               "FLOW_ROUTING         DYNWAVE",
               "LINK_OFFSETS         DEPTH",
               "MIN_SLOPE            0",
               "ALLOW_PONDING        NO",
               "SKIP_STEADY_STATE    NO",
               "",
              f"START_DATE           {date}",
               "START_TIME           00:00:00",
              f"REPORT_START_DATE    {date}",
               "REPORT_START_TIME    00:00:00",
              f"END_DATE             {date}",
               "END_TIME             12:00:00",
               "SWEEP_START          1/1",
               "SWEEP_END            12/31",
               "DRY_DAYS             0",
               "REPORT_STEP          00:05:00",
               "WET_STEP             00:01:00",
               "DRY_STEP             00:10:00",
               "ROUTING_STEP         0:00:10",
               "RULE_STEP            00:00:00",
               "",
               "INERTIAL_DAMPING     PARTIAL",
               "NORMAL_FLOW_LIMITED  BOTH",
               "FORCE_MAIN_EQUATION  H-W",
               "VARIABLE_STEP        0.75",
               "LENGTHENING_STEP     0",
               "MIN_SURFAREA         0",
               "MAX_TRIALS           0",
               "HEAD_TOLERANCE       0",
               "SYS_FLOW_TOL         5",
               "LAT_FLOW_TOL         5",
               "MINIMUM_STEP         0.5",
               "THREADS              1",
               "\n"]
    return options


def create_evaporation():
    """Returns a list of strings for the evaporation section"""

    evaporation = ["[EVAPORATION]",
                   ";;Data Source    Parameters",
                   ";;-------------- ----------------",
                   "CONSTANT         0.0",
                   "DRY_ONLY         NO",
                   "\n"]
    return evaporation


def create_raingage():
    """Returns a list of strings for the raingage section"""

    raingages = ["[RAINGAGES]",
                 ";;Name           Format    Interval SCF      Source ",
                 ";;-------------- --------- ------ ------ ----------",
                 "General          INTENSITY 0:05     1.0      TIMESERIES Design_Storm",
                 "\n"]
    return raingages


def create_subcatchments(nodes: pd.DataFrame, settings: dict):
    """Returns a list of strings for the subcatchments section"""

    subcatchments = ["[SUBCATCHMENTS]",
                     ";;Name           Rain Gage        Outlet           Area     %Imperv  \
Width    %Slope   CurbLen  SnowPack",
                     ";;-------------- ---------------- ---------------- -------- -------- \
-------- -------- -------- ----------------"]

    for node_index, node in nodes.iterrows():
        if node.role == "node":
            nr_length = len(str(node_index))
            catchment = "sub_" + str(node_index) + (17 - 4 - nr_length) * " "
            catchment += "General" + (17 - 7) * " "
            catchment += "j_" + str(node_index) + (17 - 2 - nr_length) * " "
            catchment += str(round(node.area / 10000, 4)) + \
(9 - len(str(round(node.area * 0.0001, 4)))) * " "
            catchment += str(settings['perc_inp']) + (9 - len(str(settings['perc_inp']))) * " "
            catchment += "500      0.5      0"

            subcatchments.append(catchment)
    subcatchments.append("\n")
    return subcatchments


def create_subcatchement_subareas(nodes: pd.DataFrame):
    """Returns a list of strings for the subareas section"""

    subareas = ["[SUBAREAS]",
                ";;Subcatchment   N-Imperv   N-Perv     S-Imperv   S-Perv     PctZero    \
RouteTo    PctRouted",
                ";;-------------- ---------- ---------- ---------- ---------- ---------- \
---------- ----------"]

    for node_index, node in nodes.iterrows():
        if node.role == "node":
            nr_length = len(str(node_index))
            subarea = "sub_" + str(node_index) + (17 - 4 - nr_length) * " "
            subarea += "0.01       0.1        0.05       0.05       25         OUTLET"

            subareas.append(subarea)
    subareas.append("\n")
    return subareas


def create_subcatchement_infiltration(nodes: pd.DataFrame):
    """Returns a list of strings for the infilatrion section"""

    infiltration = ["[INFILTRATION]",
                    ";;Subcatchment   Param1     Param2     Param3     Param4     Param5",
                    ";;-------------- ---------- ---------- ---------- ---------- ----------"]

    for node_index, node in nodes.iterrows():
        if node.role == "node":
            nr_length = len(str(node_index))
            infil = f"sub_{node_index}" + (17 - 4 - nr_length) * " "
            infil += "3.0        0.5        4          7          0"

            infiltration.append(infil)
    infiltration.append("\n")
    return infiltration


def create_junctions(nodes: pd.DataFrame):
    """Returns a list of strings for the junctions section"""

    junctions = ["[JUNCTIONS]",
                 ";;Name           Elevation  MaxDepth   InitDepth  SurDepth   Aponded",
                 ";;-------------- ---------- ---------- ---------- ---------- ----------"]

    for node_index, node in nodes.iterrows():
        if node.role == "node":
            nr_length = len(str(node_index))
            junc = "j_" + str(node_index) + (17 - 2 - nr_length) * " "
            junc += "-" + str(node.depth) + (10 - len(str(node.depth))) * " "
            junc += "0          0          0          0"

            junctions.append(junc)
    junctions.append("\n")
    return junctions


def create_outfalls(nodes: pd.DataFrame):
    """Returns a list of strings for the outfalls section"""

    outfalls = ["[OUTFALLS]",
                ";;Name           Elevation  Type       Stage Data       Gated    Route To",
                ";;-------------- ---------- ---------- ---------------- -------- \
----------------"]

    for index, node in nodes.iterrows():
        if node.role in ["outfall", "overflow"]:
            out = "j_" + str(index) + (17 - 2 - len(str(index))) * " "
            depth = "-" + str(nodes.at[index, 'depth'])
            out += depth + (10 - len(depth)) * " "
            out += "FREE                        NO"

            outfalls.append(out)
    outfalls.append("\n")
    return outfalls


def create_conduits(edges: pd.DataFrame):
    """Returns a list of strings for the conduits section"""

    conduits = ["[CONDUITS]",
                ";;Name           From Node        To Node          Length     Roughness  \
InOffset   OutOffset  InitFlow   MaxFlow",
                ";;-------------- ---------------- ---------------- ---------- ---------- \
---------- ---------- ---------- ----------"]

    for edge_index, edge in edges.iterrows():
        conduit = "c_" + str(edge_index) + (17 -2 - len(str(edge_index))) * " "
        conduit += "j_" + str(int(edge['from'])) + (17 - 2 - len(str(int(edge['from'])))) * " "
        conduit += "j_" + str(int(edge["to"])) + (17 - 2 - len(str(int(edge["to"])))) * " "
        conduit += str(edge.length) + (11 - len(str(edge.length))) * " "
        conduit += "0.01       0          0          0          0"

        conduits.append(conduit)
    conduits.append("\n")
    return conduits


def create_cross_section(edges: pd.DataFrame):
    """Returns a list of strings for the xsections section"""

    xsections = ["[XSECTIONS]",
                 ";;Link           Shape        Geom1            Geom2      Geom3      \
Geom4      Barrels    Culvert",
                 ";;-------------- ------------ ---------------- ---------- ---------- \
---------- ---------- ----------"]

    for edge_index, edge in edges.iterrows():
        x_sec = "c_" + str(edge_index) + (17 - 2 - len(str(edge_index))) * " "
        x_sec += "CIRCULAR     "
        x_sec += str(edge.diameter) + (17 - len(str(edge.diameter))) * " "
        x_sec += "0          0          0          1"

        xsections.append(x_sec)
    xsections.append("\n")
    return xsections


def create_timeseries(settings: dict, date: str):
    """Returns a list of strings for the timeseries section"""

    timeseries = ["[TIMESERIES]",
                  ";;Name           Date       Time       Value",
                  ";;-------------- ---------- ---------- ----------"]

    for time in range(0, settings["duration"]*60, 5):
        step = "Design_Storm     "
        step += date + (11 - len(date)) * " "

        hours, minutes = int(time // 60), int(time % 60)
        str_time = str(hours) + ":"
        if minutes == 0:
            str_time += "00"

        elif minutes == 5:
            str_time += "05"

        else:
            str_time += str(minutes)

        step += str_time + (11 - len(str_time)) * " "
        step += str(settings["peak_rain"] * 0.36)

        timeseries.append(step)
    timeseries.append("\n")
    return timeseries


def create_report():
    """Returns a list of strings for the report section"""

    report = ["[REPORT]",
              ";;Reporting Options",
              "SUBCATCHMENTS ALL",
              "NODES ALL",
              "LINKS ALL",
              "\n"]
    return report


def create_tags():
    """Returns a list of strings for the tags section"""

    tags = ["[TAGS]",
            "\n"]
    return tags


def create_map_settings(nodes: pd.DataFrame):
    """Returns a list of strings for the map settings section"""

    map_settings = ["[MAP]",
                   f"DIMENSIONS {round(nodes.x.min()-200, 2)} {round(nodes.y.min()-200, 2)} \
{round(nodes.x.max()+200, 2)} {round(nodes.y.max()+200, 2)}",
                    "Units      Meters",
                    "\n"]
    return map_settings


def create_junctions_coordinates(nodes: pd.DataFrame):
    """Returns a list of strings for the junctions coordinates section"""

    coordinates = ["[COORDINATES]",
                   ";;Node           X-Coord            Y-Coord",
                   ";;-------------- ------------------ ------------------"]

    for index, node in nodes.iterrows():
        coords = "j_" + str(index) + (17 - 2 - len(str(index))) * " "
        coords += str(node.x) + (19 - len(str(node.x))) * " "
        coords += str(node.y) + (18 - len(str(node.y))) * " "
        coordinates.append(coords)
    coordinates.append("\n")
    return coordinates


def create_subcatchment_polygons(nodes: pd.DataFrame, voro):
    """Returns a list of strings for the polygons section"""

    polygons = ["[Polygons]",
                ";;Subcatchment   X-Coord            Y-Coord",
                ";;-------------- ------------------ ------------------"]

    polytopes = voro.polytopes
    for index, node in nodes.iterrows():
        if node.role == "node":
            polygon = polytopes[index]

            for point in polygon:
                poly_point = "sub_" + str(index) + (17 - 4 - len(str(index))) * " "
                poly_point += str(round(point[0], 2)) + \
                    (19 - len(str(round(point[0], 2)))) * " "
                poly_point += str(round(point[1], 2)) + \
                    (18 - len(str(round(point[1], 2)))) * " "
                polygons.append(poly_point)

    polygons.append("\n")
    return polygons


def create_symbols(nodes: pd.DataFrame):
    """Returns a list of strings for the symbols section"""

    symbols = ["[SYMBOLS]",
                ";;Gage           X-Coord            Y-Coord",
                ";;-------------- ------------------ ------------------",]
    gage = "General          "
    gage += str(round(nodes.x.min()-100, 2)) + \
(19 - len(str(round(nodes.x.min()-100, 2)))) * " "
    gage += str(round(nodes.y.max()+100, 2)) + \
(19 - len(str(round(nodes.y.max()+100, 2)))) * " "
    symbols.append(gage)
    symbols.append("\n")
    return symbols


def tester():
    """For testing purposes only"""
    print("The swmm_formater script has run")


if __name__ == "__main__":
    tester()
