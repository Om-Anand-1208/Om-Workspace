import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { improveTextureFiltering, renderPixelRatio } from './render-quality';
const holder = document.querySelector<HTMLElement>('#project-model');
if (holder?.dataset.model) {
  try {
    const scene = new THREE.Scene();
    const isFlood = holder.dataset.model.includes('Flood-Monitoring-System');
    // Match the orthographic cameras used for the Blender catalogue renders.
    const viewWidth = isFlood ? 6.7 : 6;
    const camera = new THREE.OrthographicCamera(-viewWidth / 2, viewWidth / 2, 3, -3, .1, 100);
    camera.position.set(isFlood ? 6 : 7, isFlood ? 6 : 7, isFlood ? 8 : 9);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, isFlood ? .8 : 1.1, 0);
    controls.enablePan = false;
    controls.enableZoom = false;
    controls.maxPolarAngle = Math.PI / 2;
    controls.update();
    scene.add(new THREE.HemisphereLight('#fff1dc', '#6a7a75', 1.65));
    const addLight = (color: string, intensity: number, x: number, y: number, z: number, shadows = false) => {
      const light = new THREE.DirectionalLight(color, intensity);
      light.position.set(x, y, z);
      if (shadows) {
        light.castShadow = true;
        const shadowSize = window.matchMedia('(max-width: 640px)').matches ? 1024 : 2048;
        light.shadow.mapSize.set(shadowSize, shadowSize);
        Object.assign(light.shadow.camera, { left: -5, right: 5, top: 5, bottom: -5, near: .1, far: 30 });
        light.shadow.bias = -.0002;
        light.shadow.normalBias = .025;
        light.shadow.radius = 3;
      }
      scene.add(light);
    };
    addLight('#ffdbb5', 2, 1, 7, 4, true);
    addLight('#c9ddff', 1.15, -4, 5, 0);
    addLight('#ffe1bd', 1, 2, 5, -4);
    const render = () => renderer.render(scene, camera);
    controls.addEventListener('change', render);
    const loader = new GLTFLoader();
    const draco = new DRACOLoader(); draco.setDecoderPath('/draco/'); loader.setDRACOLoader(draco);
    loader.load(holder.dataset.model, gltf => {
      improveTextureFiltering(gltf.scene, renderer.capabilities.getMaxAnisotropy());
      gltf.scene.traverse(object => {
        if (object instanceof THREE.Mesh) { object.castShadow = true; object.receiveShadow = true; }
      });
      scene.add(gltf.scene);
      holder.replaceChildren(renderer.domElement);
      resize();
    }, undefined, () => {});
    function resize() {
      if (!holder) return;
      const aspect = holder.clientWidth / holder.clientHeight;
      if (!aspect) return;
      const width = Math.max(viewWidth, viewWidth * aspect / (4 / 3));
      const height = width / aspect;
      camera.left = -width / 2; camera.right = width / 2;
      camera.top = height / 2; camera.bottom = -height / 2;
      camera.updateProjectionMatrix();
      renderer.setPixelRatio(renderPixelRatio(holder.clientWidth, holder.clientHeight));
      renderer.setSize(holder.clientWidth, holder.clientHeight, false); render();
    }
    new ResizeObserver(resize).observe(holder);
  } catch { /* The snapshot remains available when WebGL is unavailable. */ }
}
const history = document.querySelector<HTMLElement>('#history');
if (history) {
  fetch(`https://api.github.com/repos/${encodeURIComponent(history.dataset.owner || "Om-Anand-1208")}/${encodeURIComponent(history.dataset.repo!)}/commits?per_page=6`)
    .then(response => { if (!response.ok) throw new Error(); return response.json(); })
    .then((commits: {sha:string; html_url:string; commit:{message:string; author:{date:string}}}[]) => {
      history.replaceChildren();
      if (!commits.length) { history.textContent = 'No commits available.'; return; }
      commits.forEach(commit => { const a = document.createElement('a'); a.className='history-row'; a.href=commit.html_url; a.target='_blank'; a.rel='noopener noreferrer'; const date=document.createElement('span'); date.className='history-date'; date.textContent=new Intl.DateTimeFormat('en',{day:'2-digit',month:'short',year:'numeric',timeZone:'UTC'}).format(new Date(commit.commit.author.date)); const message=document.createElement('span'); message.textContent=commit.commit.message.split('\n')[0]; const hash=document.createElement('code'); hash.textContent=commit.sha.slice(0,7); a.append(date,message,hash); history.append(a); });
    }).catch(() => { history.textContent = 'Activity is unavailable right now. View the full history on GitHub.'; });
}
