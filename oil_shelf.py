"""Oil Shelf -- pinned FDM corbels on tall, perforated vertical posts.

X follows the shelf span, Y is wall-to-room depth (wall at +Y), and Z is up.
The 1.27-inch post face is tangent to each beam end; the 1.75-inch face is the
front face, which carries the 2-column pin pattern.  The former collar/key
joint has intentionally been removed.
"""

import os
from pathlib import Path

import cadquery as cq
from cadkit import viewer as cad_viewer
from ocp_vscode import Camera


INCH = 25.4

# Existing wood
SHELF_LENGTH = 31.75 * INCH
SHELF_DEPTH = 2.80 * INCH
SHELF_THICKNESS = 0.50 * INCH
SHELF_CORNER_RADIUS = SHELF_THICKNESS / 2.0

# The 1.27-inch face is the end-contact depth; the 1.75-inch face is visible
# from the room and is wide enough for two 1.25-inch-spaced pin columns.
POST_DEPTH = 1.27 * INCH
POST_FACE_WIDTH = 1.75 * INCH
POST_HEIGHT = 72.0 * INCH
SHELF_ELEVATION = 36.0 * INCH
WALL_GAP = 3.0

# Existing post hole grid and removable steel pins
PIN_DIAMETER = 0.25 * INCH
PIN_RADIUS = PIN_DIAMETER / 2.0
PIN_COLUMN_SPACING = 1.25 * INCH
PIN_ROW_SPACING = 1.50 * INCH
PIN_ROWS = 45  # 2 × 45, centred on the 72-inch post face
PIN_CLEARANCE = 0.30
MOUNT_ROWS = (
    SHELF_ELEVATION - 3 * PIN_ROW_SPACING,
    SHELF_ELEVATION - 2 * PIN_ROW_SPACING,
    SHELF_ELEVATION - 1 * PIN_ROW_SPACING,
)

# New printed corbel. Material is concentrated at the load path rather than in
# an enclosing socket.
BRACKET_THICKNESS = 10.0  # front-to-back pin-bearing thickness
SADDLE_THICKNESS = 8.0
SADDLE_LENGTH = 4.0 * INCH
SADDLE_CLEARANCE = 0.40
CORBEL_DROP = 6.0 * INCH
EDGE_BREAK = 1.0

SHELF_BOTTOM = SHELF_ELEVATION
SHELF_CENTER_Z = SHELF_BOTTOM + SHELF_THICKNESS / 2.0
SHELF_TOP = SHELF_BOTTOM + SHELF_THICKNESS
POST_CENTER_Y = SHELF_DEPTH / 2.0 - POST_DEPTH / 2.0
POST_FRONT_Y = POST_CENTER_Y - POST_DEPTH / 2.0
POST_BACK_Y = POST_CENTER_Y + POST_DEPTH / 2.0
WALL_PLANE_Y = SHELF_DEPTH / 2.0 + WALL_GAP

ROOT = Path(__file__).parent
OUTPUT_DIR = ROOT / "output"
OCP_PORT = int(os.environ.get("OIL_SHELF_OCP_PORT", "3940"))


def rounded_yz_prism(length, depth, height, radius, center_x=0, center_y=0, center_z=0):
    """Prism along X with the supplied tangent-radius rounded YZ section."""
    straight_depth = depth - 2.0 * radius
    body = cq.Workplane("XY").box(
        length, straight_depth, height, centered=(True, True, True)
    ).translate((center_x, center_y, center_z))
    for y in (-straight_depth / 2.0, straight_depth / 2.0):
        end = (
            cq.Workplane("YZ")
            .workplane(offset=center_x - length / 2.0)
            .center(y + center_y, center_z)
            .circle(radius)
            .extrude(length)
        )
        body = body.union(end)
    return body


def pin_positions(post_x, rows=None):
    """Global XZ centres for the specified rows of a post's 2-column grid."""
    if rows is None:
        first = POST_HEIGHT / 2.0 - (PIN_ROWS - 1) * PIN_ROW_SPACING / 2.0
        rows = tuple(first + i * PIN_ROW_SPACING for i in range(PIN_ROWS))
    return [
        (post_x + x_offset, z)
        for z in rows
        for x_offset in (-PIN_COLUMN_SPACING / 2.0, PIN_COLUMN_SPACING / 2.0)
    ]


def cylinders_along_y(points, radius, start_y, length):
    """A compound of cylinders from start_y toward the front (-Y)."""
    solids = [
        cq.Solid.makeCylinder(
            radius, length, cq.Vector(x, start_y, z), cq.Vector(0, -1, 0)
        )
        for x, z in points
    ]
    return cq.Workplane(obj=cq.Compound.makeCompound(solids))


def build_shelf():
    return rounded_yz_prism(
        SHELF_LENGTH,
        SHELF_DEPTH,
        SHELF_THICKNESS,
        SHELF_CORNER_RADIUS,
        center_z=SHELF_CENTER_Z,
    )


def post_center_x(side):
    return side * SHELF_LENGTH / 2.0 + side * POST_FACE_WIDTH / 2.0


def build_post(side):
    """Tall post with the complete front-face 2 × n through-hole pattern."""
    x = post_center_x(side)
    post = (
        cq.Workplane("XY")
        .center(x, POST_CENTER_Y)
        .box(POST_FACE_WIDTH, POST_DEPTH, POST_HEIGHT, centered=(True, True, False))
        .edges("|Z")
        .fillet(1.2)
    )
    cutter = cylinders_along_y(
        pin_positions(x), PIN_RADIUS, POST_BACK_Y + 1.0, POST_DEPTH + 2.0
    )
    return post.cut(cutter)


def build_pins(side):
    """Six removable 1/4-inch reference pins used by one corbel."""
    x = post_center_x(side)
    return cylinders_along_y(
        pin_positions(x, MOUNT_ROWS),
        PIN_RADIUS,
        POST_BACK_Y,
        POST_DEPTH + BRACKET_THICKNESS,
    )


def build_pinned_corbel(side):
    """Front plate + under-shelf saddle + deep triangular web, all one print."""
    joint_x = side * SHELF_LENGTH / 2.0
    post_x = post_center_x(side)
    plate_bottom = SHELF_BOTTOM - CORBEL_DROP
    plate_top = SHELF_BOTTOM + 7.0
    plate_height = plate_top - plate_bottom
    plate_center_z = (plate_top + plate_bottom) / 2.0

    # Pin-bearing plate stays entirely in front of the post. Its X edges end at
    # the post faces, keeping the beam's end face tangent and unobstructed.
    plate = (
        cq.Workplane("XY")
        .center(post_x, POST_FRONT_Y - BRACKET_THICKNESS / 2.0)
        .box(
            POST_FACE_WIDTH,
            BRACKET_THICKNESS,
            plate_height,
            centered=(True, True, True),
        )
        .translate((0, 0, plate_center_z))
    )

    # Full-depth under-saddle spreads compression over the existing beam rather
    # than concentrating it at a printed lip.
    saddle_center_x = joint_x - side * SADDLE_LENGTH / 2.0
    saddle = (
        cq.Workplane("XY")
        .center(saddle_center_x, 0)
        .box(
            SADDLE_LENGTH,
            SHELF_DEPTH + 2.0 * SADDLE_CLEARANCE,
            SADDLE_THICKNESS,
            centered=(True, True, True),
        )
        .translate((0, 0, SHELF_BOTTOM - SADDLE_THICKNESS / 2.0))
    )

    # The broad XZ web carries span-direction cantilever load into the three
    # vertically spaced pin rows. It overlaps plate and saddle slightly.
    anchor_x = joint_x + side * 0.8
    inward_x = joint_x - side * SADDLE_LENGTH
    web_points = [
        (anchor_x, SHELF_BOTTOM - SADDLE_THICKNESS / 2.0),
        (inward_x, SHELF_BOTTOM - SADDLE_THICKNESS / 2.0),
        (anchor_x, SHELF_BOTTOM - CORBEL_DROP),
    ]
    web = (
        cq.Workplane("XZ", origin=(0, POST_FRONT_Y, 0))
        .polyline(web_points)
        .close()
        .extrude(BRACKET_THICKNESS)
    )

    pin_cut = cylinders_along_y(
        pin_positions(post_x, MOUNT_ROWS),
        PIN_RADIUS + PIN_CLEARANCE,
        POST_FRONT_Y + 1.0,
        BRACKET_THICKNESS + 2.0,
    )
    corbel = plate.union(saddle).union(web).cut(pin_cut)
    try:
        corbel = corbel.edges("|Z").fillet(EDGE_BREAK)
    except Exception:
        pass
    return corbel


def build_wall_reference():
    width = SHELF_LENGTH + 2.0 * POST_FACE_WIDTH + 4.0 * INCH
    return (
        cq.Workplane("XZ", origin=(0, WALL_PLANE_Y, 0))
        .rect(width, POST_HEIGHT)
        .extrude(-2.0)
        .translate((0, 0, POST_HEIGHT / 2.0))
    )


shelf = build_shelf()
left_post = build_post(-1)
right_post = build_post(1)
left_corbel = build_pinned_corbel(-1)
right_corbel = build_pinned_corbel(1)
left_pins = build_pins(-1)
right_pins = build_pins(1)
wall_reference = build_wall_reference()


def show_assembly():
    """Push to a viewer if one is up; say so and carry on if not.

    Previously this called set_port/show directly, so building the model at
    all required a viewer to be running on OCP_PORT. cadkit.viewer.show
    reports an absent viewer and returns False instead of raising, so the
    model can be built headless.
    """
    if not cad_viewer.is_listening(OCP_PORT):
        print(f"viewer       none on {OCP_PORT} -- not shown "
              f"(./viewer starts one)")
        return False
    for index, (part, name, color, alpha) in enumerate(zip(
        (
            shelf, left_post, right_post, left_corbel, right_corbel,
            left_pins, right_pins, wall_reference,
        ),
        (
            "existing_oil_shelf_beam",
            "left_tall_perforated_post",
            "right_tall_perforated_post",
            "left_pinned_fdm_corbel",
            "right_pinned_fdm_corbel",
            "left_six_steel_pins",
            "right_six_steel_pins",
            "wall_clearance_reference",
        ),
        (
            (176, 126, 74),
            (148, 98, 55),
            (148, 98, 55),
            (38, 64, 82),
            (38, 64, 82),
            (180, 185, 190),
            (180, 185, 190),
            (205, 205, 200),
        ),
        (1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.16),
    )):
        cad_viewer.show(
            part, name=name, port=OCP_PORT, clear=index == 0,
            reset_camera=Camera.ISO if index == 0 else None,
            options={"color": color, "alpha": alpha, "black_edges": True},
        )
    return True


def export_printables():
    OUTPUT_DIR.mkdir(exist_ok=True)
    for name, part in {
        "left_pinned_corbel": left_corbel,
        "right_pinned_corbel": right_corbel,
    }.items():
        cq.exporters.export(part, str(OUTPUT_DIR / f"{name}.step"))
        cq.exporters.export(
            part, str(OUTPUT_DIR / f"{name}.stl"), tolerance=0.05, angularTolerance=0.1
        )


if __name__ == "__main__":
    export_printables()
    show_assembly()
    print(f"shelf: {SHELF_LENGTH:.2f} x {SHELF_DEPTH:.2f} x {SHELF_THICKNESS:.2f} mm")
    print(f"post grid: 2 x {PIN_ROWS}, {PIN_DIAMETER:.2f} mm holes, {PIN_COLUMN_SPACING:.2f} x {PIN_ROW_SPACING:.2f} mm pitch")
    print("each corbel uses six 1/4-inch steel pins in a 2 x 3 pattern")
