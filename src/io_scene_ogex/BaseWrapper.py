__author__ = 'Eric Lengyel, Jonathan Hale, Nicolas Wehrle'


from .ExporterState import ExporterState


class BaseWrapper:

    def __init__(self, item, container: ExporterState, parent, offset):
        self.parent = parent
        self.children = []
        self.item = item
        self.container = container
        self.offset = offset
        self.nodeRef = {}

        self.container.nodes.append(self)


