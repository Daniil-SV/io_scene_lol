import bpy
import os

from bpy.props import (StringProperty,
                       BoolProperty,
                       CollectionProperty)

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from pathlib import Path

from ...logger import Logger
from ...blender.skinned_mesh.importer import LolSceneSkinnedImport, LolSceneSkinnedImportSettings

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
    
    split_materials: BoolProperty(
        name="Split Materials",
        description="Imports each material of asset into seperate object",
        default=False
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
        
        config = LolSceneSkinnedImportSettings()
        config.split_materials = self.split_materials
        dirname = os.path.dirname(self.filepath)
        config.skin_filepath = [
            os.path.join(dirname, str(file.name))
            for file in self.files 
            if str(file.name).endswith(".skn")
        ][0]

        if self.import_skeleton:
            if self.custom_skeleton:
                if skeleton_assets := [
                    os.path.join(dirname, str(file.name))
                    for file in self.files
                    if str(file.name).endswith(".skl")
                ]:
                    config.skeleton_filepath = skeleton_assets[0]
                else:
                    raise ValueError("Custom skeleton file is not selected!")
            else:
                config.skeleton_filepath = Path(config.skin_filepath).with_suffix(".skl")

            if (not os.path.exists(config.skeleton_filepath)):
                raise FileNotFoundError(f"Failed to find .skl file. Trying by path \"{config.skeleton_filepath}\"")

        importer = LolSceneSkinnedImport(config)
        importer.import_scene(context)
        
        Logger.final()
        return { 'FINISHED' }