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
        dot = graphviz.Digraph("UML_Class_Diagram", format="svg")
        dot.attr(overlap="false", layout="nop2", splines="curved", inputscale="1")

        for uml_class in classes:
            pos = f"{uml_class.position[0]},{-uml_class.position[1]}!"

            if uml_class.png_data:
                # Write png_data to a temporary file inside the custom temp folder
                temp_file = tempfile.NamedTemporaryFile(
                    dir=self.temp_dir, suffix=".png", delete=False
                )
                temp_file.write(uml_class.png_data)
                temp_file.close()
                self._temp_files.append(temp_file.name)

                dot.node(
                    uml_class.class_id,
                    image=temp_file.name,
                    shape="none",
                    pos=pos,
                    imagescale="true"
                )
            else:
                methods = "\\l".join(
                    method.get("name", "") if isinstance(method, dict) else str(method)
                    for method in uml_class.methods
                ) + "\\l"
                label = f"{{ {uml_class.name} | {methods} }}"
                dot.node(uml_class.class_id, label=label, shape="record", pos=pos)

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
                rel.source,
                rel.destination,
                label=rel.label or "",
                style=style,
                arrowhead=arrowhead,
                constraint="false"
            )

        dot.render(output_path, format="png")
        print(f"Graphviz UML diagram exported to {output_path}.png")
