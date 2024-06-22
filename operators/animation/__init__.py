import bpy

from bpy.props import (StringProperty,
                       IntProperty)

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper

from ...blender.animation.exporter import LolSceneAnimationExporter, LolSceneAnimationExportSettings
from ...logger import Logger

class AnimationImporter(Operator, ImportHelper):
    bl_idname = "import_scene.lol_animation"
    bl_label = "Import LoL Animation"
    bl_description = "Import animation from file to selected skeleton"
    bl_options = { 'REGISTER', 'UNDO' }

    filename_ext = '.anm'

    filter_glob: StringProperty(default=f'*{filename_ext}', options={ 'HIDDEN' })

    def __init__(self) -> None:
        super().__init__()

    def execute(self, context: bpy.types.Context):
        Logger.execute(__name__)
        #self.import_animation(context)
        Logger.final()

        return { 'FINISHED' }
    
    
class AnimationExporter(Operator, ExportHelper):
    bl_idname = "export_scene.lol_animation"
    bl_label = "LoL Animation"
    bl_description = "Export animation from selected skeleton to .ANM file"
    bl_options = { 'PRESET' }

    filename_ext = '.anm'

    filter_glob: StringProperty(default=f'*{filename_ext}', options={ 'HIDDEN' })

    #compress: BoolProperty(
    #    name='Compress animation asset',
    #    description='',
    #    default=True
    #)

    #quantize: BoolProperty(
    #    name='Quantize Rotation',
    #    description='',
    #    default=True
    #)
    
    transform_tolerance: IntProperty(
        name="Transform Tolerance", 
        description="Tolerence of Scale and Translation", 
        default=70,
        min=0,
        max=100,
        subtype="FACTOR"
    )
    
    rotation_tolerance: IntProperty(
        name="Rotation Tolerance", 
        description="Tolerance of Rotation", 
        default=60,
        min=0,
        max=100,
        subtype="FACTOR"
    )

    def __init__(self) -> None:
        pass

    def execute(self, context: bpy.types.Context):
        Logger.execute(__name__)
        
        objects = context.selected_objects
        if (len(objects) == 0):
            self.report({'ERROR'}, "Select any skeleton object before exporting")
            return

        object: bpy.types.Object = objects[0]
        if (object.type != "ARMATURE"):
            self.report({'ERROR'}, "Selected object is not armature") 
            return
        
        config = LolSceneAnimationExportSettings()
        config.output_path = self.filepath
        config.compressed = False
        config.rotation_tolerance = self.rotation_tolerance
        config.transform_tolerance = self.transform_tolerance
        
        exporter = LolSceneAnimationExporter(context, object, config)
        exporter.export(context)
        
        Logger.info("Done")
        Logger.final()
        
        self.report({"INFO"}, "Done")
        return{ 'FINISHED' }