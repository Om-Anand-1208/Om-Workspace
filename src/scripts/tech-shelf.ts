import * as THREE from 'three';
import { SVGLoader } from 'three/addons/loaders/SVGLoader.js';

// Each plaque is a small 3D object; symbols come from Simple Icons and Devicon (Java).
// These are the distinct technologies identified in the portfolio and project READMEs.
const technologies = [
  ['java', '#b74735'], ['git', '#f05234'], ['github', '#37383b'], ['javascript', '#d4b939'], ['typescript', '#3178c6'], ['html5', '#e65b30'], ['css', '#286bd1'],
  ['python', '#3775a7'], ['kotlin', '#8654d8'], ['android', '#42a968'], ['jetpackcompose', '#367ee6'], ['ktor', '#326bb2'], ['gradle', '#27484c'],
  ['astro', '#d66840'], ['threedotjs', '#565b61'], ['babylondotjs', '#bb4855'], ['webgl', '#936067'], ['vite', '#8e5bd0'], ['blender', '#db7d36'],
  ['streamlit', '#db5860'], ['pandas', '#505084'], ['numpy', '#4f84b1'], ['scikitlearn', '#d78b45'], ['firebase', '#d5a52d'], ['redis', '#bb514b'],
  ['docker', '#378ac4'], ['vercel', '#444449'],
  ['matplotlib', '#53839d'], ['seaborn', '#537b94'], ['joblib', '#7c6d91'],
] as const;

export function addTechShelf(scene: THREE.Scene, render: () => void, maxAnisotropy: number) {
  const shelf = new THREE.Group();
  shelf.name = 'Technology display shelf';
  // Mounted on the desk-side wall, in the empty area beside the workstation.
  shelf.position.set(-3.42, 3.95, -5.03);
  const textures = new THREE.TextureLoader();
  const woodMap = textures.load('/textures/oak-veneer-color.jpg', render);
  woodMap.colorSpace = THREE.SRGBColorSpace;
  woodMap.anisotropy = maxAnisotropy;
  const woodNormal = textures.load('/textures/oak-veneer-normal.jpg', render);
  woodNormal.anisotropy = maxAnisotropy;
  const wood = new THREE.MeshStandardMaterial({ map: woodMap, normalMap: woodNormal, normalScale: new THREE.Vector2(.28, .28), color: '#f4e1d6', roughness: .72 });
  const woodDark = new THREE.MeshStandardMaterial({ map: woodMap, normalMap: woodNormal, normalScale: new THREE.Vector2(.2, .2), color: '#dbc3b6', roughness: .78 });
  const ivory = new THREE.MeshStandardMaterial({ color: '#f5f5ed', metalness: .35, roughness: .28, side: THREE.DoubleSide });
  const badgeRim = new THREE.MeshStandardMaterial({ color: '#b7b5b1', metalness: .78, roughness: .3 });
  const panel = (w: number, h: number, d: number, x: number, y: number, z: number, material = wood) => {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), material);
    mesh.position.set(x, y, z); mesh.castShadow = true; mesh.receiveShadow = true; shelf.add(mesh);
  };
  const width = 2.55, height = 2.75, depth = .34;
  panel(width, height, .075, 0, 0, -.14, woodDark);
  panel(.09, height, depth, -width / 2, 0, 0);
  panel(.09, height, depth, width / 2, 0, 0);
  for (let i = 0; i <= 5; i++) panel(width, .075, depth, 0, -height / 2 + i * (height / 5), 0);
  scene.add(shelf);
  const loader = new SVGLoader();
  technologies.forEach(([name, color], index) => {
    const col = index % 6, row = Math.floor(index / 6);
    const x = -1.02 + col * .408;
    const y = height / 2 - .30 - row * (height / 5);
    const badge = new THREE.Group();
    badge.position.set(x, y, .07);
    badge.name = `${name} symbol`;
    const back = new THREE.Mesh(new THREE.CylinderGeometry(.155, .155, .06, 32), new THREE.MeshStandardMaterial({ color, metalness: .45, roughness: .32 }));
    back.rotation.x = Math.PI / 2;
    badge.add(back);
    const rim = new THREE.Mesh(new THREE.TorusGeometry(.151, .009, 6, 32), badgeRim);
    rim.position.z = .032; badge.add(rim);
    shelf.add(badge);
    const displayNames: Record<string, string> = {
      java:'Java', git:'Git', github:'GitHub', javascript:'JavaScript', typescript:'TypeScript', html5:'HTML5', css:'CSS',
      python:'Python', kotlin:'Kotlin', android:'Android', jetpackcompose:'Compose', ktor:'Ktor', gradle:'Gradle',
      astro:'Astro', threedotjs:'Three.js', babylondotjs:'Babylon.js', webgl:'WebGL', vite:'Vite', blender:'Blender',
      streamlit:'Streamlit', pandas:'pandas', numpy:'NumPy', scikitlearn:'scikit-learn', firebase:'Firebase', redis:'Redis',
      docker:'Docker', vercel:'Vercel', matplotlib:'Matplotlib', seaborn:'Seaborn', joblib:'joblib',
    };
    badge.name = `${displayNames[name] || name} symbol`;
    const labelCanvas = document.createElement('canvas'); labelCanvas.width = 256; labelCanvas.height = 64;
    const labelContext = labelCanvas.getContext('2d');
    if (labelContext) {
      labelContext.fillStyle = '#3d2c24'; labelContext.fillRect(0, 0, 256, 64);
      labelContext.fillStyle = '#fff4df'; labelContext.textAlign = 'center'; labelContext.textBaseline = 'middle';
      labelContext.font = '600 36px sans-serif'; labelContext.fillText(displayNames[name] || name, 128, 34, 240);
      const labelTexture = new THREE.CanvasTexture(labelCanvas); labelTexture.colorSpace = THREE.SRGBColorSpace;
      const nameplate = new THREE.Mesh(new THREE.PlaneGeometry(.36, .09), new THREE.MeshBasicMaterial({ map: labelTexture, toneMapped: false }));
      nameplate.position.set(0, -.218, .105); badge.add(nameplate);
    }
    const textLabels: Record<string, string> = { matplotlib: 'MPL', seaborn: 'SNS', joblib: 'JOB' };
    if (textLabels[name]) {
      const canvas = document.createElement('canvas'); canvas.width = 128; canvas.height = 128;
      const context = canvas.getContext('2d');
      if (context) {
        context.fillStyle = '#fff7e9'; context.textAlign = 'center'; context.textBaseline = 'middle';
        context.font = 'bold 43px sans-serif'; context.fillText(textLabels[name], 64, 67);
        const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace;
        const label = new THREE.Mesh(new THREE.PlaneGeometry(.25, .25), new THREE.MeshBasicMaterial({ map: texture, transparent: true, depthWrite: false }));
        label.position.z = .038; badge.add(label);
      }
      return;
    }
    loader.load(`/tech-icons/${name}.svg`, data => {
      const icon = new THREE.Group();
      icon.position.set(-.113, .113, .038);
      icon.scale.set(.0094, -.0094, .0094);
      for (const path of data.paths) {
        for (const shape of path.toShapes()) {
          const geometry = new THREE.ExtrudeGeometry(shape, { depth: 1.2, bevelEnabled: false, curveSegments: 6 });
          icon.add(new THREE.Mesh(geometry, ivory));
        }
      }
      badge.add(icon);
      render();
    }, undefined, () => console.warn(`Could not load the ${name} icon.`));
  });
  render();
}
