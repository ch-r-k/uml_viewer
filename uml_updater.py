import json
import os
from uml_class import UmlClassDiagram  # Assuming UmlClassDiagram is in uml_class.py

if __name__ == "__main__":
    # Load class data from JSON file
    with open('input/blinky.json', 'r') as json_input:
        class_data = json.load(json_input)

    # Load existing positions (if available)
    positions_path = 'input/blinky_positions.json'
    if os.path.exists(positions_path):
        with open(positions_path, 'r') as positions_input:
            positions_data = json.load(positions_input)
    else:
        positions_data = {"classes": []}

    # Instantiate UML Class Diagram and load classes
    classDiagram = UmlClassDiagram()
    classDiagram.load_uml_classes(class_data['elements'], positions_data)
    classDiagram.load_relationships(class_data.get('relationships', []))
    
    # Update positions from Draw.io file if available
    drawio_file = "output/diagram.drawio"
    if os.path.exists(drawio_file):
        classDiagram.update_positions_from_drawio(drawio_file, positions_data)
    else:
        print(f"Warning: {drawio_file} not found. Skipping position update.")
    
    # Sync positions_data with classDiagram.uml_classes
    updated_positions = {"classes": []}
    for uml_class in classDiagram.uml_classes:
        updated_positions["classes"].append({
            "id": uml_class.class_id,
            "x": uml_class.position[0],
            "y": uml_class.position[1]
        })
    
    # Save updated positions to JSON file
    with open(positions_path, 'w') as positions_output:
        json.dump(updated_positions, positions_output, indent=4)
    
    print("Updated positions saved to", positions_path)
