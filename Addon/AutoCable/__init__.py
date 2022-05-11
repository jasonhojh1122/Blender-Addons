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
    "name" : "AutoCable",
    "author" : "Deith Zireael",
    "description" : "Automatically generates a cable between two faces.",
    "blender" : (3, 1, 0),
    "version" : (0, 0, 1),
    "location" : "",
    "warning" : "",
    "category" : "Add Curve"
}

import bpy
import bmesh
from bpy.props import IntProperty, FloatProperty
from mathutils import Matrix

class AutoCable(bpy.types.Operator):
    bl_idname = "object.auto_cable"
    bl_label = "Auto cable"
    bl_options = {'REGISTER', 'UNDO'}

    res_u: IntProperty(
        name        = "Resolution U",
        description = "Resolution U",
        default     = 8,
        min         = 0,
        max         = 128
    )
    bevel_depth: FloatProperty(
        name        = "Cable radius",
        description = "Bevel depth",
        default     = 0.1,
        min         = 0.0,
        max         = 128.0
    )
    bevel_res: IntProperty(
        name        = "Bevel Resolution",
        description = "Bevel resolution",
        default     = 2,
        min         = 0,
        max         = 16
    )
    midpoint_distance: FloatProperty(
        name        = "Length",
        description = "Cable mid point multiplier",
        default     = 1,
        min         = 0.0,
        max         = 64.0
    )

    def execute(self, context: bpy.context):
        bpy.ops.object.mode_set(mode='EDIT')

        centers, normals = self.add_bezier_points(context)

        if len(centers) != 2:
            return {'CANCELLED'}

        self.add_curve('Cable', centers, normals, context)
        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}

    def add_bezier_points(self, context: bpy.context):
        centers = []
        normals = []

        obj: bpy.types.Object
        for obj in context.selected_objects:
            if (obj.type != 'MESH'):
                continue
            bm = bmesh.from_edit_mesh(obj.data)
            f: bmesh.types.BMFace
            for f in bm.faces:
                if not f.select:
                    continue
                center_local = f.calc_center_median()
                center_global = obj.matrix_world @ center_local
                normal_local_pivot = center_local + f.normal
                normal_global_pivot = obj.matrix_world @ normal_local_pivot
                centers.append(center_global)
                normals.append(normal_global_pivot - center_global)

        return centers, normals

    def add_curve(self, curve_name: str, verts, normal, context: bpy.context):
        cur_data = bpy.data.curves.new(curve_name, 'CURVE')
        cur_data.dimensions = '3D'
        spline = cur_data.splines.new('BEZIER')
        curve = bpy.data.objects.new(curve_name, cur_data)

        spline.radius_interpolation = 'BSPLINE'
        spline.tilt_interpolation = 'BSPLINE'

        spline.bezier_points.add(2)

        for i in range(3):
            spline.bezier_points[i].handle_right_type = 'ALIGNED'
            spline.bezier_points[i].handle_left_type = 'ALIGNED'
            spline.bezier_points[i].radius = 1.0
            spline.bezier_points[i].tilt = 0.0

        # starting point
        spline.bezier_points[0].co = verts[0]
        spline.bezier_points[0].handle_right = verts[0] + normal[0]
        spline.bezier_points[0].handle_left = verts[0] - normal[0]

        # middle point
        spline.bezier_points[1].co = \
            ( (verts[0] + self.midpoint_distance*normal[0]) + (verts[1] + self.midpoint_distance*normal[1])) / 2
        spline.bezier_points[1].handle_right_type = 'AUTO'
        spline.bezier_points[1].handle_left_type = 'AUTO'

        # ending point
        spline.bezier_points[2].co = verts[1]
        spline.bezier_points[2].handle_right = verts[1] - normal[1]
        spline.bezier_points[2].handle_left = verts[1] + normal[1]

        cur_data.resolution_u = self.res_u
        cur_data.bevel_depth = self.bevel_depth
        cur_data.bevel_resolution = self.bevel_res
        curve.data.transform(Matrix.Translation(-verts[0]))
        curve.matrix_world.translation += verts[0]

        context.scene.collection.objects.link(curve)

def menu_func(self, context):
    self.layout.operator(AutoCable.bl_idname)

addon_keymaps = []

def register():
    bpy.utils.register_class(AutoCable)
    bpy.types.VIEW3D_MT_add.append(menu_func)

    wm = bpy.context.window_manager
    km = wm.keyconfigs.addon.keymaps.new(name='Object Mode', space_type='EMPTY')

    kmi = km.keymap_items.new(AutoCable.bl_idname, 'T', 'PRESS', ctrl=True, shift=True)

    addon_keymaps.append((km, kmi))


def unregister():
    bpy.utils.unregister_class(AutoCable)

    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()


if __name__ == "__main__":
    register()