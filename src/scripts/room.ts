import { projects } from '../data/projects';
import { addTechShelf } from './tech-shelf';
import { improveTextureFiltering, renderPixelRatio } from './render-quality';
import { addGreenery } from './greenery';
import { addWallDecor } from './wall-decor';
import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const viewportElement = document.querySelector<HTMLElement>('#room-viewport');
if (!viewportElement) throw new Error('Room viewport not found.');
const viewport: HTMLElement = viewportElement;
const resetButton = document.querySelector<HTMLButtonElement>('#reset-view');
const status = document.querySelector<HTMLElement>('#room-status');
const socialHint = document.querySelector<HTMLElement>('#social-hint');
if (status) {
  status.textContent = 'Loading the room…';
  status.hidden = false;
}

// Fill these four fields when the account details are ready. The scene objects
// already use this single config for their links and the live contribution feed.
const portfolioProfiles = {
  linkedinUrl: 'https://www.linkedin.com/in/om-anand-8bb7242b2',
  githubUrl: 'https://github.com/Om-Anand-1208',
  githubUsername: 'Om-Anand-1208',
  codolioUrl: 'https://codolio.com/profile/om_anand_7323',
};

type SocialKey = 'linkedin' | 'github' | 'codolio' | 'projects' | 'android' | 'resume' | 'experience';
type InteractiveItem = {
  root: THREE.Group;
  key: SocialKey;
  label: string;
  url: string;
  baseScale: number;
  hoverScale: number;
};

type GitHubContribution = {
  date: string;
  count: number;
  level: number;
};

const interactiveItems: InteractiveItem[] = [];
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let hoveredItem: InteractiveItem | null = null;
let hoveredLabel = '';
let roomModel: THREE.Object3D | null = null;
let pointerDownPosition: { x: number; y: number } | null = null;
let hintTimer: number | undefined;

const scene = new THREE.Scene();
scene.background = new THREE.Color('#050505');

const camera = new THREE.PerspectiveCamera(20, 1, 0.1, 150);
const startPosition = new THREE.Vector3(-15.2, 10.8, 15.2);
const startTarget = new THREE.Vector3(0, 2, 0);
camera.position.copy(startPosition);

let renderer: THREE.WebGLRenderer;
try {
  renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
} catch (error) {
  if (status) status.textContent = 'The 3D room is unavailable in this browser. Explore the projects using the menu.';
  window.dispatchEvent(new Event('room-ready'));
  throw error;
}
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.2;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
viewport.appendChild(renderer.domElement);

function sharpenTexture<T extends THREE.Texture>(texture: T): T {
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.anisotropy = renderer.capabilities.getMaxAnisotropy();
  texture.minFilter = THREE.LinearMipmapLinearFilter;
  texture.magFilter = THREE.LinearFilter;
  texture.generateMipmaps = true;
  texture.needsUpdate = true;
  return texture;
}

const controls = new OrbitControls(camera, renderer.domElement);
controls.target.copy(startTarget);
controls.minDistance = 10;
controls.maxDistance = 50;
controls.maxPolarAngle = Math.PI / 2;
controls.minAzimuthAngle = -Math.PI / 2;
controls.maxAzimuthAngle = 0;
controls.update();

// Wait for the room and its dependent models, textures, and icons before revealing it.
THREE.DefaultLoadingManager.onLoad = () => {
  if (!roomModel) return;
  render();
  if (status) status.hidden = true;
  window.dispatchEvent(new Event('room-ready'));
};

const modelLoader = new GLTFLoader();
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('/draco/');
modelLoader.setDRACOLoader(dracoLoader);

// A canvas version of the fastfetch view is visible on the room monitor.
function makeMonitorTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 960; canvas.height = 600;
  const context = canvas.getContext('2d');
  const texture = sharpenTexture(new THREE.CanvasTexture(canvas));
  if (!context) return texture;
  const portrait = new Image();
  const draw = () => {
    context.fillStyle = '#030506'; context.fillRect(0, 0, 960, 600);
    context.fillStyle = '#43f598'; context.font = 'bold 22px monospace';
    context.fillText('(psykr@fedora)  ›', 30, 48);
    context.fillStyle = '#e8eef1'; context.fillText('fastfetch', 292, 48);
    if (portrait.complete && portrait.naturalWidth) context.drawImage(portrait, 32, 120, 340, 340);
    const rows = [
      ['Om Anand', ''], ['────────────', ''], ['Focus', 'Software & creative code'],
      ['Building', 'Web, Android & games'], ['Languages', 'Java, Kotlin, JavaScript, Python'],
      ['Frontend', 'Astro, Three.js, Compose'], ['Backend', 'Ktor, Firebase, Redis'],
      ['Graphics', 'Blender, Babylon.js, WebGL'], ['Projects', `${projects.length} projects`],
      ['GitHub', 'Om-Anand-1208'], ['Status', 'Learning & building'],
    ];
    context.font = '22px monospace';
    rows.forEach(([label, value], index) => {
      const y = 108 + index * 32;
      context.fillStyle = index < 2 ? '#e8eef1' : '#45c7ff'; context.fillText(label, 405, y);
      context.fillStyle = '#e8eef1'; context.fillText(value, 565, y, 370);
    });
    ['#151c24', '#ff6273', '#55f49a', '#ffdc65', '#56c6ff', '#cb83ff', '#4fdac7', '#eef4f6'].forEach((color, index) => {
      context.fillStyle = color; context.fillRect(405 + index * 29, 512, 29, 24);
    });
    context.fillStyle = '#43f598'; context.fillText('(psykr@fedora)  › ▌', 30, 555);
    texture.needsUpdate = true;
  };
  portrait.onload = () => { draw(); render(); };
  portrait.src = '/chilchuck.png';
  draw();
  return texture;
}

// The laptop repeats the same greeting as the opening screen.
function makeLaptopWelcomeTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 960; canvas.height = 600;
  const context = canvas.getContext('2d');
  const texture = sharpenTexture(new THREE.CanvasTexture(canvas));
  if (!context) return texture;
  const lines = ["Hi, I'm Om Anand.", 'Welcome to my workspace.'];
  const glyphs = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz*+?{}#$%&/!';
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const draw = (elapsed: number) => {
    const time = reducedMotion ? 4000 : elapsed % 6000;
    context.fillStyle = '#000'; context.fillRect(0, 0, canvas.width, canvas.height);
    context.font = 'bold 42px monospace'; context.textAlign = 'center'; context.textBaseline = 'middle';
    context.fillStyle = '#ededed';
    context.globalAlpha = time > 4650 ? Math.max(0, 1 - (time - 4650) / 550) : 1;
    lines.forEach((line, index) => {
      const start = index === 0 ? 0 : 1600;
      const duration = index === 0 ? 1400 : 1800;
      const progress = Math.max(0, Math.min(1, (time - start) / duration));
      const position = progress * (line.length + 3);
      const visible = Math.min(line.length, Math.floor(position));
      const settled = Math.max(0, Math.floor(position) - 3);
      let text = Array.from(line.slice(0, visible), (char, i) =>
        char === ' ' || i < settled ? char : glyphs[Math.floor(Math.random() * glyphs.length)]
      ).join('');
      const typing = index === 0 ? time < 1400 : time >= 1600 && time < 3400;
      if (!reducedMotion && typing && Math.floor(time / 325) % 2 === 0) text += '▌';
      context.fillText(text, canvas.width / 2, 265 + index * 70, 880);
    });
    context.globalAlpha = 1;
    texture.needsUpdate = true;
  };
  draw(0);
  if (!reducedMotion) {
    const started = performance.now();
    window.setInterval(() => {
      if (document.visibilityState !== 'visible') return;
      draw(performance.now() - started);
      render();
    }, 125);
  }
  return texture;
}

function makeNightWindowTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 768;
  const context = canvas.getContext('2d');
  if (!context) return new THREE.CanvasTexture(canvas);

  const sky = context.createLinearGradient(0, 0, 0, canvas.height);
  sky.addColorStop(0, '#020611');
  sky.addColorStop(0.58, '#07152d');
  sky.addColorStop(1, '#10264a');
  context.fillStyle = sky;
  context.fillRect(0, 0, canvas.width, canvas.height);

  const stars = [
    [54, 96, 2], [113, 174, 1], [186, 72, 1.5], [265, 138, 2],
    [337, 64, 1], [424, 190, 1.5], [471, 104, 1], [81, 286, 1],
    [219, 252, 1.5], [389, 318, 1], [458, 264, 2], [302, 356, 1],
  ];
  context.fillStyle = '#d8e8ff';
  for (const [x, y, radius] of stars) {
    context.beginPath();
    context.arc(x, y, radius, 0, Math.PI * 2);
    context.fill();
  }

  context.fillStyle = '#030712';
  context.fillRect(0, 560, 512, 208);
  const buildings = [
    [0, 470, 92], [78, 520, 118], [181, 448, 92], [260, 505, 112],
    [361, 430, 96], [445, 490, 80],
  ];
  for (const [x, y, width] of buildings) {
    context.fillRect(x, y, width, 768 - y);
  }
  context.fillStyle = '#d9a85f';
  for (let y = 500; y < 720; y += 44) {
    for (let x = 22; x < 500; x += 58) {
      if ((x + y) % 3 !== 0) context.fillRect(x, y, 7, 4);
    }
  }

  return sharpenTexture(new THREE.CanvasTexture(canvas));
}

function makeNightRoomMaterial(map: THREE.Texture | null) {
  const material = new THREE.MeshStandardMaterial({
    map,
    color: '#ffffff',
    roughness: 0.9,
    metalness: 0,
    side: THREE.DoubleSide,
  });

  material.onBeforeCompile = (shader) => {
    shader.vertexShader = `varying vec3 vNightWorldPosition;\n${shader.vertexShader}`;
    shader.vertexShader = shader.vertexShader.replace(
      '#include <project_vertex>',
      `#include <project_vertex>
      vNightWorldPosition = (modelMatrix * vec4(transformed, 1.0)).xyz;`,
    );
    shader.fragmentShader = `varying vec3 vNightWorldPosition;\n${shader.fragmentShader}`;
    shader.fragmentShader = shader.fragmentShader.replace(
      '#include <map_fragment>',
      `#include <map_fragment>
      float bakedLuminance = dot(diffuseColor.rgb, vec3(0.2126, 0.7152, 0.0722));
      float nightLuminance = mix(
        bakedLuminance,
        0.36,
        smoothstep(0.16, 0.72, bakedLuminance)
      );
      vec3 bakedChroma = diffuseColor.rgb / max(bakedLuminance, 0.001);
      diffuseColor.rgb = mix(
        vec3(nightLuminance),
        bakedChroma * nightLuminance,
        0.4
      ) * vec3(0.74, 0.83, 1.0);

      // Keep the lounge side darker than the desk and feather the shadow away
      // from the night window, giving the sofa a believable moonlit silhouette.
      vec2 sofaShadowDelta = (vNightWorldPosition.xz - vec2(-1.75, 2.75))
        / vec2(3.15, 2.20);
      float sofaShadowArea = 1.0 - smoothstep(0.52, 1.22, length(sofaShadowDelta));
      float floorSurfaceMask = 1.0 - smoothstep(0.28, 0.68, vNightWorldPosition.y);
      vec2 fromWindow = normalize(vec2(-6.35, 4.77));
      float windowDirection = dot(
        normalize(vNightWorldPosition.xz - vec2(4.60, -2.02) + vec2(0.001)),
        fromWindow
      );
      float directedShadow = sofaShadowArea * floorSurfaceMask
        * smoothstep(0.62, 0.98, windowDirection);
      diffuseColor.rgb *= mix(
        vec3(1.0),
        vec3(0.48, 0.55, 0.72),
        directedShadow * 0.66
      );`,
    );
  };
  material.customProgramCacheKey = () => 'night-room-v4-clean-source-walls';
  return material;
}

function makeLinkedInTexture() {
  const canvas = document.createElement('canvas');
  canvas.width = 512;
  canvas.height = 512;
  const context = canvas.getContext('2d');
  if (!context) return new THREE.CanvasTexture(canvas);

  context.fillStyle = '#0a66c2';
  context.fillRect(0, 0, canvas.width, canvas.height);
  const glow = context.createRadialGradient(150, 110, 20, 180, 160, 390);
  glow.addColorStop(0, '#55a8ecaa');
  glow.addColorStop(1, '#07549c00');
  context.fillStyle = glow;
  context.fillRect(0, 0, canvas.width, canvas.height);
  context.fillStyle = '#ffffff';
  context.font = '700 250px Arial, Helvetica, sans-serif';
  context.textAlign = 'center';
  context.textBaseline = 'middle';
  context.fillText('in', 256, 280);

  return sharpenTexture(new THREE.CanvasTexture(canvas));
}

function createLinkedInCube() {
  const root = new THREE.Group();
  root.name = 'LinkedIn_Profile_Cube';
  const cube = new THREE.Mesh(
    new THREE.BoxGeometry(0.3, 0.3, 0.3),
    new THREE.MeshStandardMaterial({
      map: makeLinkedInTexture(),
      color: '#ffffff',
      roughness: 0.3,
      metalness: 0.08,
    }),
  );
  cube.castShadow = true;
  cube.receiveShadow = true;
  cube.rotation.set(0.04, -0.28, -0.025);
  root.add(cube);
  root.position.set(-1.34, 2.47, -4.36);
  return root;
}

function drawContributionPanel(
  context: CanvasRenderingContext2D,
  contributions: GitHubContribution[] = [],
  state: 'loading' | 'unavailable' = 'loading',
) {
  const { width, height } = context.canvas;
  context.clearRect(0, 0, width, height);
  const background = context.createLinearGradient(0, 0, width, height);
  background.addColorStop(0, '#0d1117');
  background.addColorStop(1, '#121b27');
  context.fillStyle = background;
  context.fillRect(0, 0, width, height);

  context.fillStyle = '#f0f6fc';
  context.font = '700 38px Arial, Helvetica, sans-serif';
  context.textAlign = 'left';
  context.textBaseline = 'alphabetic';
  context.fillText('GITHUB / CONTRIBUTIONS', 58, 66);
  context.fillStyle = '#8b949e';
  context.font = '21px monospace';
  const total = contributions.reduce((sum, item) => sum + item.count, 0);
  context.fillText(
    contributions.length > 0
      ? `${total.toLocaleString()} contributions in the last year`
      : state === 'loading' ? 'LOADING CONTRIBUTIONS…' : 'CONTRIBUTIONS UNAVAILABLE',
    59,
    104,
  );

  const columns = 53;
  const rows = 7;
  const gap = 7;
  const cell = 13;
  const gridWidth = columns * cell + (columns - 1) * gap;
  const startX = Math.round((width - gridWidth) / 2);
  const startY = 142;
  const greens = ['#202a35', '#0e4429', '#006d32', '#26a641', '#39d353'];
  const latest = contributions.slice(-columns * rows);

  for (let column = 0; column < columns; column += 1) {
    for (let row = 0; row < rows; row += 1) {
      const sourceIndex = column * rows + row;
      const contribution = latest[sourceIndex];
      const level = contribution ? THREE.MathUtils.clamp(contribution.level, 0, 4) : 0;
      context.fillStyle = greens[level];
      context.fillRect(
        startX + column * (cell + gap),
        startY + row * (cell + gap),
        cell,
        cell,
      );
    }
  }

  context.fillStyle = '#6e7681';
  context.font = '17px monospace';
  context.fillText('LESS', width - 235, height - 32);
  greens.forEach((color, index) => {
    context.fillStyle = color;
    context.fillRect(width - 172 + index * 25, height - 48, 17, 17);
  });
  context.fillStyle = '#6e7681';
  context.fillText('MORE', width - 38, height - 32);
}

function createGitHubPanel() {
  const root = new THREE.Group();
  root.name = 'GitHub_Contribution_Panel';

  const canvas = document.createElement('canvas');
  canvas.width = 1120;
  canvas.height = 360;
  const context = canvas.getContext('2d');
  if (!context) return { root, texture: new THREE.CanvasTexture(canvas), context: null };
  drawContributionPanel(context);
  const texture = sharpenTexture(new THREE.CanvasTexture(canvas));

  const frame = new THREE.Mesh(
    new THREE.BoxGeometry(3.42, 1.28, 0.11),
    new THREE.MeshStandardMaterial({
      color: '#151b23',
      roughness: 0.48,
      metalness: 0.22,
    }),
  );
  frame.castShadow = true;
  frame.receiveShadow = true;
  root.add(frame);

  const display = new THREE.Mesh(
    new THREE.PlaneGeometry(3.26, 1.05),
    new THREE.MeshBasicMaterial({ map: texture, toneMapped: false }),
  );
  display.position.z = 0.061;
  root.add(display);

  const accent = new THREE.Mesh(
    new THREE.BoxGeometry(3.27, 0.025, 0.025),
    new THREE.MeshStandardMaterial({
      color: '#39d353',
      emissive: '#1b7f35',
      emissiveIntensity: 1.25,
      roughness: 0.32,
    }),
  );
  accent.position.set(0, -0.59, 0.075);
  root.add(accent);
  root.position.set(0.12, 4.82, -5.18);
  return { root, texture, context };
}

function createAndroidMascot() {
  const root = new THREE.Group();
  root.name = 'Android_Mascot';
  // The desk surface at this location is y = 1.896.
  root.position.set(4.12, 1.90, -4.55);
  root.rotation.y = -Math.PI / 4;
  modelLoader.load('/android-bot-armory.glb', ({ scene: model }) => {
    improveTextureFiltering(model, renderer.capabilities.getMaxAnisotropy());
    const bounds = new THREE.Box3().setFromObject(model);
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    const scale = 1.35 / size.y;
    model.scale.setScalar(scale);
    model.position.set(-center.x * scale, -bounds.min.y * scale, -center.z * scale);
    model.traverse(object => { if (object instanceof THREE.Mesh) { object.castShadow = true; object.receiveShadow = true; } });
    root.add(model);
    render();
  }, undefined, error => console.warn('Could not load the Android mascot.', error));
  return root;
}

function createCodolioPanel() {
  const root = new THREE.Group(); root.name = 'Codolio_Profile_Panel';
  const canvas = document.createElement('canvas'); canvas.width = 512; canvas.height = 680;
  const ctx = canvas.getContext('2d');
  if (ctx) {
    ctx.fillStyle = '#111820'; ctx.fillRect(0, 0, 512, 680);
    ctx.textAlign = 'center';
    ctx.strokeStyle = '#46515d'; ctx.lineWidth = 3; ctx.strokeRect(26, 26, 460, 628);
    ctx.fillStyle = '#a7b7c6'; ctx.font = '24px monospace'; ctx.fillText('DEVELOPER PROFILE', 256, 82);
    ctx.fillStyle = '#f3a54a'; ctx.font = 'bold 100px monospace'; ctx.fillText('</>', 256, 270);
    ctx.fillStyle = '#f3f5f4'; ctx.font = 'bold 54px sans-serif'; ctx.fillText('CODOLIO', 256, 370);
    ctx.fillStyle = '#adbac5'; ctx.font = '26px monospace'; ctx.fillText('VISIT PROFILE  ↗', 256, 505);
    ctx.fillStyle = '#f3a54a'; ctx.fillRect(211, 565, 90, 6);
  }
  const frame = new THREE.Mesh(new THREE.BoxGeometry(1.12, 1.48, .08), new THREE.MeshStandardMaterial({ color: '#29272a', roughness: .6, metalness: .18 }));
  root.add(frame);
  const art = new THREE.Mesh(new THREE.PlaneGeometry(1.01, 1.36), new THREE.MeshBasicMaterial({ map: sharpenTexture(new THREE.CanvasTexture(canvas)), toneMapped: false }));
  art.position.z = .045; root.add(art);
  // Tuck the profile between the technology shelf and the workstation.
  root.position.set(-1.48, 3.55, -4.98);
  root.scale.setScalar(.42);
  return root;
}

function createDocumentPoster(image: string, position: THREE.Vector3, rotationY = 0) {
  const root = new THREE.Group();
  const frame = new THREE.Mesh(new THREE.BoxGeometry(1.12, 1.48, .08), new THREE.MeshStandardMaterial({ color: '#29272a', roughness: .6, metalness: .18 }));
  root.add(frame);
  const texture = new THREE.TextureLoader().load(image, render);
  sharpenTexture(texture);
  const art = new THREE.Mesh(new THREE.PlaneGeometry(1.01, 1.36), new THREE.MeshBasicMaterial({ map: texture, toneMapped: false }));
  art.position.z = .045; root.add(art);
  root.position.copy(position);
  root.rotation.y = rotationY;
  return root;
}

function registerInteractiveItem(
  root: THREE.Group,
  key: SocialKey,
  label: string,
  url: string,
  hoverScale = 1.04,
) {
  interactiveItems.push({
    root,
    key,
    label,
    url,
    baseScale: root.scale.x,
    hoverScale,
  });
  root.userData.socialKey = key;
  scene.add(root);
}

async function loadGitHubContributions(
  context: CanvasRenderingContext2D,
  texture: THREE.CanvasTexture,
) {
  const username = portfolioProfiles.githubUsername.trim();
  if (!username) return;
  try {
    const response = await fetch(
      `https://github-contributions-api.jogruber.de/v4/${encodeURIComponent(username)}?y=last`,
    );
    if (!response.ok) throw new Error(`GitHub contribution request failed: ${response.status}`);
    const data = await response.json() as { contributions?: GitHubContribution[] };
    if (!Array.isArray(data.contributions)) throw new Error('Invalid contribution response');
    drawContributionPanel(context, data.contributions);
    texture.needsUpdate = true;
    render();
  } catch (error) {
    console.warn('Could not update GitHub contributions.', error);
    drawContributionPanel(context, [], 'unavailable');
    texture.needsUpdate = true;
    render();
  }
}

function addSocialPortfolioProps() {
  const linkedInCube = createLinkedInCube();
  registerInteractiveItem(
    linkedInCube,
    'linkedin',
    'LinkedIn',
    portfolioProfiles.linkedinUrl,
  );

  const githubPanel = createGitHubPanel();
  registerInteractiveItem(
    githubPanel.root,
    'github',
    'GitHub',
    portfolioProfiles.githubUrl,
    1.025,
  );
  if (githubPanel.context) {
    void loadGitHubContributions(githubPanel.context, githubPanel.texture);
  }

  const android = createAndroidMascot();
  registerInteractiveItem(android, 'android', 'Android mascot', '', 1.025);
  const codolioPanel = createCodolioPanel();
  registerInteractiveItem(codolioPanel, 'codolio', 'Codolio', portfolioProfiles.codolioUrl, 1.025);

  registerInteractiveItem(createDocumentPoster('/documents/resume.png', new THREE.Vector3(3.0, 4.22, -5.02)), 'resume', 'résumé', 'https://drive.google.com/file/d/1wmCTUM8TiUqAmuWm9Iil6k9M4pjMhqV_/view?usp=sharing', 1.025);
  registerInteractiveItem(createDocumentPoster('/documents/experience-letter.png', new THREE.Vector3(4.41, 4.22, -3.9), -Math.PI / 2), 'experience', 'experience letter', 'https://drive.google.com/file/d/1ow50hpO_lmO-CUxZ7bJh7jIKkgfUUTzA/view?usp=sharing', 1.025);

}

// The original TV is baked into the room mesh. This thin screen sits on its
// front face and supplies both an invitation and a precise raycast target.
function addProjectTV() {
  const canvas = document.createElement('canvas');
  canvas.width = 1024;
  canvas.height = 576;
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  const texture = sharpenTexture(new THREE.CanvasTexture(canvas));
  const images = projects.map(project => {
    const image = new Image();
    image.src = project.cover;
    image.addEventListener('load', () => { drawScreen(0); render(); });
    return image;
  });
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const slideDuration = 5000;
  const drawScreen = (time: number) => {
    ctx.fillStyle = '#090909';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.textAlign = 'left';
    ctx.textBaseline = 'alphabetic';
    ctx.fillStyle = '#f5f5f5';
    ctx.font = 'bold 44px sans-serif';
    ctx.fillText('MY PROJECTS', 52, 76);
    const elapsed = reducedMotion ? 0 : time;
    const current = Math.floor(elapsed / slideDuration) % projects.length;
    const phase = elapsed % slideDuration;
    const step = Math.max(0, Math.min(1, (phase - 4100) / 900));
    const eased = step * step * (3 - 2 * step);
    const cardWidth = 600;
    const cardGap = 28;
    const x = 52 - eased * (cardWidth + cardGap);
    ctx.save();
    ctx.beginPath(); ctx.rect(0, 95, canvas.width, 480); ctx.clip();
    for (let offset = 0; offset < 3; offset++) {
      const index = (current + offset) % projects.length;
      const left = x + offset * (cardWidth + cardGap);
      ctx.fillStyle = '#222'; ctx.fillRect(left, 110, cardWidth, 370);
      const image = images[index];
      if (image.complete && image.naturalWidth) {
        const scale = Math.min(cardWidth / image.naturalWidth, 370 / image.naturalHeight);
        const width = image.naturalWidth * scale;
        const height = image.naturalHeight * scale;
        ctx.drawImage(image, left + (cardWidth - width) / 2, 110 + (370 - height) / 2, width, height);
      }
      const shade = ctx.createLinearGradient(0, 350, 0, 480);
      shade.addColorStop(0, '#0000'); shade.addColorStop(1, '#000e');
      ctx.fillStyle = shade; ctx.fillRect(left, 330, cardWidth, 150);
      ctx.fillStyle = '#fff'; ctx.font = 'bold 38px sans-serif';
      ctx.fillText(projects[index].title, left + 24, 448, cardWidth - 48);
    }
    ctx.restore();
    texture.needsUpdate = true;
  };
  drawScreen(0);
  if (!reducedMotion) {
    const started = performance.now();
    window.setInterval(() => {
      if (document.visibilityState !== 'visible') return;
      drawScreen(performance.now() - started);
      render();
    }, 125);
  }
  const root = new THREE.Group();
  const screen = new THREE.Mesh(
    new THREE.PlaneGeometry(4.20, 2.35),
    new THREE.MeshBasicMaterial({ map: texture, side: THREE.DoubleSide, toneMapped: false }),
  );
  screen.rotation.y = -Math.PI / 2;
  root.add(screen);
  root.position.set(4.19, 2.67, 1.82);
  registerInteractiveItem(root, 'projects', 'Projects', '', 1);
}

function showSocialHint(message: string) {
  if (!socialHint) return;
  window.clearTimeout(hintTimer);
  socialHint.textContent = message;
  socialHint.hidden = false;
  hintTimer = window.setTimeout(() => {
    socialHint.hidden = true;
  }, 2800);
}

function findInteractiveItem(object: THREE.Object3D | null) {
  let current = object;
  while (current) {
    const item = interactiveItems.find((candidate) => candidate.root === current);
    if (item) return item;
    current = current.parent;
  }
  return null;
}

type RoomHit = { item: InteractiveItem | null; label: string; screen?: 'monitor' | 'laptop' };

// The original furniture is baked into one mesh. Use the point actually hit
// on that mesh to identify the main areas, rather than invisible click boxes.
function bakedRoomLabel(point: THREE.Vector3, object: THREE.Object3D) {
  if (object.name.includes('Laptop_Screen')) return 'Laptop';
  if (object.name.includes('Monitor_Screen')) return 'Monitor';
  if (object.name.includes('Coffee_Steam')) return 'Coffee';
  if (point.y < 0.12) return 'Wood floor';
  if (point.y > 5.5 || point.z < -5.08 || point.x > 4.45) return 'Room';
  if (point.z < -3 && point.y < 2.15) return 'Workstation desk';
  if (point.z < -3 && point.y < 3.5) return 'Workstation';
  if (point.x > 1.8 && point.z > 0) return 'TV and media console';
  if (point.z > 0 && point.y < 2.2) return 'Sofa';
  return 'Room furnishing';
}

function pickRoomHit(event: PointerEvent): RoomHit | null {
  const bounds = renderer.domElement.getBoundingClientRect();
  pointer.x = ((event.clientX - bounds.left) / bounds.width) * 2 - 1;
  pointer.y = -((event.clientY - bounds.top) / bounds.height) * 2 + 1;
  raycaster.setFromCamera(pointer, camera);
  const intersections = raycaster.intersectObjects(scene.children, true);
  for (const intersection of intersections) {
    if (intersection.object.name.includes('Monitor_Screen_Dynamic')) return { item: null, label: 'Open terminal', screen: 'monitor' };
    if (intersection.object.name.includes('Laptop_Screen_Dynamic')) return { item: null, label: 'Play welcome', screen: 'laptop' };
    const item = findInteractiveItem(intersection.object);
    if (item) return { item, label: item.key === 'projects' ? 'Explore projects' : item.key === 'android' ? 'Android mascot' : item.key === 'resume' || item.key === 'experience' ? `Open ${item.label} ↗` : `Visit ${item.label} ↗` };
    let current: THREE.Object3D | null = intersection.object;
    while (current && current !== scene) {
      if (current === roomModel) return { item: null, label: bakedRoomLabel(intersection.point, intersection.object) };
      if (current.name === 'Technology display shelf' || current.name.endsWith(' symbol') ||
          current.name === 'Potted plant' || current.name === 'Vines and coloured string lights' ||
          current.name.endsWith(' developer poster') || current.name === 'Warm LED tube light') {
        return { item: null, label: current.name.replace('code developer poster', 'Developer poster').replace('terminal developer poster', 'Developer poster') };
      }
      current = current.parent;
    }
  }
  return null;
}

function setHoveredHit(hit: RoomHit | null) {
  const nextItem = hit?.item ?? null;
  const nextLabel = hit?.label ?? '';
  if (hoveredItem === nextItem && hoveredLabel === nextLabel) return;
  if (hoveredItem) hoveredItem.root.scale.setScalar(hoveredItem.baseScale);
  hoveredItem = nextItem;
  hoveredLabel = nextLabel;
  if (hoveredItem) hoveredItem.root.scale.setScalar(hoveredItem.baseScale * hoveredItem.hoverScale);
  viewport.classList.toggle('is-link-hovering', Boolean(hit?.screen || (hoveredItem && (hoveredItem.url || hoveredItem.key === 'projects'))));
  if (socialHint) {
    window.clearTimeout(hintTimer);
    socialHint.hidden = !nextLabel;
    socialHint.textContent = nextLabel;
  }
  render();
}

function addPendantBulb(position: THREE.Vector3, color: string, intensity: number) {
  const fixture = new THREE.Group();
  const cordLength = 0.72;
  const cord = new THREE.Mesh(
    new THREE.CylinderGeometry(0.015, 0.015, cordLength, 10),
    new THREE.MeshStandardMaterial({ color: '#19171a', roughness: 0.82 }),
  );
  cord.position.set(position.x, position.y + cordLength * 0.5 + 0.16, position.z);
  cord.castShadow = true;
  fixture.add(cord);

  const shade = new THREE.Mesh(
    new THREE.CylinderGeometry(0.12, 0.27, 0.22, 24, 1, true),
    new THREE.MeshStandardMaterial({
      color: '#33272a',
      roughness: 0.58,
      metalness: 0.18,
      side: THREE.DoubleSide,
    }),
  );
  shade.position.set(position.x, position.y + 0.12, position.z);
  shade.castShadow = true;
  fixture.add(shade);

  const bulb = new THREE.Mesh(
    new THREE.SphereGeometry(0.105, 24, 16),
    new THREE.MeshStandardMaterial({
      color: '#fff3d4',
      emissive: color,
      emissiveIntensity: 5,
      roughness: 0.2,
    }),
  );
  bulb.position.copy(position);
  fixture.add(bulb);

  const light = new THREE.PointLight(color, intensity, 14.5, 2);
  light.position.copy(position);
  light.castShadow = true;
  const shadowSize = window.matchMedia('(max-width: 720px)').matches ? 512 : 1024;
  light.shadow.mapSize.set(shadowSize, shadowSize);
  light.shadow.camera.near = 0.12;
  light.shadow.camera.far = 15;
  light.shadow.bias = -0.00035;
  light.shadow.normalBias = 0.025;
  light.shadow.radius = 4;
  fixture.add(light);

  scene.add(fixture);
}

modelLoader.load(
  '/room-sofa-shifted.glb?v=sofa-shift-2',
  ({ scene: model }) => {
    const monitorTexture = makeMonitorTexture();
    const laptopTexture = makeLaptopWelcomeTexture();

    model.traverse((object) => {
      if (object instanceof THREE.Mesh) {
        const sourceMaterial = Array.isArray(object.material)
          ? object.material[0]
          : object.material;
        const sourceName = sourceMaterial?.name ?? '';

        if (object.name.includes('Monitor_Screen_Dynamic') || sourceName.includes('WEB_Monitor_Screen')) {
          object.material = new THREE.MeshBasicMaterial({ map: monitorTexture, side: THREE.DoubleSide, toneMapped: false });
        } else if (object.name.includes('Laptop_Screen_Dynamic') || sourceName.includes('WEB_Laptop_Screen')) {
          object.material = new THREE.MeshBasicMaterial({ map: laptopTexture, side: THREE.DoubleSide, toneMapped: false });
        } else if (object.name.includes('Coffee_Steam')) {
          object.material = new THREE.MeshBasicMaterial({
            color: '#9a6b66',
            transparent: true,
            opacity: 0.22,
            depthWrite: false,
            side: THREE.DoubleSide,
          });
        } else if (sourceName.includes('SRC_Baked_Day')) {
          const source = sourceMaterial as THREE.MeshStandardMaterial;
          const map = source.map ?? source.emissiveMap;
          if (map) sharpenTexture(map);
          object.material = makeNightRoomMaterial(map);
          object.castShadow = true;
          object.receiveShadow = true;
        }
      }
    });
    scene.add(model);
    roomModel = model;
    addSocialPortfolioProps();
    addProjectTV();
    addTechShelf(scene, render, renderer.capabilities.getMaxAnisotropy());
    addGreenery(scene, modelLoader, render, renderer.capabilities.getMaxAnisotropy());
    addWallDecor(scene);

    const nightWindow = new THREE.Mesh(
      new THREE.PlaneGeometry(4.0, 4.8),
      new THREE.MeshBasicMaterial({
        map: makeNightWindowTexture(),
        side: THREE.DoubleSide,
        toneMapped: false,
      }),
    );
    // Set the sky behind the window frame and its railings.
    nightWindow.position.set(5.57, 3.18, -2.02);
    nightWindow.rotation.y = -Math.PI / 2;
    scene.add(nightWindow);

    scene.add(new THREE.AmbientLight('#ffe5cf', 2.8));
    scene.add(new THREE.HemisphereLight('#607bb2', '#6b4532', 2.2));

    const warmFill = new THREE.DirectionalLight('#ffd2a2', 1.0);
    warmFill.position.set(-5, 8, 6);
    scene.add(warmFill);

    const coolFill = new THREE.DirectionalLight('#9fbce8', 0.8);
    coolFill.position.set(6, 7, -5);
    scene.add(coolFill);
    const bounds = new THREE.Box3().setFromObject(model);
    const center = bounds.getCenter(new THREE.Vector3());
    const sphere = bounds.getBoundingSphere(new THREE.Sphere());
    const verticalFov = THREE.MathUtils.degToRad(camera.fov);
    const horizontalFov = 2 * Math.atan(Math.tan(verticalFov / 2) * camera.aspect);
    const limitingFov = Math.min(verticalFov, horizontalFov);
    const fitPadding = camera.aspect < 0.75 ? 1.05 : 0.82;
    const distance = Math.max(sphere.radius / Math.tan(limitingFov / 2) * fitPadding, 12);
    const viewDirection = new THREE.Vector3(-0.5, 0.29, 0.5).normalize();
    startTarget.copy(center);
    startPosition.copy(center).addScaledVector(viewDirection, distance);
    camera.position.copy(startPosition);
    controls.target.copy(startTarget);
    controls.minDistance = Math.max(6, distance * 0.35);
    controls.maxDistance = distance * 1.8;
    controls.update();
    render();
  },
  undefined,
  (error) => {
    console.error('Could not load the room model.', error);
    if (status) {
      const event = error as { message?: string; type?: string; target?: { constructor?: { name?: string }; status?: number; statusText?: string; responseURL?: string; readyState?: number } };
      const detail = error instanceof Error
        ? error.message
        : [event.message, event.type, event.target?.constructor?.name, `status ${event.target?.status}`, `ready ${event.target?.readyState}`, event.target?.responseURL].filter(Boolean).join(' ');
      status.textContent = `Room failed to load: ${detail}`;
      status.hidden = false;
    }
    window.dispatchEvent(new Event('room-ready'));
  },
);

function resize() {
  const { clientWidth, clientHeight } = viewport;
  if (!clientWidth || !clientHeight) return;
  camera.aspect = clientWidth / clientHeight;
  camera.updateProjectionMatrix();
  renderer.setPixelRatio(renderPixelRatio(clientWidth, clientHeight));
  renderer.setSize(clientWidth, clientHeight, false);
  render();
}

function render() {
  renderer.render(scene, camera);
}

controls.addEventListener('change', render);
new ResizeObserver(resize).observe(viewport);
resize();

renderer.domElement.addEventListener('pointermove', (event) => {
  if (socialHint) {
    socialHint.style.left = `${Math.min(event.clientX + 16, window.innerWidth - 160)}px`;
    socialHint.style.top = `${Math.min(event.clientY + 18, window.innerHeight - 50)}px`;
  }
  if (event.pointerType !== 'touch') setHoveredHit(pickRoomHit(event));
});

renderer.domElement.addEventListener('pointerleave', () => {
  setHoveredHit(null);
});

renderer.domElement.addEventListener('pointerdown', (event) => {
  if (event.button !== 0) return;
  pointerDownPosition = { x: event.clientX, y: event.clientY };
});

renderer.domElement.addEventListener('pointerup', (event) => {
  if (event.button !== 0 || !pointerDownPosition) return;
  const travel = Math.hypot(
    event.clientX - pointerDownPosition.x,
    event.clientY - pointerDownPosition.y,
  );
  pointerDownPosition = null;
  if (travel > 6) return;
  const hit = pickRoomHit(event);
  if (!hit) return;
  if (hit.screen) { window.dispatchEvent(new CustomEvent('open-room-screen', { detail: hit.screen })); return; }
  const item = hit.item;
  if (!item) { showSocialHint(hit.label); return; }
  if (item.key === 'projects') {
    window.dispatchEvent(new CustomEvent('open-projects'));
  } else if (item.key === 'android') {
    showSocialHint('Android mascot');
  } else if (item.url.trim()) {
    window.open(item.url, '_blank', 'noopener,noreferrer');
  } else {
    showSocialHint(`${item.label} will open here after you provide the account link.`);
  }
});

resetButton?.addEventListener('click', () => {
  camera.position.copy(startPosition);
  controls.target.copy(startTarget);
  controls.update();
});
