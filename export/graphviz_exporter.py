# graphviz_exporter.py
import os
import tempfile
import atexit
import graphviz
from application.interface import UmlExporter
from core.uml_class import UmlClass
from core.uml_relationshpi import UmlRelationship

class GraphvizUmlExporter(UmlExporter):
    def __init__(self):
        # Create a dedicated temp directory for image files
        self.temp_dir = os.path.join(tempfile.gettempdir(), "graphviz_uml_temp")
        os.makedirs(self.temp_dir, exist_ok=True)

        self._temp_files = []
        atexit.register(self._cleanup_temp_files)

    def _cleanup_temp_files(self):
        for file_path in self._temp_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass

    def export(self, classes: list[UmlClass], relationships: list[UmlRelationship], output_path: str):
        dot = graphviz.Digraph("UML_Class_Diagram", format="png")
        dot.attr(layout="neato", splines="curved", inputscale="1")

        # Add global spacing and node padding
        dot.attr("graph")
        dot.attr("node")

        # Step 1: Organize classes into a tree based on group path
        class_group_tree = {}

        for uml_class in classes:
            node = class_group_tree
            for group in uml_class.groups:
                node = node.setdefault(group, {})
            node.setdefault("_classes", []).append(uml_class)

        # Step 2: Recursive function to add clusters and class nodes
        def add_clusters(parent_graph, group_dict, prefix=""):
            for group_name, subgroups in group_dict.items():
                if group_name == "_classes":
                    for uml_class in subgroups:
                        x, y = uml_class.position[0] / 96, -uml_class.position[1] / 96
                        pos = f"{x},{y}!"

                        # Main class node
                        parent_graph.node(
                            str(uml_class.class_id),
                            label=uml_class.code_data,
                            shape="record",
                            pos=pos,
                            style="filled",  # Changed from "invis" to "filled"
                            fillcolor="lightgray",
                        )

                        # Add invisible padding node to push cluster box away
                        margin = 70.0 / 96.0
                        pad_x = (uml_class.size[0] / 70.0) + margin
                        pad_y = (uml_class.size[1] / 70.0) + margin
                        pos = f"{x},{y}!"

                        parent_graph.node(
                            f"{uml_class.class_id}_padding",
                            label="",
                            shape="box",
                            width=str(pad_x),
                            height=str(pad_y),
                            fixedsize="true",
                            style = "invis",
                            pos=pos
                        )
                else:
                    cluster_name = f"cluster_{prefix}{group_name}"
                    with parent_graph.subgraph(name=cluster_name) as sub:
                        sub.attr(label=group_name, style="rounded", color="black")
                        add_clusters(sub, subgroups, prefix=f"{prefix}{group_name}_")

        # Step 3: Build nested clusters
        add_clusters(dot, class_group_tree)

        # Step 4: Draw relationships
        for rel in relationships:
            style, arrowhead = "solid", "none"
            if rel.type == "inheritance":
                arrowhead = "empty"
            elif rel.type == "association":
                arrowhead = "open"
            elif rel.type == "dependency":
                style = "dashed"; arrowhead = "open"
            elif rel.type == "aggregation":
                arrowhead = "diamond"
            elif rel.type == "composition":
                arrowhead = "diamond"; style = "bold"

            dot.edge(
                str(rel.source),
                str(rel.destination),
                label=rel.label or "",
                style=style,
                arrowhead=arrowhead,
                constraint="false"
            )

        dot.render(output_path, format="svg")
        print(f"Graphviz UML diagram exported to {output_path}.svg")
