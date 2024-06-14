import bpy

from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       CollectionProperty)

from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, axis_conversion

from ..logger import Logger
from ..reader import BinaryReader

class Animation_Importer(Operator, ImportHelper):
    bl_idname = "import_scene.lol"
    bl_label = "Import LoL Animation"
    bl_description = "Import animation from file to selected skeleton"
    bl_options = { 'REGISTER', 'UNDO' }

    filename_ext = '.anm'

    filter_glob: StringProperty(default=f'*{filename_ext}', options={ 'HIDDEN' })

    def __init__(self) -> None:
        self.logger = Logger(__name__)
        super().__init__()

    def execute(self, context: bpy.types.Context):
        self.logger.execute()
        self.import_animation(context)
        self.logger.final()

        return { 'FINISHED' }
    
    def import_animation(self, context: bpy.types.Context):
        self.logger.info(f"Importing {self.filepath}")

        objects = context.selected_objects
        if (len(objects) == 0):
            self.report({'ERROR'}, "Select any skeleton object before exporting")
            return

        object: bpy.types.Object = objects[0]
        if (object.type != "ARMATURE"):
            self.report({'ERROR'}, "Selected object is not armature") 
            return
        
        file = open(self.filepath, "wb")
        buffer = BinaryReader(file.read())
        file.close()

        

        
