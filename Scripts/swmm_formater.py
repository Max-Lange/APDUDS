"""Defines the function needed for creating the SWMM file
"""

from datetime import datetime
import pandas as pd

def swmm_file_creator(nodes: pd.DataFrame, edges: pd.DataFrame, voro, settings: dict):
    """Creates a .txt file which follows the System Water Management Model format, so that the
    created network can be used in that software

    Args:
        nodes (DataFrame): The nodes of the system along with their attributes
        edges (DataFrame): The conduits of the system along with their attributes
        voro (locality.voronoi): Voronoi calculator of the subcatchments areas
        settings (dict): system parameters
        filename (str): name of the SWMM file
    """

    date = datetime.today().strftime('%m/%d/%Y')

    with open(f"{settings['filename']}.txt", 'w', encoding="utf8") as file:

        # Create title
        title = ["[TITLE]",
                 ";;Project Title/Notes",
                 "\n"]
        file.write('\n'.join(title))

        # Recreate the standard options (units in [m])
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
                   "END_TIME             06:00:00",
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
        file.write('\n'.join(options))

        # Create Evaporation
        evaporation = ["[EVAPORATION]",
                    ";;Data Source    Parameters",
                    ";;-------------- ----------------",
                    "CONSTANT         0.0",
                    "DRY_ONLY         NO",
                    "\n"]
        file.write('\n'.join(evaporation))

        # Create the single raingage
        raingages = ["[RAINGAGES]",
                     ";;Name           Format    Interval SCF      Source ",
                     ";;-------------- --------- ------ ------ ----------",
                     "General          INTENSITY 1:00     1.0      TIMESERIES",
                     "\n",]
        file.write('\n'.join(raingages))

        # Create the subcatchment areas, and apply the general raingage
        subcatchments = ["[SUBCATCHMENTS]",
                         ";;Name           Rain Gage        Outlet           Area     %Imperv  \
Width    %Slope   CurbLen  SnowPack",
                         ";;-------------- ---------------- ---------------- -------- -------- \
-------- -------- -------- ----------------"]

        for node_index, node in nodes.iterrows():
            if node.role == "node":
                nr_length = len(str(node_index))
                catchment = f"sub_{node_index}" + (17 - 4 - nr_length) * " "
                catchment += "General" + (17 - 7) * " "
                catchment += "j_" + str(node_index) + (17 - 2 - nr_length) * " "
                catchment += str(round(node.area * 0.0001, 4)) + \
(9 - len(str(round(node.area * 0.0001, 4)))) * " "
                catchment += str(settings['perc_inp']) + (9 - len(str(settings['perc_inp']))) * " "
                catchment += "500      0.5      0"

                subcatchments.append(catchment)
        subcatchments.append("\n")
        file.write('\n'.join(subcatchments))

        # Create the subareas for the subcatchments
        subareas = ["[SUBAREAS]",
                    ";;Subcatchment   N-Imperv   N-Perv     S-Imperv   S-Perv     PctZero    \
RouteTo    PctRouted",
                    ";;-------------- ---------- ---------- ---------- ---------- ---------- \
---------- ----------"]

        for node_index, node in nodes.iterrows():
            if node.role == "node":
                nr_length = len(str(node_index))
                subarea = f"sub_{node_index}" + (17 - 4 - nr_length) * " "
                subarea += "0.01       0.1        0.05       0.05       25         OUTLET"

                subareas.append(subarea)
        subareas.append("\n")
        file.write('\n'.join(subareas))

        # Create the infiltration information for the subcatchments (default parameters)
        infiltration = ["[INFILTRATION]",
                        ";;Subcatchment   Param1     Param2     Param3     Param4     Param5",
                        ";;-------------- ---------- ---------- ---------- ---------- ----------",]

        for node_index, node in nodes.iterrows():
            if node.role == "node":
                nr_length = len(str(node_index))
                infil = f"sub_{node_index}" + (17 - 4 - nr_length) * " "
                infil += "3.0        0.5        4          7          0"

                infiltration.append(infil)
        infiltration.append("\n")
        file.write('\n'.join(infiltration))

        # Create the junctions
        junctions = ["[JUNCTIONS]",
                     ";;Name           Elevation  MaxDepth   InitDepth  SurDepth   Aponded",
                     ";;-------------- ---------- ---------- ---------- ---------- ----------",]

        for node_index, node in nodes.iterrows():
            if node.role == "node":
                nr_length = len(str(node_index))
                junc = "j_" + str(node_index) + (17 - 2 - nr_length) * " "
                junc += str(node.depth) + (11 - len(str(node.depth))) * " "
                junc += "0          0          0          0"

                junctions.append(junc)
        junctions.append("\n")
        file.write('\n'.join(junctions))

        # Create the outfalls
        outfalls = ["[OUTFALLS]",
                    ";;Name           Elevation  Type       Stage Data       Gated    Route To",
                    ";;-------------- ---------- ---------- ---------------- -------- \
----------------"]

        for index, node in nodes.iterrows():
            if node.role in ["outfall", "overflow"]:
                out = "j_" + str(index) + (17 - 2 - len(str(index))) * " "
                depth = str(nodes.at[index, 'depth'])
                out += depth + (11 - len(depth)) * " "
                out += "FREE                        NO"

                outfalls.append(out)

        outfalls.append("\n")
        file.write('\n'.join(outfalls))

        # Create the conduits
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
        file.write('\n'.join(conduits))

        # Create cross sections for conduits
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
        file.write('\n'.join(xsections))

        # Add the timeseries here


        # Create the report settings
        report = ["[REPORT]",
                  ";;Reporting Options",
                  "SUBCATCHMENTS ALL",
                  "NODES ALL",
                  "LINKS ALL",
                  "\n"]
        file.write('\n'.join(report))

        # Create the tags
        tags = ["[TAGS]",
                "\n"]
        file.write('\n'.join(tags))

        # Create the map settings
        map_settings = ["[MAP]",
                       f"DIMENSIONS {round(nodes.x.min()-200, 2)} {round(nodes.y.min()-200, 2)} \
{round(nodes.x.max()+200, 2)} {round(nodes.y.max()+200, 2)}",
                        "Units      Meters",
                        "\n"]
        file.write('\n'.join(map_settings))

        # Create the junction coordinates
        coordinates = ["[COORDINATES]",
                       ";;Node           X-Coord            Y-Coord",
                       ";;-------------- ------------------ ------------------"]

        for index, node in nodes.iterrows():
            coords = "j_" + str(index) + (17 - 2 - len(str(index))) * " "
            coords += str(node.x) + (19 - len(str(node.x))) * " "
            coords += str(node.y) + (18 - len(str(node.y))) * " "
            coordinates.append(coords)
        coordinates.append("\n")
        file.write('\n'.join(coordinates))


        if settings["polygons"] == "y":
            # Create the subcatchments polygons
            polygons = ["[Polygons]",
                        ";;Subcatchment   X-Coord            Y-Coord",
                        ";;-------------- ------------------ ------------------"]

            polytopes = voro.polytopes
            for index, node in nodes.iterrows():
                if node.role == "node":
                    polygon = polytopes[index]

                    name = "sub_" + str(index) + (17 - 4 - len(str(index))) * " "
                    for point in polygon:
                        poly_point = name
                        poly_point += str(round(point[0], 2)) + \
                            (19 - len(str(round(point[0], 2)))) * " "
                        poly_point += str(round(point[1], 2)) + \
                            (18 - len(str(round(point[1], 2)))) * " "
                        polygons.append(poly_point)

            polygons.append("\n")
            file.write('\n'.join(polygons))

        # Create the map symbols
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
        file.write('\n'.join(symbols))


def tester():
    """For testing purposes only
    """

    from attribute_calculator import voronoi_area
    nodes = pd.read_csv("write_test_nodes_2.csv")
    edges = pd.read_csv("write_test_edges_2.csv")

    settings = {"outfalls":[130], "min_depth":1.1, "min_slope":1/500,
                "rainfall": 70, "perc_inp": 23, "diam_list": [0.25, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                "filename": "test_swmm"}
    _, voro = voronoi_area(nodes)

    swmm_file_creator(nodes, edges, voro, settings)


if __name__ == "__main__":
    tester()
