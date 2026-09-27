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
toolbox preview --name oil-shelf-agent -- ./preview
```

## This project uses Toolbox's Python environment

Install [Toolbox](https://github.com/benredrew/toolbox) once and run its
`./install` command. That creates the `toolbox` command, backed by its pinned
CAD runtime. This project invokes `toolbox python`; it must never reach into a
sibling checkout, a `.venv`, or `cad-python`.

The shared `cadkit` package is importable from Toolbox:
`cadkit.sheet` for drawing sheets, `cadkit.viewer` for viewer handling. See
CadKit's published documentation.

## Building never requires a viewer

`show_assembly()` checks whether a browser-ready viewer is on `OCP_PORT` and
returns without drawing if not, so `./preview` works headless. Do not make the
build depend on a GUI being up — that charges a human interaction for every
run. `OIL_SHELF_OCP_PORT` overrides the port; 3940 and 3941 belong to this
project. For an interactive preview, use the one `toolbox preview` command
shown above: it starts/reserves the viewer, opens the browser, waits for that
browser to register, then runs the build with `CAD_VIEWER_PORT` injected.
That standard variable takes precedence over the Oil-specific fallback, so
parallel agents receive isolated viewers without repurposing 3940/3941.
Never start `./viewer` and separately run `./preview` as a hand-timed pair;
OCP-VSCode drops model data sent before the browser is connected. Plain
`./preview` remains the headless build path.

## History

Version control starts at "Oil Shelf as it stood before any stabilisation" —
this project had none until then, so nothing before that commit is recoverable.
