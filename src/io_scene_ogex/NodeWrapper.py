import bpy
from .BaseWrapper import BaseWrapper
from .BoneWrapper import BoneWrapper
from .ExporterState import *


__author__ = 'Eric Lengyel, Jonathan Hale, Nicolas Wehrle'


class NodeWrapper(BaseWrapper):

    def __init__(self, node, container: ExporterState, parent=None, offset=None):
        super().__init__(node, container, parent, offset)

        self.bones = []

        self.process_node()

        if len(node.children) != 0:
            for obj in node.children:
                self.children.append(NodeWrapper(obj, self.container, self, None))


    def process_node(self):
        if self.container.exportAll or self.item.select_get():
            self.nodeRef["nodeType"] = self.get_node_type()
            self.nodeRef["structName"] = B"node" + bytes(str(len(self.container.nodes)), "UTF-8")

            if self.item.parent_type == "BONE":
                bone_subnode_array = self.container.boneParentArray.get(self.item.parent_bone)
                if bone_subnode_array:
                    bone_subnode_array.append(self)
                else:
                    self.container.boneParentArray[self.item.parent_bone] = [self]

            # all bones belonging to the armature are stored in the `bones` property of an armature.
            # We only want those bones whose `parent` is not set (meaning: they're not attached 
            # to other bones)
            if self.item.type == "ARMATURE":
                skeleton: bpy.types.Armature = self.item.data
                if skeleton:
                    for bone in skeleton.bones:
                        if not bone.parent:
                            # FIXME register somehow
                            self.bones.append(BoneWrapper(bone, self.container))

    def get_node_type(self):
        if self.item.type == "MESH":
            if len(self.item.data.vertices) != 0:
                return NodeType.geometry
        elif self.item.type == "LAMP":
            lamp_type = self.item.data.type
            if (lamp_type == "SUN") or (lamp_type == "POINT") or (lamp_type == "SPOT"):
                return NodeType.light
        elif self.item.type == "CAMERA":
            return NodeType.camera

        return NodeType.node
