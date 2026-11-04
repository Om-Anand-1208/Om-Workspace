import * as THREE from 'three';
import type { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { improveTextureFiltering } from './render-quality';

export function addGreenery(scene: THREE.Scene, loader: GLTFLoader, render: () => void, maxAnisotropy: number) {
  const vine = new THREE.Group();
  vine.name = 'Vines and coloured string lights';
  const stemMaterial = new THREE.MeshStandardMaterial({ color: '#33582f', roughness: .9 });
  const bulbGeometry = new THREE.SphereGeometry(.052, 12, 8);
  const bulbs = ['#ff667f', '#7bd9ff', '#c99aff', '#ffcf70', '#8ee1aa'].map(color => new THREE.MeshBasicMaterial({ color, toneMapped: false }));
  // The two paths meet at the wall corner. Their gentle scallops keep the
  // garland clear of the screen, window and technology shelf.
  const points: THREE.Vector3[] = [];
  const segmentCount = 100;
  for (let i = 0; i <= segmentCount; i++) {
    const t = i / segmentCount;
    points.push(new THREE.Vector3(-4.75 + 9.15 * t, 5.81 - .11 * Math.abs(Math.sin(t * Math.PI * 4)), -5.08));
  }
  for (let i = 1; i <= segmentCount; i++) {
    const t = i / segmentCount;
    points.push(new THREE.Vector3(4.43, 5.81 - .11 * Math.abs(Math.sin(t * Math.PI * 4)), -5.08 + 9.1 * t));
  }
  const curve = new THREE.CatmullRomCurve3(points);
  const stem = new THREE.Mesh(new THREE.TubeGeometry(curve, 320, .017, 6, false), stemMaterial);
  vine.add(stem);
  // Reuse a textured leaf extracted from the same CC0 plant as the floor pots.
  loader.load('/vine-leaf.glb', ({ scene: leafModel }) => {
    improveTextureFiltering(leafModel, maxAnisotropy);
    let template: THREE.Mesh | undefined;
    leafModel.traverse(object => { if (object instanceof THREE.Mesh && !template) template = object; });
    if (!template) return;
    const leafTemplate = template as THREE.Mesh;
    const materials = Array.isArray(leafTemplate.material) ? leafTemplate.material : [leafTemplate.material];
    materials.forEach(material => { material.side = THREE.DoubleSide; });
    for (let i = 2; i < points.length - 2; i += 2) {
      const p = points[i];
      const side = Math.floor(i / 2) % 2 === 0 ? 1 : -1;
      const onBack = i <= segmentCount;
      const leaf = new THREE.Mesh(leafTemplate.geometry, leafTemplate.material);
      leaf.position.copy(p).add(new THREE.Vector3(onBack ? side * .08 : -.035, -.10, onBack ? .035 : side * .08));
      if (onBack) leaf.rotation.z = side * .68;
      else { leaf.rotation.y = -Math.PI / 2; leaf.rotation.z = side * .68; }
      vine.add(leaf);
    }
    render();
  }, undefined, error => console.warn('Could not load the vine leaf.', error));
  for (let i = 5; i < points.length; i += 10) {
    const p = points[i];
    const bulb = new THREE.Mesh(bulbGeometry, bulbs[Math.floor(i / 10) % bulbs.length]);
    bulb.position.copy(p).add(new THREE.Vector3(0, -.12, 0));
    vine.add(bulb);
  }
  for (const [index, color] of [[25, '#ff9bba'], [75, '#91baff'], [125, '#d0a0ff'], [175, '#ffc589']] as const) {
    const light = new THREE.PointLight(color, .45, 2.5, 2);
    light.position.copy(points[index]);
    vine.add(light);
  }
  scene.add(vine);

  // Reuse the CC0 plant model; scale and ground using its own bounds.
  loader.load('/potted-plant-web.glb', ({ scene: source }) => {
    improveTextureFiltering(source, maxAnisotropy);
    const bounds = new THREE.Box3().setFromObject(source);
    const size = bounds.getSize(new THREE.Vector3());
    const center = bounds.getCenter(new THREE.Vector3());
    const addPlant = (x: number, y: number, z: number, height: number, rotation: number) => {
      const plant = source.clone(true);
      const scale = height / size.y;
      plant.scale.setScalar(scale);
      plant.position.set(-center.x * scale, -bounds.min.y * scale, -center.z * scale);
      plant.traverse(object => { if (object instanceof THREE.Mesh) { object.castShadow = true; object.receiveShadow = true; } });
      // Layer the original textured foliage around the central stem for a fuller canopy.
      const foliage = plant.getObjectByName('potted_plant_01_leaves');
      if (foliage) {
        for (const angle of [2.1, 4.2]) {
          const extraLeaves = foliage.clone();
          extraLeaves.rotation.y += angle;
          extraLeaves.scale.multiplyScalar(.92);
          plant.add(extraLeaves);
        }
      }
      const anchor = new THREE.Group(); anchor.name = 'Potted plant'; anchor.position.set(x, y, z); anchor.rotation.y = rotation; anchor.add(plant); scene.add(anchor);
    };
    addPlant(-4.35, .06, -4.40, 1.55, -.35);
    render();
  }, undefined, error => console.warn('Could not load the plant model.', error));
  render();
}
