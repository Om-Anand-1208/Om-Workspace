# SurferFlow pastel isometric diorama: Blender + Codex kit

## Goal

Build an editable, stylized 3D diorama for the SurferFlow project: one small surfer on a surfboard, riding a sculptural curling turquoise wave, with pale foam, open water on all sides, a small rocky/plant accent, and a peach studio background. The art direction is the cute matte-clay pastel look in the supplied style reference, not realistic ocean simulation.

The included Python script is a **procedural starter model**. It uses Blender's built-in `bpy` API and basic meshes, curves, bevels, and area lights. It is intended to be easy for Codex to revise. It does not need external models or paid add-ons.

## Reference files

Use these files from the `references/` folder:

- `pastel_clay_style_reference.png`: **style only**. Match the reference's pastel palette, soft clay-like materials, clean shadows, rounded forms, and uncluttered isometric presentation. Do not copy its room subject.
- `surferflow_three_quarter_style.png`: **primary content and composition reference**. Use it for the surfer/wave relationship, foam, colors, and overall silhouette.
- `surferflow_multiview_concept_sheet.png`: rough front/back/left/right/top concept sheet and build breakdown.
- `concept_isometric.png`, `concept_front.png`, `concept_back.png`, `concept_left.png`, `concept_right.png`, `concept_top.png`: crops of the views in the concept sheet.

Important: generated multi-view pictures are visual concepts, not engineering orthographic drawings. Small details and proportions may differ between panels. The script-created Blender scene is the single source of truth for exact view consistency: it renders all six cameras from the same geometry, using the same orthographic scale and lighting.

## 1. Recommended tools

1. **Blender**: actual modelling, materials, camera setup, rendering, and `.blend` project file.
2. **Blender Python API (`bpy`)**: best for repeatable builds and global edits. Use the included script before adding one-off manual objects.
3. **Codex**: read the reference images and this guide, edit the script, run Blender, inspect renders, and iterate. Ask it to make small measured changes rather than completely rebuilding the scene every pass.
4. **Blender MCP (if already configured in your Codex environment)**: use it to inspect the scene, run snippets, change selected objects/materials, and inspect renders. First inspect the MCP's available tools and their actual schemas. Do not guess tool names. If MCP cannot reliably run scripts or render, use the shell commands below.

No fluid simulation is necessary for this look. Use one mesh ribbon for the wave, a few foam spheres/curves, smooth ellipsoids for the surfer, and a beveled cube for the surfboard. Keeping the geometry simple is intentional.

## 2. Build the scene

### Linux terminal

Run from this kit's directory:

```bash
blender --version
blender --background --python surferflow_diorama.py -- --output-dir ./surferflow_output
```

The second command writes:

```text
surferflow_output/
├── SurferFlow_Diorama.blend
├── view_three_quarter.png
├── view_front.png
├── view_back.png
├── view_left.png
├── view_right.png
└── view_top.png
```

Open the editable project:

```bash
blender ./surferflow_output/SurferFlow_Diorama.blend
```

For a faster model-only pass without rendering all six views:

```bash
blender --background --python surferflow_diorama.py -- --output-dir ./surferflow_output --no-render
```

If Blender is not installed, install it through the package manager or official Blender distribution before running the script. The script cannot execute in normal system Python because `bpy` is provided by Blender.

### Blender GUI

Open Blender, switch to the **Scripting** workspace, open `surferflow_diorama.py`, then click **Run Script**. The script writes to `./surferflow_output` relative to Blender's working directory. For predictable paths and all renders, prefer the terminal command above.

**Safety:** the script clears objects from the currently open scene before building. Run it in a fresh Blender file or save a backup first; do not run it over unrelated work you need to keep.

## 3. How the model is organized

The script uses descriptive object names and collections. Edit the named part instead of applying random transforms to the whole scene.

| Part | Main objects / code | What to change |
|---|---|---|
| Ocean tile | `Ocean_Tile_Beveled_Base`, `Ocean_Surface` | Overall footprint, thickness, base color |
| Wave | `build_wave()`, `Wave_Main_Curled_Ribbon` | The `profile` list controls the wave silhouette; `y_min` / `y_max` control its width |
| Foam | `Foam_Crest_*`, `Foam_Foot_*`, `Ocean_Ripple_*` | Number, spacing, size, and material of foam/ripple details |
| Surfer | `build_surfer()` and objects prefixed `Surfer_` | Stance, body proportions, colors, hair, sunglasses |
| Board | `build_surfboard()`, `Surfboard_*` | Length, width, board tilt, accent stripe |
| Coast detail | `build_coastal_details()` | Rocks, sand patch, and small leaves; remove these if the scene feels busy |
| Lighting | `build_studio()` | Light energy, size, and warm/cool color balance |
| Views | `build_cameras()` | Orthographic camera directions and `ortho_scale` |

### The most valuable edit: the wave profile

In `build_wave()`, the `profile` list is a list of `(x, z)` points. It begins near the water surface, rises up the face, curves over the crest, and curls back inward. Move a few points to alter the shape. Keep the points in order along the wave surface. The mesh is extruded across the `y` direction, then given thickness and soft edges.

For a simpler wave, use fewer profile points and a lower crest. For a more dramatic wave, raise the middle crest points and pull the final curl points toward negative `x`. Change one or two points at a time, render again, and compare the three-quarter camera.

## 4. Iteration loop for Codex

1. Read this guide and inspect `references/surferflow_three_quarter_style.png` plus `references/pastel_clay_style_reference.png`.
2. Run the starter script in a fresh scene.
3. Inspect `view_three_quarter.png` first. Do not judge a model only from the top view; the wave's silhouette is the main read in three-quarter view.
4. Render all cameras and check that the whole diorama stays in frame at the same scale.
5. Make a small change, regenerate, compare, and keep the good changes. Avoid adding lots of decorative details just because there is empty space.
6. Open the `.blend` and confirm the model is still editable and that objects have meaningful names.
7. When satisfied, render the final three-quarter image at 1200–1600 px and save a lightweight preview separately.

Suggested quality order:

- First: recognizable curling wave silhouette and clearly visible board.
- Second: surfer's pose reads correctly and feet meet the board.
- Third: foam is arranged in a few broad clusters, not thousands of tiny particles.
- Fourth: soft peach background, matte pastel materials, gentle shadows.
- Last: sparse ripples, tiny rocks, and leaves.

## 5. Prompt to give Codex

Copy this prompt into Codex from this folder:

> Build and iteratively refine the SurferFlow pastel isometric diorama in Blender using `surferflow_diorama.py` and the images in `references/`. Read `CODEX_BLENDER_GUIDE.md` first. Use `surferflow_three_quarter_style.png` as the main composition reference and `pastel_clay_style_reference.png` for style only. The target is a beginner-manageable Blender model: one stylized surfer on a cream surfboard riding one sculptural turquoise curling wave, water surrounding the model, chunky pale foam, a tiny rock/plant accent, matte pastel materials, peach backdrop, soft area lights, orthographic cameras. Do not use fluid simulation or add lots of objects. Run the script in a fresh scene because it clears scene objects. Prefer editing named functions/parameters in the existing script over rebuilding from scratch. Generate the `.blend` plus the six camera renders. Inspect the render from `CAM_ThreeQuarter`; fix visible problems such as surfer/board intersections, wave geometry, cropped edges, foam clutter, or inconsistent scale. Re-render all views after each structural change. If Blender MCP is connected, inspect its actual available tools before using them; otherwise run Blender via shell. Do not claim a render succeeded unless the output file exists.

## 6. Blender MCP workflow (if available)

Tool names vary by MCP installation. Ask Codex to:

- discover and read the installed Blender MCP tool descriptions first;
- start with a fresh scene or new `.blend` file;
- run the script through the supported Blender-Python execution path, or use Blender's shell CLI;
- inspect object names, active camera, scene dimensions, and render results;
- make edits through named objects or the script, not by deleting the whole scene unexpectedly;
- render the six named views and verify each output exists.

If the MCP operates only on the active scene and cannot pass a script file, have Codex read `surferflow_diorama.py` and execute its contents using the MCP-supported Python-code action, provided that action permits multi-line Blender Python. Otherwise, the CLI route is more reliable.

## 7. Final validation checklist

- [ ] Surfer stands on the board; feet do not visibly float or sink.
- [ ] Curling wave remains the focal point and is recognizable from three-quarter view.
- [ ] Water surrounds the wave and fills the tile.
- [ ] Foam reads as a few broad, soft shapes, not photorealistic spray.
- [ ] Entire base fits in all views; no object is clipped by the camera.
- [ ] All six views use the same orthographic scale and resolution.
- [ ] Materials stay muted pastel and mostly matte.
- [ ] `.blend` file opens, and the named objects remain editable.
- [ ] Final renders are present and have non-zero file sizes.
