# drawio_exporter.py
import base64
import xml.etree.ElementTree as ET

from application.interface import UmlExporter
from core.uml_class import UmlClass
from core.uml_relationshpi import UmlRelationship

class DrawioUmlExporter(UmlExporter):

    def export(self, classes: list[UmlClass], relationships: list[UmlRelationship], output_path: str):
        def encode_svg(svg_text: str) -> str:
            try:
                return base64.b64encode(svg_text.encode("utf-8")).decode("utf-8")
            except Exception as e:
                print(f"Error encoding SVG data: {e}")
                return ""

        mxfile = ET.Element("mxfile")
        diagram_node = ET.SubElement(mxfile, "diagram", name="UML Class Diagram")
        model = ET.SubElement(diagram_node, "mxGraphModel")
        root = ET.SubElement(model, "root")

        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")

        class_id_map = {}
        edge_counter = 1

        for uml_class in classes:
            x, y = uml_class.position
            width, height = uml_class.size
            image_data = encode_svg(uml_class.svg_data)
            if image_data:
                img_src = f"data:image/svg+xml;base64,{image_data}"
                cell = ET.SubElement(root, "mxCell",
                    id=str(uml_class.class_id),
                    value=f"<img width='{width}' height='{height}' src='{img_src}'>",
                    style="rounded=0;whiteSpace=wrap;html=1;",
                    vertex="1",
                    parent="1")
                ET.SubElement(cell, "mxGeometry", x=str(x), y=str(y), width=str(width), height=str(height), **{"as": "geometry"})
                class_id_map[uml_class.class_id] = uml_class.class_id

        for rel in relationships:
            src = class_id_map.get(rel.source)
            dst = class_id_map.get(rel.destination)
            if not src or not dst:
                continue

            style = "edgeStyle=elbowEdgeStyle;rounded=1;"
            if rel.type == "extension" or rel.type == "inheritance":
                style += "endArrow=block;"
            elif rel.type == "association":
                style += "endArrow=open;"
            elif rel.type == "dependency":
                style += "dashed=1;endArrow=open;"
            elif rel.type == "aggregation":
                style += "endArrow=diamond;"
            elif rel.type == "composition":
                style += "endArrow=diamond;fillColor=black;"

            edge = ET.SubElement(root, "mxCell",
                id=f"edge_{edge_counter}",
                value=rel.label or "",
                style=style,
                edge="1",
                parent="1",
                source=str(src),
                target=str(dst))
            ET.SubElement(edge, "mxGeometry", relative="1", **{"as": "geometry"})
            edge_counter += 1

        tree = ET.ElementTree(mxfile)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)
        print(f"Draw.io diagram exported to {output_path}")