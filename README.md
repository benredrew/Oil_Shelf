# Oil Shelf

Concept model for a pinned shelf corbel. Dimensions are modeled in millimetres
from the supplied inch values.

- Existing rounded beam: 31.75 × 2.80 × 0.50 in
- Two vertical post references: 1.27 × 1.75 in
- Tall posts with a centred 2 × 45 pattern of 1/4 in through-holes
- Two FDM front corbels, each retained by six removable 1/4 in steel pins

The posts are shown 72 in tall with the shelf at 36 in. Their rear faces align
with the shelf rear edge, 3 mm in front of the wall reference plane. The former
collar and tapered-key parts are retired. The replacement is a 4 in under-shelf
saddle on a deep 6 in triangular corbel, pinned through three vertically spaced
rows. This is a design concept, not a load-rated structural connection.

Print the corbel with its broad XZ web flat on the bed so span-direction bending
and pin bearing lie in the stronger layer plane. Use a generous perimeter count
and solid/modifier volume around every pin hole and at the saddle/web junction;
sparse infill is appropriate only in the large, low-stress web interior. Avoid
relying on Z-layer tension or peel at the pin holes (roughly the 0.4-strength
direction of the stated FDM anisotropy).

Install [Toolbox](https://github.com/benredrew/toolbox) and run its
`./install` command once. Then run `./viewer` in one terminal and `./preview`
in another. The dedicated CadKit instance listens on `127.0.0.1:3940`.
Printable STEP and STL files are written to `output/` whenever `./preview`
runs.

For the close-up assembly sequence, run `./preview exploded_joint.py`. It shows
the fixed perforated post, corbel, six pins, and shelf end along their insertion
paths.

`./viewer_full` plus `./preview_full` opens an independent full-assembly viewer
on port 3941, leaving the exploded view on port 3940 unchanged.
