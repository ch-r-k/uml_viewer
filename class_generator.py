import subprocess
import xml.etree.ElementTree as ET
import os

class ClassDiagramGenerator:
    def __init__(self, output_folder='class_diagrams'):
        self.output_folder = output_folder

    def generate_plantuml(self, uml_class):
        """
        Generates the PlantUML code for a given UmlClass object.

        :param uml_class: The UmlClass object containing class details
        :return: A string containing the PlantUML code
        """
        class_name = uml_class.name
        methods = uml_class.methods
        is_abstract = uml_class.is_abstract

        plantuml_code = "@startuml\n"
        
        # Use a skinparam block for styling
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
            if method["is_pure_virtual"]:
                method_signature += " *"  # Denote pure virtual methods
            plantuml_code += method_signature + "\n"

        plantuml_code += "    }\n"
        plantuml_code += "@enduml"
        return plantuml_code

    def save_and_generate_svg(self, uml_code, output_file):
        """
        Saves the generated PlantUML code to a `.puml` file, then generates the corresponding SVG file.

        :param uml_code: The PlantUML code to be written to the file
        :param output_file: The path to save the generated SVG file
        """
        puml_filename = output_file.replace(".svg", ".puml")
        with open(puml_filename, "w") as f:
            f.write(uml_code)
        
        subprocess.run(["plantuml", "-tsvg", "-tsvg:noclass", puml_filename]) # Generate SVG


                # Parse the generated SVG file
        with open(output_file, "r") as f:
            svg_content = f.read()
        
        tree = ET.ElementTree(ET.fromstring(svg_content))
        root = tree.getroot()
        
        # Find the class rectangle element
        for rect in root.findall(".//{http://www.w3.org/2000/svg}rect"):
            if "width" in rect.attrib and "height" in rect.attrib:
                x = float(rect.attrib.get("x", 0))
                y = float(rect.attrib.get("y", 0))
                width = float(rect.attrib["width"])
                height = float(rect.attrib["height"])
                
                # Update viewBox, width, and height
                root.attrib["viewBox"] = f"{x} {y} {width} {height}"
                root.attrib["width"] = f"{width}px"
                root.attrib["height"] = f"{height}px"
                
                break  # Stop after the first class rect is found
        
        # Write back the modified SVG
        with open(output_file, "w") as f:
            f.write(ET.tostring(root, encoding="unicode"))

    def save_and_generate_png(self, uml_code, output_file):
        """
        Saves the generated PlantUML code to a `.puml` file, then generates the corresponding SVG file.

        :param uml_code: The PlantUML code to be written to the file
        :param output_file: The path to save the generated SVG file
        """
        puml_filename = output_file.replace(".png", ".puml")
        with open(puml_filename, "w") as f:
            f.write(uml_code)
        
        subprocess.run(["plantuml", "-tpng", puml_filename])  # Generate PNG
    
    def process_uml_classes(self, uml_class):
        """
        Processes a list of UmlClass objects, generating PlantUML code and saving corresponding SVG files.

        :param uml_classes: A list of UmlClass objects to be processed
        """

        # Create the folder if it doesn't exist
        if not os.path.exists(self.output_folder):
            os.makedirs(self.output_folder)

        # Generate the UML code for each class
        uml_code = self.generate_plantuml(uml_class)
        
        # Define the output file path in the specified folder
        output_file_svg = os.path.join(self.output_folder, f"{uml_class.class_id}.svg")
        
        # Save the UML code and generate the SVG
        self.save_and_generate_svg(uml_code, output_file_svg)
        print(f"Class diagram saved as {output_file_svg}")

        # Define the output file path in the specified folder
        output_file_png = os.path.join(self.output_folder, f"{uml_class.class_id}.png")

        # Save the UML code and generate the PNG
        self.save_and_generate_png(uml_code, output_file_png)
        print(f"Class diagram saved as {output_file_png}")
        