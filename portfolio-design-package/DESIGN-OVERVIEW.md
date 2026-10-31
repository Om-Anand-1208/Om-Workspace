# Om's Room — project design overview

Captured 31 October 2026 from the local production build. The screenshots are desktop viewport captures, not full-page exports; the catalogue is shown in two images to cover both rows. Commit history is live data and may change or be unavailable when GitHub's API is rate-limited.

## Idea

Om's Room is a developer portfolio presented as a small interactive studio. The room provides a personal, playful first impression, while a conventional project catalogue and readable project pages make the work accessible without needing to discover every 3D object. The intended feeling is cozy and curious, with developer-oriented typography and real project information.

## Visitor journey

1. **Room:** A full-screen isometric studio introduces Om. Visitors can orbit and zoom the room, reset the camera, follow social links, or use the TV / Explore projects button.
2. **Catalogue:** The TV opens a modal grid of six projects. Each card combines a snapshot of its isometric model, a project name, and a short category.
3. **Project page:** Each project has a separate URL. A three-column layout places its description, technology and links on the left, a rotatable 3D model in the middle, and recent GitHub commits on the right. The catalogue and room are linked from the page.

## Visual language

- Dark, nearly black and deep green surfaces let the room and models stand out.
- Warm wood, soft pastels, plants, small objects and rounded edges support the cozy diorama style.
- Restrained sans-serif headings and small monospaced labels suggest a developer's working environment.
- Isometric model snapshots make the catalogue visually navigable; the interactive versions let visitors inspect a project from different angles.
- Fine borders, muted green accents and generous spacing provide structure without competing with the models.

## Project scenes

| Project | Scene concept | Page |
| --- | --- | --- |
| SurferFlow | A surfer on calm water beside a sandy coast with pines and coastal plants. | `/projects/surferflow/` |
| Cubenikal | A 5×5×5 directional steel-block puzzle on a desk, with an extracted block, lamp and tea. The repository is a fork. | `/projects/cubenikal/` |
| eUdyaan | A quiet garden and bench surrounding a phone displaying the app's home interface. | `/projects/eudyaan/` |
| Guess Whose Song | Four music-app characters performing together on a small stage. | `/projects/guess-whose-song/` |
| Flood Monitoring System | A floodplain scene in front of a dashboard representing the project's data inputs and model comparisons. | `/projects/flood-monitoring/` |
| Om's Room | The actual room model, showing the portfolio itself as a work in progress. | `/projects/om-portfolio/` |

## Interaction and implementation

The site uses Astro for static pages, Three.js for the interactive room and project models, TypeScript for client behavior, and Blender-authored GLB assets. The catalogue uses static project metadata; project pages request the six latest commits on each repository's default branch from GitHub's public API. Commit entries link to their source. If activity cannot be fetched, the page offers a link to GitHub instead.

The catalogue is a dialog with a close control and direct keyboard-accessible project links. The project pages retain a static image if the model cannot load. Social links and the Explore projects button are available as ordinary HTML controls alongside the room's 3D interactions.

## Screenshot index

- `01-home.jpg` — room and introduction
- `02-catalogue-top.jpg` and `03-catalogue-bottom.jpg` — both rows of the project catalogue
- `04-surferflow.jpg` — SurferFlow project page
- `05-cubenikal.jpg` — Cubenikal project page
- `06-eudyaan.jpg` — eUdyaan project page
- `07-guess-whose-song.jpg` — Guess Whose Song project page
- `08-flood-monitoring.jpg` — Flood Monitoring System project page
- `09-oms-room.jpg` — Om's Room project page

## Current boundaries

The scenes are stylized representations rather than literal screenshots of each application. The public Om-Portfolio repository may not yet contain the current local Astro implementation, so its live commit history should not be read as the complete history of this version. The website credits Bruno Simon for the room; see the project's asset documentation for more detail. Screenshots reflect the state of the local build at capture time.
