# depgraph/back/graph/_base.py

from pathlib import Path
from typing import List, Tuple, Dict, Any
import networkx as nx
import pandas as pd
from networkx.drawing.nx_pydot import to_pydot
import xml.etree.ElementTree as ET

class GraphControl:
    """
    Manages the creation, manipulation, and visualization of a dependency graph.
    """

    def __init__(self):
        self.graph = nx.Graph()
    
    def add_modules_to_graph(self, modules: Dict[str, Path]):
        """
        Adds module and package nodes to the graph.

        Args:
            modules (Dict[str, Path]): A dictionary of module names and their paths.
        """
        nodes = []
        for full_name, path in modules.items():
            if path.name == "__init__.py":
                node_type = "package"
            else:
                node_type = "module"

            nodes.append((
                full_name,  # Unique node key
                {
                    "path": path,
                    "type": node_type
                }
            ))
        self.graph.add_nodes_from(nodes)

    def print_nx_nodes(self):
        """
        Prints a table of all graph nodes and their attributes.
        """
        nodes_data = [(node, *attrs.values()) for node, attrs in self.graph.nodes(data=True)]
        
        if len(self.graph.nodes) > 0:
            attr_keys = list(next(iter(dict(self.graph.nodes(data=True)).values())).keys())
        else:
            attr_keys = []

        df = pd.DataFrame(nodes_data, columns=["node"] + attr_keys)
        print(df.to_string(index=False))

    def add_dependencies_to_graph(self, dependencies: List[Tuple[Path, List[Tuple[str, Path]]]]):
        """
        Adds edges to the graph based on the list of dependencies.

        Args:
            dependencies (list): A list of dependencies in the format:
                [
                (Path_to_source, [
                    (full_module_name, Path_to_module),
                    ...
                ]),
                ...
                ]
        """
        # Create a mapping from path to node name
        path_to_node = {attrs["path"]: node for node, attrs in self.graph.nodes(data=True)}

        for source_path, deps in dependencies:
            source_node = path_to_node.get(source_path)
            if not source_node:
                continue

            for dep_full_name, dep_path in deps:
                target_node = path_to_node.get(dep_path)
                if target_node:
                    self.graph.add_edge(source_node, target_node)
    
    def build_from_dependencies(self, dependencies: List[Tuple[Path, List[Tuple[str, Path]]]],
                                python_modules: Dict[str, Path]):
        """
        Builds the complete graph from dependencies and module list.
        """
        self.add_modules_to_graph(python_modules)
        self.add_dependencies_to_graph(dependencies)
    
    def draw_graph_pydot(self, filename: str = "graph.png"):
        """
        Visualizes the dependency graph using pydot.

        Args:
            filename (str): The path to save the image.
        """
        pydot_graph = to_pydot(self.graph)

        # Node styling
        for node in pydot_graph.get_nodes():
            node_name = node.get_name().strip('"')
            if node_name in self.graph.nodes:
                attrs = self.graph.nodes[node_name]
                node_type = attrs.get("type", "module")
                if node_type == "package":
                    node.set_shape("box")
                    node.set_style("filled")
                    node.set_fillcolor("lightblue")
                else:
                    node.set_shape("ellipse")
                    node.set_style("filled")
                    node.set_fillcolor("lightgreen")
            node.set_fontname("Courier")
            node.set_fontsize(10)

        # Edge styling
        for edge in pydot_graph.get_edges():
            edge.set_color("gray")
            edge.set_arrowsize(0.7)

        pydot_graph.write_png(filename)
        print(f"PyDot graph saved to {filename}")

    def draw_dependency_table(self, filename: str = "dependencies.xml"):
        """
        Saves module dependencies from the graph to an XML file.
        
        Args:
            filename (str): The path to save the XML file.
        """
        root = ET.Element("modules")

        for node in sorted(self.graph.nodes()):
            node_type = self.graph.nodes[node].get("type", "module")
            module_elem = ET.SubElement(root, "module", name=node, type=node_type)

            for neighbor in sorted(self.graph.neighbors(node)):
                neighbor_type = self.graph.nodes[neighbor].get("type", "module")
                ET.SubElement(module_elem, "dependency", name=neighbor, type=neighbor_type)

        tree = ET.ElementTree(root)
        tree.write(filename, encoding="utf-8", xml_declaration=True)
        print(f"Dependencies saved to {filename}")

    def to_json_serializable(self) -> Dict[str, List[Any]]:
        """
        Converts the graph to a JSON-serializable dictionary.
        This is a convenient API for a web frontend.

        Returns:
            Dict[str, List[Any]]: A dictionary with 'nodes' and 'edges'.
        """
        nodes_data = []
        for node_name, data in self.graph.nodes(data=True):
            nodes_data.append({
                "name": node_name,
                "type": data.get("type", "module")
            })

        edges_data = []
        for u, v in self.graph.edges():
            edges_data.append({"source": u, "target": v})
        
        return {
            "nodes": nodes_data,
            "edges": edges_data
        }
