"""Exploded close-up of the new six-pin Oil Shelf corbel."""

import os

import cadquery as cq
from cadkit import viewer as cad_viewer
from ocp_vscode import Camera

import oil_shelf as model


JOINT_X = -model.SHELF_LENGTH / 2.0
LOCAL_SHIFT = (-JOINT_X, 0, -model.SHELF_BOTTOM)
SHELF_VISIBLE = 6.0 * model.INCH

CORBEL_EXPLODE_Y = -78.0
PIN_EXPLODE_Y = -168.0

post = model.left_post.translate(LOCAL_SHIFT)
corbel = model.left_corbel.translate(LOCAL_SHIFT).translate((0, CORBEL_EXPLODE_Y, 0))
pins = model.left_pins.translate(LOCAL_SHIFT).translate((0, PIN_EXPLODE_Y, 0))
shelf_end = model.rounded_yz_prism(
    SHELF_VISIBLE,
    model.SHELF_DEPTH,
    model.SHELF_THICKNESS,
    model.SHELF_CORNER_RADIUS,
    center_x=SHELF_VISIBLE / 2.0 + 65.0,
    center_z=model.SHELF_THICKNESS / 2.0,
)


def arrow_between(start, end, radius=0.8):
    start_v = cq.Vector(*start)
    end_v = cq.Vector(*end)
    direction = end_v - start_v
    unit = direction.normalized()
    head_length = 5.0
    shaft = cq.Solid.makeCylinder(radius, direction.Length - head_length, start_v, unit)
    head = cq.Solid.makeCone(2.4, 0.0, head_length, end_v - unit.multiply(head_length), unit)
    return cq.Workplane(obj=shaft.fuse(head))


shelf_arrow = arrow_between((62, 31, 6.35), (14, 31, 6.35))
corbel_arrow = arrow_between((-22, -61, -62), (-22, -13, -62))
pin_arrow = arrow_between((-22, -148, -55), (-22, -20, -55))
wall_slice = (
    cq.Workplane("XZ", origin=(0, model.WALL_PLANE_Y, 0))
    .rect(270.0, 260.0)
    .extrude(-2.0)
    .translate((70.0, 0, -65.0))
)


def show_exploded_joint():
    port = int(os.environ.get("OIL_SHELF_OCP_PORT", "3940"))
    if not cad_viewer.is_listening(port):
        print(f"viewer       none on {port} -- not shown (./viewer starts one)")
        return False
    for index, (part, name, color, alpha) in enumerate(zip(
        (post, corbel, pins, shelf_end, corbel_arrow, pin_arrow, shelf_arrow, wall_slice),
        (
            "01_tall_perforated_post_fixed",
            "02_pinned_corbel_slide_forward",
            "03_six_steel_pins_insert",
            "04_existing_shelf_end_set_down",
            "corbel_assembly_arrow",
            "pin_assembly_arrow",
            "shelf_assembly_arrow",
            "wall_3mm_behind_wood",
        ),
        (
            (148, 98, 55),
            (38, 64, 82),
            (180, 185, 190),
            (176, 126, 74),
            (225, 184, 70),
            (225, 184, 70),
            (225, 184, 70),
            (205, 205, 200),
        ),
        (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.16),
    )):
        cad_viewer.show(
            part, name=name, port=port, clear=index == 0,
            reset_camera=Camera.ISO if index == 0 else None,
            options={"color": color, "alpha": alpha, "black_edges": True},
        )
    return True


if __name__ == "__main__":
    show_exploded_joint()
    print("Exploded six-pin corbel: fit corbel to front face, insert six pins, then set shelf on saddle.")
