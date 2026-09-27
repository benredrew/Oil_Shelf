<!--
Author: Claude (Opus 5)
Co-Author: Brendan Fennell
-->
# Oil Shelf

CadQuery model of a shelf and its pinned corbels, cut from real lumber. For
any agent — Claude, Codex, or otherwise.

```bash
./preview          # build the model (headless; no viewer needed)
./preview_full     # build, pointed at the full-assembly viewer on 3941
./viewer           # start the viewer on 3940
./viewer_full      # start the full-assembly viewer on 3941
```

## This project owns no Python environment

It runs on **`cad-python`**, the shared CAD interpreter
(`~/.local/bin/cad-python` → `~/.local/share/cad/venv`). It used to invoke
`../Aquarium/.venv/bin/python` directly from four separate scripts, which
meant renaming, moving or rebuilding a *different* project broke this one, and
the dependency was invisible unless you read every script. Do not reintroduce
a relative path into a sibling project.

The shared `cadkit` package is importable from that interpreter:
`cadkit.sheet` for drawing sheets, `cadkit.viewer` for viewer handling. See
`~/Projects/cadkit/AGENTS.md`.

## Building never requires a viewer

`show_assembly()` checks whether anything is listening on `OCP_PORT` and
returns without drawing if not, so `./preview` works headless. Do not make the
build depend on a GUI being up — that charges a human interaction for every
run. `OIL_SHELF_OCP_PORT` overrides the port; 3940 and 3941 belong to this
project.

## History

Version control starts at "Oil Shelf as it stood before any stabilisation" —
this project had none until then, so nothing before that commit is recoverable.
