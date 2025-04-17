import os
import atexit
from graphviz import Digraph
from PIL import Image
from core.uml_class import UmlClass
from application.interface import ClassImageGenerator
from graphviz import Source

class GraphvizClassDiagramGenerator(ClassImageGenerator):
    def __init__(self, output_folder='class_diagrams'):
        self.output_folder = output_folder
        self._temp_files = []
        atexit.register(self._cleanup_temp_files)

    def _cleanup_temp_files(self):
        for file_path in self._temp_files:
            try:
                os.unlink(file_path)
            except OSError:
                pass

    def generate_graphviz_code(self, uml_class: UmlClass) -> str:
        methods = "\\l".join(
            method.get("name", "") if isinstance(method, dict) else str(method)
            for method in uml_class.methods
        ) + "\\l"

        label = f"{{ {uml_class.name} | {methods} }}"
        uml_class.label = label  # 👈 Store the label for later use

        dot_code = f"""
            digraph {{
                node [shape=record, fontsize=12, fontname="Helvetica"];
                {uml_class.class_id} [label="{label}"];
            }}
        """
        return dot_code
    
    def generate_graphviz_lable(self, uml_class: UmlClass) -> str:
        methods = "\\l".join(
            method.get("name", "") if isinstance(method, dict) else str(method)
            for method in uml_class.methods
        ) + "\\l"

        label = f"{{ {uml_class.name} | {methods} }}"
        uml_class.label = label  # 👈 Store the label for later use

        return label

    def generate_svg(self, uml_class: UmlClass):
        dot_code = self.generate_graphviz_code(uml_class)

        dot = Source(dot_code, format='svg')
        svg_path = dot.render()
        self._temp_files.append(svg_path)

        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()

        width, height = self._extract_svg_size(svg_content)
        return {
            "svg": svg_content,
            "dot": dot_code,
            "width": width,
            "height": height,
            "label": uml_class.label  # optional if needed elsewhere
        }

    def generate_png(self, uml_class: UmlClass):
        dot_code = self.generate_graphviz_code(uml_class)

        dot = Source(dot_code, format='png')
        png_path = dot.render()
        self._temp_files.append(png_path)

        with open(png_path, "rb") as f:
            png_data = f.read()

        with Image.open(png_path) as img:
            width, height = img.size

        return {
            "png": png_data,
            "dot": dot_code,
            "width": width,
            "height": height,
            "label": uml_class.label  # optional if needed elsewhere
        }

    def _extract_svg_size(self, svg_content: str):
        """
        Extracts width and height from an SVG's root element.
        """
        import xml.etree.ElementTree as ET

        try:
            root = ET.fromstring(svg_content)
            width = root.get('width', '').replace('pt', '').replace('px', '')
            height = root.get('height', '').replace('pt', '').replace('px', '')

            try:
                width = float(width)
                height = float(height)
            except ValueError:
                width = height = None

            return width, height
        except ET.ParseError:
            return None, None
