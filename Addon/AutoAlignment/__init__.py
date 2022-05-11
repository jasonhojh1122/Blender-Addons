# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "AutoAlignment",
    "author" : "Deith Zireael",
    "description" : "Aligns objects with a given axis.",
    "blender" : (3, 1, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Object"
}

import bpy
from bpy.props import *
from functools import cmp_to_key

class AutoAlignment(bpy.types.Operator):
    bl_idname = "object.auto_alignment"
    bl_label = "Align objects"
    bl_options = {'REGISTER', 'UNDO'}

    align_axis: EnumProperty(
        name        = "Alignment axis",
        description = "Fixed axis to align objects along with",
        items       = {
                        ('X', 'X', 'X axis', 'EMPTY_AXIS', 0),
                        ('Y', 'Y', 'Y axis', 'EMPTY_AXIS', 1),
                        ('Z', 'Z', 'Z axis', 'EMPTY_AXIS', 2) },
        default     = 'Z'
    )
    dist: BoolProperty(
        name        = "Distribute",
        description = "To enable distribute or not",
        default     = True
    )
    dist_axis: EnumProperty(
        name        = "Distribute axis",
        description = "Fixed axis to distribute objects along with",
        items       = {
                        ('X', 'X', 'X axis', 'EMPTY_AXIS', 0),
                        ('Y', 'Y', 'Y axis', 'EMPTY_AXIS', 1),
                        ('Z', 'Z', 'Z axis', 'EMPTY_AXIS', 2) },
        default     = 'Z'
    )

    def execute(self, context: bpy.context):
        self.align(context.selected_objects)
        if self.dist:
            self.distribute(context.selected_objects)
        return {'FINISHED'}

    def align(self, objs):
        axis = self.axis_id(self.align_axis)

        for obj in objs:
            for i in range(1, 3):
                id = (axis + i) % 3
                obj.location[id] = bpy.context.active_object.location[id]

    def distribute(self, objs):
        axis = self.axis_id(self.dist_axis)
        sorted_objs = self.sort(objs, axis)
        step = ( sorted_objs[len(objs)-1].location[axis] - sorted_objs[0].location[axis] ) / (len(objs) - 1)
        curLocation = sorted_objs[0].location[axis]

        obj: bpy.types.Object
        for obj in sorted_objs:
            obj.location[axis] = curLocation
            curLocation += step

    def sort(self, objs: list[bpy.types.Object], axis: int) -> list[bpy.types.Object]:
        def compare(item1: bpy.types.Object, item2: bpy.types.Object):
            match axis:
                case 0:
                    return item1.location.x - item2.location.x
                case 1:
                    return item1.location.y - item2.location.y
                case 2:
                    return item1.location.z - item2.location.z

        return sorted(objs, key=cmp_to_key(compare))

    def axis_id(self, axis) -> int:
        match axis:
            case 'X':
                return 0
            case 'Y':
                return 1
            case 'Z':
                return 2
        return


def menu_func(self, context):
    self.layout.operator(AutoAlignment.bl_idname)

addon_keymaps = []

def register():
    bpy.utils.register_class(AutoAlignment)
    bpy.types.VIEW3D_MT_add.append(menu_func)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

    kmi = km.keymap_items.new(AutoAlignment.bl_idname, 'A', 'PRESS', ctrl=True, shift=True)

    addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(AutoAlignment)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()