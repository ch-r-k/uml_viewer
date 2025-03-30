from PIL import Image
import os
import cairosvg
import matplotlib
import numpy as np
import xml.etree.ElementTree as ET
import base64

class UmlRelationship:
    def __init__(self, source, destination, relationship_type, access, label=None):
        self.source = source
        self.destination = destination
        self.type = relationship_type
        self.access = access
        self.label = label

    def __repr__(self):
        return f"UmlRelationship({self.source} -> {self.destination}, {self.type}, {self.access}, {self.label})"


class UmlClass:
    def __init__(self, class_id, name, methods, is_abstract, position, size, svg_path):
        self.class_id = class_id
        self.name = name
        self.methods = methods
        self.is_abstract = is_abstract
        self.position = position  # tuple (x, y)
        self.size = size
        self.svg_path = svg_path
        self.relationships = []  # List to store relationships

    def add_relationship(self, relationship):
        self.relationships.append(relationship)

    def __repr__(self):
        return f"UmlClass({self.class_id}, {self.name}, {self.position}, {self.svg_path})"


class UmlClassDiagram:
    def __init__(self, class_folder='class_diagrams'):
        self.class_folder = class_folder
        self.uml_classes = []
        self.relationships = []

        matplotlib.use("TkAgg")  # or "Qt5Agg"

    def load_uml_classes(self, class_data, positions_data):
        """
        Recursively process the class data and position data and store UmlClass objects.
        """
        positions = {item['id']: (item['x'], item['y']) for item in positions_data['classes']}

        def get_svg_size(svg_path):
            try:
                png_path = svg_path.replace(".svg", ".png")
                cairosvg.svg2png(url=svg_path, write_to=png_path)
                with Image.open(png_path) as img:
                    return img.size  # (width, height)
            except Exception as e:
                print(f"Error reading SVG size: {e}")
                return (100, 200)  # Default size

        def process_elements(elements):
            for class_data_item in elements:
                if class_data_item.get("type") == "class":
                    class_id = class_data_item['id']
                    name = class_data_item['name']
                    methods = class_data_item.get('methods', [])
                    is_abstract = class_data_item.get('is_abstract', False)
                    position = positions.get(class_id, (0, 0))  # Fixed position from input data
                    svg_path = os.path.join(self.class_folder, f"{class_id}.svg")
                    
                    size = get_svg_size(svg_path) if os.path.exists(svg_path) else (100, 200)
                    
                    uml_class = UmlClass(class_id, name, methods, is_abstract, position, size, svg_path)
                    self.uml_classes.append(uml_class)

                if "elements" in class_data_item:
                    process_elements(class_data_item["elements"])

        process_elements(class_data)

    def load_relationships(self, relationships_data):
        """
        Load relationships and associate them with the corresponding UmlClass objects.
        """
        class_map = {uml_class.class_id: uml_class for uml_class in self.uml_classes}
        
        for relationship in relationships_data:
            source_id = relationship['source']
            destination_id = relationship['destination']
            relationship_type = relationship['type']
            access = relationship.get('access', 'public')
            label = relationship.get('label')
            
            uml_relationship = UmlRelationship(source_id, destination_id, relationship_type, access, label)
            self.relationships.append(uml_relationship)
            
            if source_id in class_map:
                class_map[source_id].add_relationship(uml_relationship)

    def elements_without_position(self):
        """Return all classes with the default position (0,0)."""
        return [uml_class for uml_class in self.uml_classes if uml_class.position == (0, 0)]

    def export_class_diagram(self, output_path="diagram.drawio"):
        """
        Exports the UML class diagram as a Draw.io (diagrams.net) XML file using embedded PNG images for each class.
        """
        def encode_image(image_path):
            try:
                with open(image_path, "rb") as image_file:
                    return base64.b64encode(image_file.read()).decode("utf-8")
            except Exception as e:
                print(f"Error encoding image {image_path}: {e}")
                return ""

        mxfile = ET.Element("mxfile")
        diagram = ET.SubElement(mxfile, "diagram", name="UML Class Diagram")
        mxGraphModel = ET.SubElement(diagram, "mxGraphModel")
        root = ET.SubElement(mxGraphModel, "root")

        # Add a default layer
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")

        # Create a mapping of class IDs to their corresponding XML elements
        class_id_map = {}
        edge_counter = 1  # Ensure unique edge IDs

        for uml_class in self.uml_classes:
            x, y = uml_class.position
            width, height = uml_class.size
            image_data = encode_image(uml_class.svg_path)

            if image_data:
                img_src = f"data:image/svg+xml;base64,{image_data}"
                class_node = ET.SubElement(root, "mxCell", 
                    id=str(uml_class.class_id),
                    value=f"<img width=\"{width}\" height=\"{height}\" src=\"{img_src}\">",
                    style="rounded=0;whiteSpace=wrap;html=1;",
                    vertex="1",
                    parent="1")

                ET.SubElement(class_node, "mxGeometry", x=str(x), y=str(y), width=str(width), height=str(height), **{"as": "geometry"})
                class_id_map[uml_class.class_id] = str(uml_class.class_id)


        for relationship in self.relationships:
            source_id = class_id_map.get(relationship.source)
            destination_id = class_id_map.get(relationship.destination)
            label = relationship.label if relationship.label else ""

            if source_id and destination_id:
                style = "edgeStyle=elbowEdgeStyle;rounded=1;"
                if relationship.type == "extension":
                    style += "endArrow=block;"
                if relationship.type == "inheritance":
                    style += "endArrow=block;"
                elif relationship.type == "association":
                    style += "endArrow=open;"
                elif relationship.type == "dependency":
                    style += "dashed=1;endArrow=open;"
                elif relationship.type == "aggregation":
                    style += "endArrow=diamond;"
                elif relationship.type == "composition":
                    style += "endArrow=diamond;fillColor=black;"
                
                edge = ET.SubElement(root, "mxCell", 
                    id=f"edge_{edge_counter}",  # Ensure unique ID
                    value=label,
                    style=style,
                    edge="1",
                    parent="1",
                    source=str(source_id),
                    target=str(destination_id))
                
                ET.SubElement(edge, "mxGeometry", relative="1", **{"as": "geometry"})
                
                edge_counter += 1  # Increment for next edge

        # Convert XML tree to a string
        tree = ET.ElementTree(mxfile)
        tree.write(output_path, encoding="utf-8", xml_declaration=True)

        print(f"Class diagram exported as {output_path}")


    def update_positions_from_drawio(self, drawio_path, positions_data):
        """
        Reads the class positions from the Draw.io file and updates positions_data.
        """
        try:
            tree = ET.parse(drawio_path)
            root = tree.getroot()
            
            # Extract the mxGraphModel root
            diagram = root.find("diagram")
            if diagram is None:
                print("Invalid Draw.io file: No diagram element found.")
                return
            
            mxGraphModel = diagram.find("mxGraphModel")
            if mxGraphModel is None:
                print("Invalid Draw.io file: No mxGraphModel element found.")
                return
            
            mx_cells = mxGraphModel.findall(".//mxCell")
            id_to_position = {}
            
            # Parse positions
            for cell in mx_cells:
                geometry = cell.find("mxGeometry")
                if geometry is not None and cell.get("vertex") == "1":
                    class_id = cell.get("id")
                    x = float(geometry.get("x", 0))
                    y = float(geometry.get("y", 0))
                    id_to_position[class_id] = (x, y)
            
            def find_by_id(uml_classes, class_id):
                for uml_class in uml_classes:
                    if uml_class.class_id == class_id:
                        return uml_class
                return None  # Return None if not found

            # Update positions_data
            for class_data in positions_data['classes']:
                class_id = str(class_data['id'])
                uml_class = find_by_id(self.uml_classes, class_id)
                uml_class.position = id_to_position[class_id]
            
            print("Positions updated successfully from Draw.io file.")
        except Exception as e:
            print(f"Error reading Draw.io file: {e}")
