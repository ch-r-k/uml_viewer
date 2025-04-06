# interfaces.py
from abc import ABC, abstractmethod
from typing import Tuple
from core.uml_class import UmlClass
from core.uml_relationshpi import UmlRelationship

class UmlImporter(ABC):
    @abstractmethod
    def import_classes_and_relationships(self, input_path:str):
        pass
    @abstractmethod
    def import_posittions(self, input_path:str):
        pass

class UmlExporter(ABC):
    @abstractmethod
    def export(self, classes: list[UmlClass], relationships: list[UmlRelationship], output_path:str):
        pass

class PositionUpdater(ABC):
    @abstractmethod
    def opem(self, classes:UmlClass, relationships:UmlRelationship, class_possitions: Tuple[float, float]):
        pass

    @abstractmethod
    def update_positions(self):
        pass

class ClassImageGenerator(ABC):
    @abstractmethod
    def generate_png(self, uml_class: UmlClass):
        pass

    @abstractmethod
    def generate_svg(self, uml_class: UmlClass):
        pass