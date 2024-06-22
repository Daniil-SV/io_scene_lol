import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       CollectionProperty)

import os
import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from pathlib import Path
from ...resources.skeleton import SkeletonAsset
from ...resources.skinned_mesh import SkinnedMeshAsset
from ..mesh.mesh_utility import MeshUtility

from ...logger import Logger

class LolSceneSkinnedImportSettings:
    def __init__(self) -> None:
        self.skeleton_filepath: str = None
        self.skin_filepath: str = None

class LolSceneSkinnedImport:
    def __init__(self, config: LolSceneSkinnedImportSettings) -> None:
        self.name = Path(config.skin_filepath).stem
        self.asset = SkinnedMeshAsset()
        self.asset.read(config.skin_filepath)
        self.skeleton: SkeletonAsset  = None
        
        if config.skeleton_filepath is not None:
            self.skeleton = SkeletonAsset()
            self.skeleton.read(config.skeleton_filepath)

    def import_scene(self, context: bpy.types.Context) -> None:
        vertices = self.asset.vertices
        indices = self.asset.indices
        primitive = MeshUtility.create_primitive(
            f"{self.name}-mesh", 
            indices,
            vertices,
            texcoord=self.asset.texcoord
        )
        
        obj = bpy.data.objects.new(self.name, primitive)
        
        
        context.scene.collection.objects.link(obj)