#uml_viewer2.py

from application.uml_app import UmlClassDiagram


def main():
    # === Config ===
    umlClassDiagram = UmlClassDiagram()

    json_path_data = "input/blinky.json"
    json_path_pos = "input/blinky_positions.json"
    output_folder = "class_diagrams"
    drawio_output = "output/diagram.drawio"

    # === Step 1: Load JSON data ===
    umlClassDiagram.import_file(json_path_data)
    umlClassDiagram.import_positions(json_path_pos)
    umlClassDiagram.gernate_classes()
    umlClassDiagram.export_diagram()

    print("✅ Done")


if __name__ == "__main__":
    main()