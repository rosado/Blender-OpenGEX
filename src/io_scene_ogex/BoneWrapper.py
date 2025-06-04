import bpy

from .BaseWrapper import BaseWrapper

from .ExporterState import *

__author__ = 'Eric Lengyel, Jonathan Hale, Nicolas Wehrle'


class BoneWrapper(BaseWrapper):

    def __init__(self, bone, container, parent=None, offset=None, armature: bpy.types.Armature | None = None):
        """Pass the armature only if the bone is a root bone"""
        super().__init__(bone, container, parent, offset)
        assert (armature is None) or (armature and bone.parent == None)

        self.process_bone(bone, armature=armature)

        if len(bone.children) != 0:
            self.create_children(bone.children)

    def process_bone(self, bone, armature=None):
        if self.container.exportAll or bone.select:
            self.nodeRef["nodeType"] = NodeType.bone
            self.nodeRef["structName"] = bytes("node" + str(len(self.container.nodes)), "UTF-8")
            if armature:
                self.nodeRef["armature"] = armature
                armatures = self.container.armatures.get(armature.name)
                if not armatures:
                    armatures = []
                    self.container.armatures[armature.name] = armatures
                armatures.append(self)

    def create_children(self, children, offset=None):
        for bone in children:
            self.children.append(BoneWrapper(bone, self.container, self, offset))
