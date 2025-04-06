import subprocess
import tempfile
import os
import atexit
from core.uml_class import UmlClass
from application.interface import ClassImageGenerator

class PlantUmlClassDiagramGenerator(ClassImageGenerator):
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

    def generate_plantuml(self, uml_class):
        """
        Generates the PlantUML code for a given UmlClass object.
        """
        class_name = uml_class.name
        methods = uml_class.methods
        is_abstract = uml_class.is_abstract

        plantuml_code = "@startuml\n"

        plantuml_code += """
        skinparam classAttributeIconSize 0
        skinparam classBackgroundColor LightGray
        skinparam classBorderColor Black
        skinparam classFontStyle Bold
        skinparam classFontColor Black
        skinparam shadowing false
        skinparam Padding 0
        skinparam Margin 0
        """

        class_declaration = "abstract class" if is_abstract else "class"
        plantuml_code += f"    {class_declaration} {class_name} {{\n"

        for method in methods:
            method_signature = f"        + {method['name']}()"
            if method.get("is_pure_virtual"):
                method_signature += " *"
            plantuml_code += method_signature + "\n"

        plantuml_code += "    }\n@enduml"
        return plantuml_code

    def generate_svg_from_puml(self, uml_code):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".puml", mode="w", encoding="utf-8") as puml_file:
            puml_file.write(uml_code)
            puml_path = puml_file.name
            self._temp_files.append(puml_path)

        svg_path = puml_path.replace(".puml", ".svg")

        subprocess.run(["plantuml", "-tsvg", puml_path], capture_output=True)

        with open(svg_path, "r", encoding="utf-8") as svg_file:
            svg_content = svg_file.read()

        self._temp_files.append(svg_path)
        return svg_content

    def generate_png_from_puml(self, uml_code):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".puml", mode="w", encoding="utf-8") as puml_file:
            puml_file.write(uml_code)
            puml_path = puml_file.name
            self._temp_files.append(puml_path)

        png_path = puml_path.replace(".puml", ".png")

        subprocess.run(["plantuml", "-tpng", puml_path], capture_output=True)

        with open(png_path, "rb") as png_file:
            png_data = png_file.read()

        self._temp_files.append(png_path)
        return png_data

    def generate_svg(self, uml_class: UmlClass):
        uml_code = self.generate_plantuml(uml_class)
        svg_data = self.generate_svg_from_puml(uml_code)
        print("Generated SVG data")
        return svg_data

    def generate_png(self, uml_class: UmlClass):
        uml_code = self.generate_plantuml(uml_class)
        png_data = self.generate_png_from_puml(uml_code)
        print("Generated PNG data")
        return png_data
