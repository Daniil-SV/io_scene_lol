import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       CollectionProperty)

import os
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from pathlib import Path
from ...resources.skeleton import SkeletonAsset
from ...resources.skinned_mesh import SkinnedMeshAsset

from ...logger import Logger

class SkinnedMeshImporter(Operator, ImportHelper):
    bl_idname = "import_scene.lol_skinned_mesh"
    bl_label = "LoL Skinned Mesh"
    bl_description = "Import skinned mesh file to current scene"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = '.skn'
    filter_glob: StringProperty(default=f'*.skn;*.skl', options={ 'HIDDEN' })
    
    import_skeleton: BoolProperty(
        name="Import Skeleton",
        description="Imports skeleton along with mesh, otherwise only mesh will be imported.",
        default=True
    )
    
    custom_skeleton: BoolProperty(
        name="Custom Skeleton",
        description="Uses selected .skl file as a skeleton file if active, otherwise it will use a .skl with same name as .skn",
        default=False
    )
    
    files: CollectionProperty(
        type=bpy.types.OperatorFileListElement,
        options={'HIDDEN', 'SKIP_SAVE'},
    )
    
    def execute(self, context: bpy.types.Context):
        Logger.execute(__name__)
        self.import_skinned_mesh()
        Logger.final()
        return { 'FINISHED' }
    
    def import_skinned_mesh(self) -> None:
        dirname = os.path.dirname(self.filepath)
        mesh_filepath = [
            os.path.join(dirname, str(file.name))
            for file in self.files 
            if str(file.name).endswith(".skn")
        ][0]
        
        mesh = SkinnedMeshAsset()
        mesh.read(mesh_filepath)
        
        skeleton: SkeletonAsset = SkeletonAsset() if self.import_skeleton else None
        if self.import_skeleton:
            skeleton_filepath = ""
            
            if self.custom_skeleton:
                if skeleton_assets := [
                    os.path.join(dirname, str(file.name))
                    for file in self.files
                    if str(file.name).endswith(".skl")
                ]:
                    skeleton_filepath = skeleton_assets[0]
                else:
                    raise ValueError("Custom skeleton file is not selected!")
            else:
                skeleton_filepath = Path(mesh_filepath).with_suffix(".skl")

            if (not os.path.exists(skeleton_filepath)):
                raise FileNotFoundError(f"Failed to find .skl file. Trying by path \"{skeleton_filepath}\"")
                
            skeleton.read(skeleton_filepath)

        self.import_asset(skeleton, mesh)
    
    def import_asset(self, skeleton: SkeletonAsset, mesh: SkinnedMeshAsset) -> None:
        pass