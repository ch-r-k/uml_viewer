# json_importer.py
import json
from typing import List

from core.uml_class import UmlClass
from core.uml_relationshpi import UmlRelationship
from application.interface import UmlImporter


class JsonUmlImporter(UmlImporter):
    def __init__(self):
        self.uml_classes: List[UmlClass] = []
        self.relationships: List[UmlRelationship] = []

    def import_classes_and_relationships(self, input_path:str):
        with open(input_path, 'r') as json_input:
            class_data = json.load(json_input)

        self.load_class(class_data['elements'])
        self.load_relationships(class_data['relationships'])

        return  self.uml_classes, self.relationships
    
    def import_posittions(self, input_path:str):
        with open(input_path, 'r') as json_input:
            position_data = json.load(json_input)
        
        self.load_positions(position_data['classes'])

        return self.uml_classes
    
    def save_positions(self, uml_classes: List[UmlClass], file_path: str):
        classes_data = []
        for element in uml_classes:
            classes_data.append({
                "id": element.class_id,  # Make sure this matches your actual UmlClass attributes
                "name": element.name,
                "position": {
                    "x": element.position[0],
                    "y": element.position[1]
                }
            })

        with open(file_path, 'w') as f:
            json.dump({"classes": classes_data}, f, indent=4)
    
    # -------------------------------------------------------------

    def load_class(self, class_data):
        def process_elements(elements, group_path):
            for class_data_item in elements:
                display_name = class_data_item.get("display_name", "")

                # Build new group path for this element level
                current_group_path = group_path + [display_name] if display_name else group_path

                if class_data_item.get("type") == "class":
                    class_id = class_data_item['id']
                    name = class_data_item['name']
                    methods = class_data_item.get('methods', [])
                    is_abstract = class_data_item.get("is_abstract", False)

                    position = (0.0, 0.0)
                    size = (0.0, 0.0)
                    svg_data = []
                    png_data = []
                    code_data = []

                    # Join the group path for display or keep it as list depending on UmlClass constructor
                    groups = current_group_path

                    uml_class = UmlClass(class_id, name, methods, is_abstract, groups, position, size, svg_data, png_data, code_data)
                    self.uml_classes.append(uml_class)

                if "elements" in class_data_item:
                    process_elements(class_data_item["elements"], current_group_path)

        process_elements(class_data, [])
    
    def load_relationships(self, relationships_data):        
        for relationship in relationships_data:
            source_id = relationship['source']
            destination_id = relationship['destination']
            relationship_type = relationship['type']
            access = relationship.get('access', 'public')
            label = relationship.get('label')
            
            uml_relationship = UmlRelationship(source_id, destination_id, relationship_type, access, label)
            self.relationships.append(uml_relationship)



    def load_positions(self, position_data):
        # Get the list of class position entries from the wrapped "classes" key

        for position_item in position_data:
            class_id = position_item['id']
            position = (
                position_item['position']['x'],
                position_item['position']['y']
            )

            # Find the UmlClass with the matching class_id
            uml_class = next((uc for uc in self.uml_classes if uc.class_id == class_id), None)

            if uml_class:
                uml_class.position = position
            else:
                print(f"Warning: UmlClass with ID {class_id} not found.")
    