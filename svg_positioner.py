from lxml import etree
import os
import json

class SvgPositioner:
    def __init__(self, positions_file='positions.json', output_file='main.svg', class_folder='class_diagrams'):
        self.positions_file = positions_file
        self.output_file = output_file
        self.class_folder = class_folder
        self.classes_positions = self._load_positions()

    def _load_positions(self):
        """Load class positions from the JSON file."""
        with open(self.positions_file, 'r') as f:
            data = json.load(f)
        return {item['id']: (item['x'], item['y']) for item in data['classes']}

    def _get_svg_path(self, class_id):
        """Return the path to the SVG file based on the class ID."""
        return os.path.join(self.class_folder, f'{class_id}.svg')

    def _apply_translation(self, svg_root, x, y):
        """Apply translation to the SVG root element."""
        transform = svg_root.get('transform', '')

        # Apply translation, if there's an existing transform, append to it.
        if transform:
            new_transform = f"{transform} translate({x}, {y})"
        else:
            new_transform = f"translate({x}, {y})"
        
        svg_root.set('transform', new_transform)

    def _add_svg_to_main(self, main_svg, class_svg, x, y):
        """Add the class SVG to the main SVG at the specified position (x, y)."""
        class_tree = etree.parse(class_svg)
        class_root = class_tree.getroot()

        # Apply translation to the root of the class SVG
        self._apply_translation(class_root, x, y)

        # Append the class SVG to the main SVG
        main_root = main_svg.getroot()
        for element in class_root:
            main_root.append(element)

        # Track the bounds for setting the size of the main SVG later
        return class_root

    def _get_svg_dimensions(self, class_svg):
        """Get the dimensions (width, height) of an SVG file."""
        tree = etree.parse(class_svg)
        root = tree.getroot()

        # Use the 'viewBox' or 'width'/'height' attributes to calculate the size.
        width = float(root.get('width', '0').replace('px', '').replace('em', ''))
        height = float(root.get('height', '0').replace('px', '').replace('em', ''))

        # If viewBox is set, calculate the size from it.
        viewBox = root.get('viewBox')
        if viewBox:
            _, _, vb_width, vb_height = map(float, viewBox.split())
            width = max(width, vb_width)
            height = max(height, vb_height)

        return width, height

    def create_main_svg(self):
        """Create the main SVG file by placing individual class SVGs at the specified positions."""
        # Create an empty main SVG with a root element
        main_svg = etree.Element('svg', xmlns="http://www.w3.org/2000/svg")

        # Wrap the main SVG in an ElementTree
        main_svg_tree = etree.ElementTree(main_svg)

        # Variables to track the bounds of the main SVG
        max_x = 0
        max_y = 0

        # Iterate over each class and position its SVG on the main SVG
        for class_id, (x, y) in self.classes_positions.items():
            class_svg_path = self._get_svg_path(class_id)
            if os.path.exists(class_svg_path):
                # Add the class SVG and calculate its dimensions
                class_root = self._add_svg_to_main(main_svg_tree, class_svg_path, x, y)
                
                # Get the dimensions of the current class SVG
                class_width, class_height = self._get_svg_dimensions(class_svg_path)

                # Update the maximum x and y for the main SVG size
                max_x = max(max_x, x + class_width)
                max_y = max(max_y, y + class_height)
            else:
                print(f"Warning: SVG file for class {class_id} not found. Skipping.")

        # Set the size of the main SVG to fit all the class SVGs
        main_svg.set('width', str(max_x))
        main_svg.set('height', str(max_y))

        # Save the main SVG to the specified output file
        main_svg_tree.write(self.output_file)
        print(f"Main SVG saved as {self.output_file}")
