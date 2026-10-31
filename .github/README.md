# Om's Studio — portfolio source

This repository contains the source for a personal portfolio presented as a cozy cyberpunk studio. The room model is built in Blender and rendered in Three.js; its three displays and framed project pieces are interactive. The black page, orbit camera, and responsive project notes keep the room as the main experience.

## Stack

- Astro static site
- Three.js for the interactive 3D room and camera
- TypeScript for scene behavior
- CSS for the responsive layout
- Blender Python source for the room model, exported as glTF Binary (GLB)
- SVG as a still fallback when WebGL is unavailable

## Run locally

Use Node.js 24 (or Node.js 22.23.4 or newer).

```sh
npm install
npm run dev
```

## Build and preview

```sh
npm run build
npm run preview
```

The static output is written to `dist/`. This project is ready to connect to Vercel with the repository root as the project root and `npm run build` as the build command.

## Project layout

- `src/pages/index.astro` — the studio page and its project navigation
- `src/scripts/room.ts` — GLB loading, generated display interfaces, project selection, and orbit camera
- `src/styles/global.css` — responsive visual system
- `scripts/blender/build_studio.py` — procedural Blender scene builder and GLB exporter
- `blender/assets/` — source GLBs for the free CC0 desk, chair, keyboard, lamp, and plants
- `blender/ASSET_CREDITS.md` — model sources and license notes
- `blender/om-cyberpunk-studio.blend` — editable Blender scene
- `public/assets/om-cyberpunk-studio.glb` — optimized web model
- `public/studio.svg` — the isometric studio illustration

To regenerate the room model, run `scripts/blender/build_studio.py` from the connected Blender MCP. The builder uses local source GLBs, keeps their materials, and downsizes large textures for the web model. The scene is created separately so unrelated open Blender scenes are preserved.
