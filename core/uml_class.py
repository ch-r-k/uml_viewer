#uml_class.py
from typing import List, Tuple

class UmlClass:
    def __init__(self, 
                 class_id: int, 
                 name: str, 
                 methods: List[str], 
                 is_abstract: bool, 
                 position: Tuple[float, float], 
                 size: Tuple[float, float], 
                 svg_data,
                 png_data):
        
        self.class_id = class_id
        self.name = name
        self.methods = methods
        self.is_abstract = is_abstract
        self.position = position
        self.size = size
        self.svg_data = svg_data
        self.png_data = png_data
