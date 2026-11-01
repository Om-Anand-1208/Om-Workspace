type GalleryImage = { src: string; alt: string };
type ProjectManifest = {
  title: string;
  description: string;
  stack: string;
  repo: string;
  owner?: string;
  url?: string;
  order?: number;
  kind: 'image' | 'model' | 'room';
  cover: string;
  model?: string;
  gallery?: { file: string; alt: string }[];
};
export type Project = Omit<ProjectManifest, 'cover' | 'model' | 'gallery'> & {
  slug: string;
  cover: string;
  model?: string;
  gallery: GalleryImage[];
};

// Every project lives in its own folder. Vite discovers the manifests and
// assets for both the catalogue and the project pages at build/dev time.
const manifests = import.meta.glob<ProjectManifest>('../projects/*/project.json', { eager: true, import: 'default' });
const assets = import.meta.glob<string>('../projects/*/*.{png,jpg,jpeg,webp,glb}', { eager: true, query: '?url', import: 'default' });

export const projects: Project[] = Object.entries(manifests).map(([path, data]) => {
  const slug = path.split('/').at(-2)!;
  const label = `Project ${slug}`;
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(slug)) throw new Error(`${label}: folder name must be a lowercase URL slug.`);
  if (!data.title || !data.description || !data.stack || !data.repo || !data.cover) throw new Error(`${label}: title, description, stack, repo and cover are required.`);
  if (!['image', 'model', 'room'].includes(data.kind)) throw new Error(`${label}: kind must be image, model or room.`);
  if (data.kind === 'model' && !data.model) throw new Error(`${label}: model projects need a model file.`);
  const asset = (file: string) => {
    if (file.includes('/') || file.includes('..')) throw new Error(`${label}: assets must be in the project folder.`);
    const url = assets[`../projects/${slug}/${file}`];
    if (!url) throw new Error(`${label}: asset ${file} was not found.`);
    return url;
  };
  return {
    ...data,
    slug,
    cover: asset(data.cover),
    model: data.model ? asset(data.model) : undefined,
    gallery: (data.gallery ?? []).map(image => ({ src: asset(image.file), alt: image.alt || `${data.title} screenshot` })),
  };
}).sort((a, b) => (a.order ?? 999) - (b.order ?? 999) || a.title.localeCompare(b.title));
