bl_info = {
    "name": "ScreenSnap Turntable",
    "author": "designersoup + modified by plu5",
    "version": (1, 0, 0),
    "blender": (2, 93, 0),
    "location": "3D Viewport > N-panel > ScreenSnap",
    "description": "Viewport screenshots every N actions with a fixed camera, stealth capture, optional turntable, and sensible overlay controls.",
    "category": "3D View",
    "doc_url": "www.youtube.com/@designersoup",
    "tracker_url": "www.youtube.com/@designersoup",
}

import bpy, bmesh, os
from math import radians
from mathutils import Vector, Matrix
from bpy.props import StringProperty, IntProperty, BoolProperty, PointerProperty, EnumProperty, FloatProperty
import subprocess

PANEL_CATEGORY = "ScreenSnap"
CAPTURE_PREFIX = "blender_"
CAPTURE_EXT = ".png"

_pending_timer = None
_internal_change = False
_last_geom_sig = None

def _default_output_dir():
    try:
        if bpy.data.filepath:
            return os.path.join(os.path.dirname(bpy.data.filepath), "screensnap")
    except Exception:
        pass
    base = bpy.app.tempdir if getattr(bpy.app, "tempdir", None) else os.path.expanduser("~")
    return os.path.join(base, "screensnap")

def ensure_dir(path):
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        pass

def find_view3d_context():
    for window in bpy.context.window_manager.windows:
        screen = window.screen
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                for region in area.regions:
                    if region.type == 'WINDOW':
                        space = area.spaces.active
                        return window, screen, area, region, space
    return None, None, None, None, None

def _camera_pointer_poll(self, obj): return bool(obj and obj.type == 'CAMERA')

def _effective_dir(prefs): return bpy.path.abspath(prefs.output_dir) if prefs.output_dir else _default_output_dir()

def _camera_projection_of(space, cam_obj):
    if cam_obj and cam_obj.type == 'CAMERA':
        return 'ORTHO' if getattr(cam_obj.data, "type", 'PERSP') == 'ORTHO' else 'PERSP'
    r3d = space.region_3d
    return 'ORTHO' if r3d.view_perspective == 'ORTHO' else 'PERSP'

def _collect_layer_collections(root_lc, col, out, recursive=True):
    if root_lc.collection == col:
        out.append(root_lc)
    for child in root_lc.children:
        if recursive: _collect_layer_collections(child, col, out, recursive)

def _empty_image_visibility_flags(obj):
    if obj.type != 'EMPTY' or getattr(obj, "empty_display_type", None) != 'IMAGE': return True, True
    a1, b1 = "show_empty_image_perspective", "show_empty_image_orthographic"
    a2, b2 = "show_in_perspective", "show_in_orthographic"
    for a, b in ((a1, b1), (a2, b2)):
        sp, so = getattr(obj, a, None), getattr(obj, b, None)
        if sp is not None and so is not None: return bool(sp), bool(so)
    return True, True

def _geom_signature(context):
    v = e = f = 0
    for ob in context.scene.objects:
        if ob.type == 'MESH' and ob.data:
            me = ob.data
            v += len(me.vertices); e += len(me.edges); f += len(me.polygons)
    return (v, e, f)

class SSPreferences(bpy.types.PropertyGroup):
    enabled: BoolProperty(name="Enabled", default=False)
    counter: IntProperty(name="Counter", default=0, min=0)

    batch: IntProperty(name="Every N actions", default=5, min=1, soft_max=50)
    output_dir: StringProperty(name="Save Folder", default="", subtype='DIR_PATH')

    action_mode: EnumProperty(
        name="Actions mode",
        items=(('SMART',"SMART (filter nav)",""),('STRICT',"STRICT (keys+edits)","")),
        default='STRICT'
    )
    count_left:   BoolProperty(name="Left Click",   default=False)
    count_right:  BoolProperty(name="Right Click",  default=False)
    count_middle: BoolProperty(name="Middle Click", default=False)
    count_enter:  BoolProperty(name="Enter/Return", default=True)
    count_space:  BoolProperty(name="Space",        default=False)
    extra_keys: StringProperty(name="Also count keys", default="E,G,R,S")
    ignore_navigation_inputs: BoolProperty(name="Ignore navigation inputs", default=True)
    count_mesh_edits: BoolProperty(name="Count mesh edits", default=True)

    capture_method: EnumProperty(
        name="Capture Method",
        items=(('VIEWPORT',"Viewport (fast)",""),('CAMERA_RENDER',"Camera render","")),
        default='VIEWPORT'
    )
    use_fixed_camera: BoolProperty(name="Use Fixed Camera (stealth)", default=True)
    fixed_camera: PointerProperty(name="Camera", type=bpy.types.Object, poll=_camera_pointer_poll)
    debounce_seconds: FloatProperty(name="Debounce (s)", default=0.25, min=0.0, soft_max=1.0)

    overlay_mode: EnumProperty(
        name="Overlay Mode",
        items=(('NONE',"Keep overlays",""),('EXTRAS',"Hide Extras only",""),('ALL',"Hide All overlays","")),
        default='NONE'
    )
    hide_grid_axes: BoolProperty(name="Hide Grid & Axes (capture only)", default=True)
    force_opaque_materials: BoolProperty(name="Force Opaque Materials", default=True)
    capture_shading: EnumProperty(
        name="Shading for Viewport Capture",
        items=(('KEEP',"Keep current",""),('WIREFRAME',"Wireframe",""),('SOLID',"Solid",""),
               ('MATERIAL',"Material",""),('RENDERED',"Rendered","")), default='KEEP'
    )

    use_turntable: BoolProperty(name="Turntable (rotate camera)", default=False)
    turntable_target: PointerProperty(name="Target", type=bpy.types.Object)
    turntable_degrees: FloatProperty(name="Degrees per Shot", default=10.0, soft_min=-360.0, soft_max=360.0)
    turntable_axis: EnumProperty(name="Axis", items=(('X','X',''),('Y','Y',''),('Z','Z','')), default='Z')

    hide_blueprints_by_mode: BoolProperty(name="Auto-hide Image Blueprints by camera mode", default=True)
    hide_collection: PointerProperty(name="Hide Collection (during capture)", type=bpy.types.Collection)
    hide_collection_recursive: BoolProperty(name="Recursive", default=True)

    reveal_hidden_edit: BoolProperty(name="Reveal hidden Edit-Mode elements", default=True)

    stop_on_key: BoolProperty(name="Enable stop hotkey", default=True)
    stop_key: EnumProperty(name="Stop key", items=tuple((f"F{i}", f"F{i}", "") for i in range(1,13)), default='F10')
    stop_use_ctrl:  BoolProperty(name="Ctrl",  default=True)
    stop_use_shift: BoolProperty(name="Shift", default=True)
    stop_use_alt:   BoolProperty(name="Alt",   default=False)

    debug_log: BoolProperty(name="Debug log", default=False)
    last_message: StringProperty(name="Last", default="")
    index: IntProperty(name="Image Index", default=1, min=1)

def _stop_combo_pressed(prefs, event):
    if not prefs.stop_on_key or event.type != prefs.stop_key or event.value != 'PRESS': return False
    if prefs.stop_use_ctrl  and not event.ctrl:  return False
    if prefs.stop_use_shift and not event.shift: return False
    if prefs.stop_use_alt   and not event.alt:   return False
    return True

def _is_navigation_event(prefs, event):
    if not prefs.ignore_navigation_inputs: return False
    nav_mouse = {'MIDDLEMOUSE','WHEELUPMOUSE','WHEELDOWNMOUSE','WHEELINMOUSE','WHEELOUTMOUSE'}
    nav_numpad = {'NUMPAD_1','NUMPAD_2','NUMPAD_3','NUMPAD_4','NUMPAD_5','NUMPAD_6','NUMPAD_7','NUMPAD_8','NUMPAD_9','NUMPAD_PLUS','NUMPAD_MINUS','NUMPAD_PERIOD'}
    nav_misc = {'HOME','END'}
    nav_ndof = {'NDOF_MOTION','NDOF_BUTTON_MENU','NDOF_BUTTON_FIT','NDOF_BUTTON_TOP','NDOF_BUTTON_BOTTOM','NDOF_BUTTON_LEFT','NDOF_BUTTON_RIGHT','NDOF_BUTTON_FRONT','NDOF_BUTTON_BACK','NDOF_BUTTON_ROTATE','NDOF_BUTTON_PAN'}
    t = event.type
    return t in nav_mouse or t in nav_numpad or t in nav_misc or t in nav_ndof

def counts_as_action(prefs, event):
    if event.value != 'PRESS': return False
    if prefs.action_mode == 'STRICT':
        if event.type in {'LEFTMOUSE','RIGHTMOUSE','MIDDLEMOUSE'}: return False
        if prefs.count_enter and event.type in {'RET','NUMPAD_ENTER','ENTER'}: return True
        if prefs.count_space and event.type == 'SPACE': return True
        if prefs.extra_keys:
            keys = {k.strip().upper() for k in prefs.extra_keys.split(',') if k.strip()}
            if event.type in keys: return True
        return False
    if _is_navigation_event(prefs, event): return False
    if prefs.count_left   and event.type == 'LEFTMOUSE':   return True
    if prefs.count_right  and event.type == 'RIGHTMOUSE':  return True
    if prefs.count_middle and event.type == 'MIDDLEMOUSE': return True
    if prefs.count_enter  and event.type in {'RET','NUMPAD_ENTER','ENTER'}: return True
    if prefs.count_space  and event.type == 'SPACE': return True
    if prefs.extra_keys:
        keys = {k.strip().upper() for k in prefs.extra_keys.split(',') if k.strip()}
        if event.type in keys: return True
    return False

def _rotate_camera_around_target(cam, target, angle_deg, axis='Z'):
    if not cam or not target: return
    t = target.matrix_world.translation.copy()
    c = cam.matrix_world.translation.copy()
    vec = c - t
    axis_vec = {'X':Vector((1,0,0)),'Y':Vector((0,1,0)),'Z':Vector((0,0,1))}[axis]
    rot = Matrix.Rotation(radians(angle_deg), 4, axis_vec)
    cam.location = t + (rot @ vec)
    d = (t - cam.location)
    if d.length_squared: cam.rotation_euler = d.to_track_quat('-Z','Y').to_euler()

def _snapshot_view_state(space):
    r3d, sh, ov = space.region_3d, space.shading, space.overlay
    return dict(
        view_perspective=r3d.view_perspective,
        view_matrix=r3d.view_matrix.copy(),
        view_location=r3d.view_location.copy(),
        view_rotation=r3d.view_rotation.copy(),
        view_distance=r3d.view_distance,
        lens=getattr(space, "lens", None),
        space_camera=getattr(space, "camera", None),
        shading_type=getattr(sh, "type", 'SOLID'),
        show_xray=getattr(sh, "show_xray", False),
        show_overlays=ov.show_overlays,
        show_extras=getattr(ov, "show_extras", True),
        show_floor=getattr(ov, "show_floor", True),
        show_axis_x=getattr(ov, "show_axis_x", True),
        show_axis_y=getattr(ov, "show_axis_y", True),
        show_axis_z=getattr(ov, "show_axis_z", True),
        show_face_orientation=getattr(ov, "show_face_orientation", False),
    )

def _restore_view_state(space, s):
    r3d, sh, ov = space.region_3d, space.shading, space.overlay
    r3d.view_perspective = s["view_perspective"]
    r3d.view_matrix, r3d.view_location, r3d.view_rotation = s["view_matrix"], s["view_location"], s["view_rotation"]
    r3d.view_distance = s["view_distance"]
    if s["lens"] is not None and hasattr(space, "lens"): space.lens = s["lens"]
    space.camera = s["space_camera"]
    if hasattr(sh, "type"): sh.type = s["shading_type"]
    if hasattr(sh, "show_xray"): sh.show_xray = s["show_xray"]
    ov.show_overlays = s["show_overlays"]
    if hasattr(ov, "show_extras"): ov.show_extras = s["show_extras"]
    if hasattr(ov, "show_floor"):  ov.show_floor  = s["show_floor"]
    if hasattr(ov, "show_axis_x"): ov.show_axis_x = s["show_axis_x"]
    if hasattr(ov, "show_axis_y"): ov.show_axis_y = s["show_axis_y"]
    if hasattr(ov, "show_axis_z"): ov.show_axis_z = s["show_axis_z"]
    if hasattr(ov, "show_face_orientation"): ov.show_face_orientation = s["show_face_orientation"]

def _in_edit_mesh_mode(context):
    try: return context.mode.startswith('EDIT_MESH')
    except Exception: return any(o.mode == 'EDIT' for o in context.objects if o.type == 'MESH')

def _get_edit_mesh_objects(context):
    if not _in_edit_mesh_mode(context): return []
    try: return [o for o in context.objects_in_mode_unique_data if o.type == 'MESH']
    except Exception: return [o for o in context.selected_objects if o.type == 'MESH' and o.mode == 'EDIT']

def _snapshot_and_reveal_hidden_edit_elements(context):
    res = []
    for ob in _get_edit_mesh_objects(context):
        me = ob.data
        try: bm = bmesh.from_edit_mesh(me)
        except Exception: continue
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        hv = [i for i,v in enumerate(bm.verts) if getattr(v,"hide",False)]
        he = [i for i,e in enumerate(bm.edges) if getattr(e,"hide",False)]
        hf = [i for i,f in enumerate(bm.faces) if getattr(f,"hide",False)]
        if hv or he or hf:
            for i in hv: bm.verts[i].hide = False
            for i in he: bm.edges[i].hide = False
            for i in hf: bm.faces[i].hide = False
            bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)
        res.append(dict(obj=ob, hidden_verts=hv, hidden_edges=he, hidden_faces=hf))
    return res

def _restore_hidden_edit_elements(snap):
    for d in snap:
        ob, me = d["obj"], d["obj"].data
        try: bm = bmesh.from_edit_mesh(me)
        except Exception: continue
        bm.verts.ensure_lookup_table(); bm.edges.ensure_lookup_table(); bm.faces.ensure_lookup_table()
        for i in d["hidden_verts"]:
            if i < len(bm.verts): bm.verts[i].hide = True
        for i in d["hidden_edges"]:
            if i < len(bm.edges): bm.edges[i].hide = True
        for i in d["hidden_faces"]:
            if i < len(bm.faces): bm.faces[i].hide = True
        bmesh.update_edit_mesh(me, loop_triangles=False, destructive=False)

def popup(text):
    def draw(self, context):
        self.layout.label(text=text)

    bpy.context.window_manager.popup_menu(
        draw,
        title="ScreenSnap",
        icon='INFO'
    )

def update_preview(f):
    c = subprocess.run([
        'pgrep', 'imv'
    ], capture_output=True).stdout.decode()
    if len(c):
        subprocess.run([
            'imv-msg', c, 'open', f
        ])
        subprocess.run([
            'imv-msg', c, 'goto', '-1'
        ])
    return None  # stop timer

def _capture_viewport(context, prefs, filepath):
    scene = bpy.context.scene
    old_engine = scene.render.engine
    old_samples = scene.cycles.samples
    scene.render.engine = 'BLENDER_WORKBENCH'
    scene.render.use_compositing = False
    scene.render.use_sequencer = False
    oldpath = scene.render.filepath
    f = os.path.join("/home/pm/KritaRecorder/20260517231119/", f"{prefs.index:07d}.png")
    scene.render.filepath = f
    if os.path.exists(f):
        print("[ScreenSnap] ERROR file exists, avoid overwriting. something went wrong")
        popup("ERROR file exists, avoid overwriting. something went wrong")
        return False
    bpy.ops.render.render(write_still=True)
    scene.render.filepath = oldpath
    scene.render.engine = old_engine
    scene.cycles.samples = old_samples
    # bpy.app.timers.register(lambda: update_preview(f), first_interval=1)
    update_preview(f)
    return True

def _do_capture():
    global _pending_timer
    _pending_timer = None
    ctx = bpy.context
    if not ctx or not ctx.window_manager: return None
    prefs = ctx.window_manager.screen_snap_prefs
    if prefs.capture_method != 'VIEWPORT': prefs.capture_method = 'VIEWPORT'

    folder = _effective_dir(prefs); ensure_dir(folder)
    filepath = os.path.join(folder, f"{CAPTURE_PREFIX}{prefs.index:07d}{CAPTURE_EXT}")
    filepath = bpy.path.ensure_ext(filepath, CAPTURE_EXT)

    ok = _capture_viewport(ctx, prefs, filepath)
    if ok:
        prefs.index += 1
        # if prefs.use_fixed_camera and prefs.fixed_camera and prefs.use_turntable and prefs.turntable_target:
        #     _rotate_camera_around_target(prefs.fixed_camera, prefs.turntable_target, prefs.turntable_degrees, prefs.turntable_axis)
        print(f"[ScreenSnap] Saved: {filepath}")
    return None

def schedule_capture(prefs):
    global _pending_timer
    if _pending_timer is not None: return
    delay = max(0.0, float(prefs.debounce_seconds))
    _pending_timer = bpy.app.timers.register(_do_capture, first_interval=delay)

class SSModalWatcher(bpy.types.Operator):
    bl_idname = "wm.ss_modal_watcher"
    bl_label = "ScreenSnap Watcher"
    _timer = None

    def _check_mesh_edits(self, context, prefs):
        global _last_geom_sig
        if _internal_change or not prefs.count_mesh_edits: return
        sig = _geom_signature(context)
        if _last_geom_sig is None: _last_geom_sig = sig; return
        if sig != _last_geom_sig:
            _last_geom_sig = sig
            prefs.counter += 1
            if prefs.debug_log: print(f"[ScreenSnap] Counted mesh edit: sig {sig}")
            if prefs.counter >= prefs.batch:
                prefs.counter = 0; schedule_capture(prefs)

    def modal(self, context, event):
        prefs = context.window_manager.screen_snap_prefs
        if not prefs.enabled:
            self.cancel(context); return {'CANCELLED'}

        if _stop_combo_pressed(prefs, event):
            prefs.enabled = False; self.cancel(context); self.report({'INFO'}, "ScreenSnap stopped (hotkey)."); return {'CANCELLED'}

        if counts_as_action(prefs, event):
            prefs.counter += 1
            if prefs.counter >= prefs.batch:
                prefs.counter = 0; schedule_capture(prefs)

        if event.type == 'TIMER': self._check_mesh_edits(context, prefs)
        return {'PASS_THROUGH'}

    def execute(self, context):
        global _last_geom_sig
        prefs = context.window_manager.screen_snap_prefs
        prefs.counter = 0; _last_geom_sig = _geom_signature(context)
        if self._timer is None: self._timer = context.window_manager.event_timer_add(0.15, window=context.window)
        context.window_manager.modal_handler_add(self); return {'RUNNING_MODAL'}

    def cancel(self, context):
        if self._timer is not None:
            context.window_manager.event_timer_remove(self._timer); self._timer = None

class SSStart(bpy.types.Operator):
    bl_idname = "wm.ss_start"
    bl_label = "Start ScreenSnap"
    bl_description = "Start monitoring and take a screenshot every N actions"
    def execute(self, context):
        prefs = context.window_manager.screen_snap_prefs
        if prefs.enabled: self.report({'INFO'}, "ScreenSnap already running."); return {'CANCELLED'}
        # _ = _default_output_dir()  # ??
        prefs.enabled = True; bpy.ops.wm.ss_modal_watcher('INVOKE_DEFAULT')
        prefs.last_message = "Started."; self.report({'INFO'}, "ScreenSnap started."); return {'FINISHED'}

class SSStop(bpy.types.Operator):
    bl_idname = "wm.ss_stop"
    bl_label = "Stop ScreenSnap"
    bl_description = "Stop monitoring"
    def execute(self, context):
        prefs = context.window_manager.screen_snap_prefs
        prefs.enabled = False; prefs.last_message = "Stopped."; self.report({'INFO'}, "ScreenSnap stopped."); return {'FINISHED'}

class SSSnapNow(bpy.types.Operator):
    bl_idname = "screensnap.snap_now"
    bl_label = "Snap Now"
    def execute(self, context):
        prefs = context.window_manager.screen_snap_prefs
        folder = _effective_dir(prefs); ensure_dir(folder)
        filepath = bpy.path.ensure_ext(os.path.join(folder, f"{CAPTURE_PREFIX}{prefs.index:07d}{CAPTURE_EXT}"), CAPTURE_EXT)
        ok = False
        try: ok = _capture_viewport(context, prefs, filepath)
        except Exception as ex:
            ok = False; print(f"[ScreenSnap] Snap Now failed: {ex}"); prefs.last_message = f"Snap Now failed: {ex}"
        if ok:
            prefs.index += 1
            # if prefs.use_fixed_camera and prefs.fixed_camera and prefs.use_turntable and prefs.turntable_target:
            #     _rotate_camera_around_target(prefs.fixed_camera, prefs.turntable_target, prefs.turntable_degrees, prefs.turntable_axis)
            self.report({'INFO'}, f"Saved: {filepath}"); return {'FINISHED'}
        self.report({'ERROR'}, "Capture failed (see console)."); return {'CANCELLED'}


_first_load = True


class SSPanel(bpy.types.Panel):
    bl_idname = "VIEW3D_PT_screensnap"
    bl_label = "ScreenSnap"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = PANEL_CATEGORY

    def calcindex(self, prefs):
        entries = []
        with os.scandir("/home/pm/KritaRecorder/20260517231119/") as it:
            for entry in it:
                n = entry.name.split('.')[0]
                if n.isdigit():
                    entries.append(int(n))
        entries.sort()
        prefs.index = entries[-1] + 1
        print('@@', prefs.index)

    def draw(self, context):
        global _first_load
        prefs = context.window_manager.screen_snap_prefs
        if _first_load:
            self.calcindex(prefs)
            _first_load = False
        col = self.layout.column(align=True)
        row = col.row(align=True)
        row.prop(prefs, "enabled", text="Enabled", toggle=True)
        row.operator("wm.ss_stop" if prefs.enabled else "wm.ss_start", text=("Stop" if prefs.enabled else "Start"), icon=('PAUSE' if prefs.enabled else 'PLAY'))
        col.label(text=f"Running: {'Yes' if prefs.enabled else 'No'}")
        if prefs.last_message: col.label(text=prefs.last_message)
        col.operator("screensnap.snap_now", text="Snap Now", icon='CAMERA_DATA')

        col.separator(); col.prop(prefs, "batch"); col.prop(prefs, "debounce_seconds")
        col.prop(prefs, "output_dir"); col.label(text=f"Saving to: {_effective_dir(prefs)}")
        col.label(text=f"Next index: {prefs.index:04d}")
        col.label(text=f"Actions until snap: {max(0, prefs.batch - prefs.counter)}")

        col.separator(); col.label(text="Actions policy:"); col.prop(prefs, "action_mode", expand=True)
        if prefs.action_mode == 'SMART':
            col.prop(prefs, "ignore_navigation_inputs")
            g = col.grid_flow(columns=2, even_columns=True)
            g.prop(prefs, "count_left"); g.prop(prefs, "count_right"); g.prop(prefs, "count_middle")
        else:
            col.label(text="Mouse clicks are ignored in STRICT mode.")
        g2 = col.grid_flow(columns=2, even_columns=True)
        g2.prop(prefs, "count_enter"); g2.prop(prefs, "count_space")
        col.prop(prefs, "extra_keys"); col.prop(prefs, "count_mesh_edits")

        col.separator(); col.label(text="Viewport capture:")
        col.prop(prefs, "capture_method", text="Method")
        col.prop(prefs, "use_fixed_camera")
        r = col.row(); r.enabled = prefs.use_fixed_camera; r.prop(prefs, "fixed_camera", text="Camera")
        col.prop(prefs, "capture_shading"); col.prop(prefs, "overlay_mode"); col.prop(prefs, "hide_grid_axes"); col.prop(prefs, "force_opaque_materials")

        col.separator(); col.label(text="Blueprint/References:")
        col.prop(prefs, "hide_blueprints_by_mode")
        r = col.row(); r.prop(prefs, "hide_collection"); r.prop(prefs, "hide_collection_recursive")

        col.separator(); col.label(text="Edit Mode:"); col.prop(prefs, "reveal_hidden_edit")

        col.separator(); col.label(text="Stop hotkey:"); col.prop(prefs, "stop_on_key")
        r = col.row(align=True); r.enabled = prefs.stop_on_key
        r.prop(prefs, "stop_key"); r.prop(prefs, "stop_use_ctrl"); r.prop(prefs, "stop_use_shift"); r.prop(prefs, "stop_use_alt")

        col.separator(); col.label(text="Turntable:")
        r = col.row(); r.enabled = prefs.use_fixed_camera; r.prop(prefs, "use_turntable")
        r = col.row(); r.enabled = prefs.use_fixed_camera and prefs.use_turntable; r.prop(prefs, "turntable_target")
        r = col.row(align=True); r.enabled = prefs.use_fixed_camera and prefs.use_turntable
        r.prop(prefs, "turntable_degrees"); r.prop(prefs, "turntable_axis", expand=True)

classes = (SSPreferences, SSModalWatcher, SSStart, SSStop, SSSnapNow, SSPanel)

def register():
    global _pending_timer
    for cls in classes: bpy.utils.register_class(cls)
    bpy.types.WindowManager.screen_snap_prefs = PointerProperty(type=SSPreferences)
    if _pending_timer is not None:
        try: bpy.app.timers.unregister(_do_capture)
        except Exception: pass
        _pending_timer = None

def unregister():
    global _pending_timer
    if hasattr(bpy.types.WindowManager, "screen_snap_prefs"):
        try: del bpy.types.WindowManager.screen_snap_prefs
        except Exception: pass
    for cls in reversed(classes):
        try: bpy.utils.unregister_class(cls)
        except Exception: pass
    if _pending_timer is not None:
        try: bpy.app.timers.unregister(_do_capture)
        except Exception: pass
        _pending_timer = None
