import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
const holder = document.querySelector<HTMLElement>('#project-model');
if (holder) {
  try {
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, .1, 100);
    camera.position.set(7, 6, 7);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(devicePixelRatio, 1.5)); renderer.outputColorSpace = THREE.SRGBColorSpace;
    const controls = new OrbitControls(camera, renderer.domElement); controls.target.set(0, .7, 0); controls.enablePan = false; controls.enableZoom = false; controls.maxPolarAngle = Math.PI / 2; controls.update();
    scene.add(new THREE.HemisphereLight(0xffffff, 0x526c68, 2.2)); const light = new THREE.DirectionalLight(0xffffff, 2); light.position.set(5, 8, 5); scene.add(light);
    const render = () => renderer.render(scene, camera);
    controls.addEventListener('change', render);
    const loader = new GLTFLoader();
    const draco = new DRACOLoader(); draco.setDecoderPath('/draco/'); loader.setDRACOLoader(draco);
    loader.load(holder.dataset.model!, gltf => {
      if (holder.dataset.model?.includes('original-room')) {
        const bounds = new THREE.Box3().setFromObject(gltf.scene);
        const size = bounds.getSize(new THREE.Vector3());
        const center = bounds.getCenter(new THREE.Vector3());
        const scale = 4.2 / Math.max(size.x, size.y, size.z);
        gltf.scene.scale.setScalar(scale); gltf.scene.position.copy(center).multiplyScalar(-scale);
        camera.position.set(-7, 5, 7); controls.target.set(0, 0, 0); controls.update();
      }
      scene.add(gltf.scene); holder.replaceChildren(renderer.domElement); resize();
    }, undefined, () => {});
    function resize() { if (!holder) return; camera.aspect = holder.clientWidth / holder.clientHeight; camera.updateProjectionMatrix(); renderer.setSize(holder.clientWidth, holder.clientHeight, false); render(); }
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
