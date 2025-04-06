#uml_relationship.py
class UmlRelationship:
    def __init__(self, source, destination, relationship_type, access, label=None):
        self.source = source
        self.destination = destination
        self.type = relationship_type
        self.access = access
        self.label = label

    def __repr__(self):
        return f"UmlRelationship({self.source} -> {self.destination}, {self.type}, {self.access}, {self.label})"