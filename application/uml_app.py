# uml_app.py

from typing import List, Tuple
import re

from core.uml_class import UmlClass
from core.uml_relationshpi import UmlRelationship

from importer.json_importer import JsonUmlImporter
from class_generators.plantuml_class_generator import PlantUmlClassDiagramGenerator
from class_generators.graphviz_class_generator import GraphvizClassDiagramGenerator
from export.drawio_exporter import DrawioUmlExporter
from export.graphviz_exporter import GraphvizUmlExporter
from placing_tool.placing_tool import DrawioPositionTool

class UmlClassDiagram:
    def __init__(self):
        self.uml_classes: List[UmlClass] = []
        self.relationships: List[UmlRelationship] = [] 
        self.json_importer = JsonUmlImporter()  # Create an instance of JsonUmlImporter
        self.class_generator = PlantUmlClassDiagramGenerator()
        self.class_generator_graphviz = GraphvizClassDiagramGenerator()
        self.exporter = DrawioUmlExporter()
        self.exporter_graphviz = GraphvizUmlExporter()
        self.tool = DrawioPositionTool()
        self.position_file = ""

    def import_file(self, file):
        self.uml_classes, self.relationships = JsonUmlImporter.import_classes_and_relationships(self.json_importer, file)

    def import_positions(self, file):
        self.uml_classes = JsonUmlImporter.import_posittions(self.json_importer, file)
        self.position_file = file

    def gernate_classes(self):
        for element in self.uml_classes:
            png_data = self.class_generator_graphviz.generate_png(element)
            element.png_data = png_data

            svg_data = self.class_generator_graphviz.generate_svg(element)
            element.svg_data = svg_data["svg"]

            code_data = self.class_generator_graphviz.generate_graphviz_lable(element)
            element.code_data = code_data

            element.size = (svg_data["width"], svg_data["height"])

    def export_diagram(self):
        self.exporter.export(self.uml_classes, self.relationships, "output/test.drawio")
        self.exporter_graphviz.export(self.uml_classes, self.relationships, "output/test.gv")

    def place(self):
        self.uml_classes = self.tool.run(self.uml_classes, self.relationships, "diagram.drawio")
        self.json_importer.save_positions(self.uml_classes, self.position_file)

    def _extract_svg_size(self, svg_data: str) -> Tuple[float, float]:
        width_match = re.search(r'width="([\d.]+)([a-z]*)"', svg_data)
        height_match = re.search(r'height="([\d.]+)([a-z]*)"', svg_data)

        if width_match and height_match:
            width = float(width_match.group(1))
            height = float(height_match.group(1))
            return width, height
        else:
            # Default size if not found
            return 100.0, 100.0




