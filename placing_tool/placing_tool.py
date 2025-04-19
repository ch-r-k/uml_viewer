import os
import time
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

    def run(self, classes: list[UmlClass], relationships: list[UmlRelationship], file_path: str):
        self.exporter.export(classes, relationships, file_path)

        last_mtime = os.path.getmtime(file_path)
        print("Opening in VS Code Draw.io...")
        self.open_in_vscode(file_path)

        print("Waiting for file to be modified...")
        while True:
            time.sleep(1)
            current_mtime = os.path.getmtime(file_path)
            if current_mtime != last_mtime:
                print("File was modified. Reloading positions.")
                self.update_positions_from_file(classes, file_path)
                break

        return classes
