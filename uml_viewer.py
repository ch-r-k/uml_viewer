import json
import os
from class_generator import ClassDiagramGenerator
from uml_class import UmlClassDiagram  # Assuming UmlClass and UmlClassLoader are now in uml_class.py

if __name__ == "__main__":
    # Step 1: Load the class data and position data from JSON files
    with open('input/blinky.json', 'r') as json_input:
        class_data = json.load(json_input)

    with open('input/blinky_positions.json', 'r') as positions_input:
        positions_data = json.load(positions_input)

    # Step 2: Use UmlClassDiagram to create and store UmlClass objects
    classDiagram = UmlClassDiagram()  # Instantiate the diagram
    classDiagram.load_uml_classes(class_data['elements'], positions_data)  # Load UML classes
    classDiagram.load_relationships(class_data.get('relationships', []))  # Load relationships
    
    # Get elements without position and update JSON file
    missing_positions = classDiagram.elements_without_position()
    for uml_class in missing_positions:
        positions_data['classes'].append({
            "id": uml_class.class_id,
            "name": uml_class.name,
            "x": 200,
            "y": 100
        })
    
    # Save updated positions to JSON file
    with open('input/blinky_positions.json', 'w') as positions_output:
        json.dump(positions_data, positions_output, indent=4)

    # Step 3: Generate the SVG files for each class
    output_folder = 'class_diagrams'
    for root, dirs, files in os.walk(output_folder, topdown=False):
       for name in files:
           os.remove(os.path.join(root, name))  # Delete each file
       for name in dirs:
           os.rmdir(os.path.join(root, name))  # Delete each directory
    
    generator = ClassDiagramGenerator(output_folder=output_folder)  # Instantiate the generator
    for uml_class in classDiagram.uml_classes:
       generator.process_uml_classes(uml_class)  # Generate SVG for each UML class

    # Export the diagram to a single SVG file
    classDiagram.export_class_diagram(output_path="output/diagram.drawio")
    classDiagram.export_to_graphviz(output_path="output/diagram.gv")
