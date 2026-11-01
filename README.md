# Om’s Workspace

A personal portfolio inside an interactive 3D room. Explore the television to browse projects, open the workstation screens, and visit project pages for artwork, links, and recent GitHub activity.

Built with Astro, TypeScript, Three.js, CSS, and Blender.

## Requirements and local development

Use Node.js 24 or Node.js 22.23.4 or later. From the repository root:

```bash
npm install
npm run dev
```

Open the local address printed by Astro, normally `http://localhost:4321/`. Keep the command running while previewing the site.

```bash
npm run build    # Build the static site in dist/
npm run preview  # Preview the production build locally
```

The site is built as static files and can be deployed to a static host using `npm run build` and the `dist/` output directory.

## Explore the workspace

- Drag the room to orbit, scroll to zoom, and right-drag to pan.
- Select the TV to open **My Projects**, then choose a card for its project page. The catalogue also opens at `/projects/`.
- Select the monitor to open the fastfetch-style profile, or the laptop to replay the welcome. Click inside either window to replay it; use its close button or Escape to close it.
- Select the LinkedIn, GitHub, or Codolio objects to visit those profiles. Keyboard-accessible controls for the TV and workstation screens are available by tabbing into the room.
- Project activity is fetched from the corresponding public GitHub repository. If GitHub is unavailable or rate-limited, the page links to the full history instead.

A normal refresh preserves the open catalogue or current project URL. The supported keyboard restart shortcuts (`Ctrl+Shift+R`, `Ctrl+F5`, and `Cmd+Shift+R`) return to the opening screen; they are handled by the site and do not guarantee bypassing the browser cache.

## Add a project

Each project is defined by a `project.json` and its media inside `src/projects/<slug>/`. The folder name is the URL slug: for example, `src/projects/my-project/` becomes `/projects/my-project/`.

1. Create a folder named with lowercase letters, numbers, and hyphens, such as `src/projects/my-project/`.
2. Create `project.json` in that folder using the example below, and fill in your project details.
3. Put the referenced cover image and optional screenshots in the same folder. Remove `gallery` if you do not have additional images.
4. Start or rebuild the site. It discovers the project and adds its page, a card in **My Projects**, and an entry on the TV automatically. If the dev server is already running, restart it if the new folder does not appear.

For example:

```text
src/projects/my-project/
├── project.json
├── cover.png
└── screenshot.png
```

```json
{
  "title": "My new project",
  "description": "A short description of the project.",
  "stack": "TypeScript · Astro",
  "repo": "My-Repository",
  "owner": "Om-Anand-1208",
  "url": "",
  "kind": "image",
  "cover": "cover.png",
  "gallery": [
    { "file": "screenshot.png", "alt": "A view of my project" }
  ]
}
```

`title`, `description`, `stack`, `repo`, `kind`, and `cover` are required. `owner` defaults to `Om-Anand-1208`, `url` is an optional deployed link, and an optional numeric `order` controls catalogue order. The `owner` and `repo` values select the GitHub links and activity feed.

For a 3D project, set `"kind": "model"`, place a `.glb` file in the folder, and add `"model": "model.glb"`. The cover remains required for the catalogue and as a fallback. `"kind": "room"` embeds the main workspace. Supported image extensions are lowercase PNG, JPG, JPEG, and WebP. Run `npm run build` to check the project; invalid slugs, missing required fields, and missing media produce an error identifying the project.

## Change the room and profile

- `src/scripts/room.ts` loads the room and controls interactions, screens, and the TV. `greenery.ts`, `tech-shelf.ts`, and `wall-decor.ts` add the corresponding details.
- `src/pages/index.astro` contains the room and screen-window markup. `screen-windows.ts` controls the terminal and laptop animations; `welcome.ts` controls the opening sequence.
- `src/projects/` holds each project’s metadata and media. `src/data/projects.ts` discovers and validates those folders. `src/pages/projects/[slug].astro` is the shared project-page template.
- `src/styles/` contains site styling; `src/assets/` is configured as Astro’s static directory for the room model and shared assets. `src/assets/draco/` contains the decoder required by compressed models. Files in that folder are served from the site root (for example, `src/assets/draco/` is served at `/draco/`).
- The deployed GLB models and artwork are kept in their project folders or in `src/assets/`; editable Blender source files are not included.

Profile links and the GitHub contribution username are configured in `src/scripts/room.ts`. The profile text shown in the terminal is in `src/pages/index.astro` and its monitor texture in `src/scripts/room.ts`.
