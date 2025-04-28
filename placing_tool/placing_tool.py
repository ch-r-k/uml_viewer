import os
import time
import shutil
import tempfile
import xml.etree.ElementTree as ET
import subprocess

from application.interface import UmlExporter
from core.uml_class import UmlClass
from core.uml_relationshpi import UmlRelationship
from export.drawio_exporter import DrawioUmlExporter

class DrawioPositionTool:
    def __init__(self, exporter: UmlExporter = None):
        self.exporter = exporter or DrawioUmlExporter()

    def open_in_vscode(self, file_path: str):
        subprocess.Popen(["code", "--wait", file_path])

    def update_positions_from_file(self, classes: list[UmlClass], file_path: str):
        tree = ET.parse(file_path)
        root = tree.getroot()
        graph_root = root.find(".//root")

        if graph_root is None:
            print("No graph root found in the file.")
            return

        for cell in graph_root.findall("mxCell"):
            cell_id = cell.attrib.get("id")
            geometry = cell.find("mxGeometry")
            if geometry is not None and geometry.attrib.get("as") == "geometry":
                x = float(geometry.attrib.get("x", 0))
                y = float(geometry.attrib.get("y", 0))

                for uml_class in classes:
                    if str(uml_class.class_id) == cell_id:
                        uml_class.position = (x, y)
                        break

    def prepare_temp_file(self, template_path: str = None) -> str:
        # Create a temporary file for editing
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".drawio")
        temp_file_path = temp.name
        temp.close()

        if template_path and os.path.exists(template_path):
            shutil.copy(template_path, temp_file_path)
            print(f"Template {template_path} copied to temp file {temp_file_path}")
        else:
            print(f"No template used. Empty temp file created at {temp_file_path}")

        return temp_file_path

    def run(self, classes: list[UmlClass], relationships: list[UmlRelationship], file_path: str, template_path: str = None):
        # Step 1: Prepare a temporary file
        temp_file_path = self.prepare_temp_file(template_path)

        # Step 2: Export UML diagram into the temp file
        self.exporter.export(classes, relationships, temp_file_path)

        # Step 3: Open the temp file in VS Code
        last_mtime = os.path.getmtime(temp_file_path)
        print("Opening in VS Code Draw.io...")
        self.open_in_vscode(temp_file_path)

        # Step 4: Wait for user to save changes
        print("Waiting for file to be modified...")
        while True:
            time.sleep(1)
            current_mtime = os.path.getmtime(temp_file_path)
            if current_mtime != last_mtime:
                print("Temp file was modified. Reloading positions.")
                self.update_positions_from_file(classes, temp_file_path)
                break

        # (Optional: you could copy back from temp_file_path to file_path if you want to save final result)
        # shutil.copy(temp_file_path, file_path)

        # Step 5: Clean up
        try:
            os.remove(temp_file_path)
            print(f"Temporary file {temp_file_path} removed.")
        except Exception as e:
            print(f"Could not remove temporary file: {e}")

        return classes
