import * as THREE from 'three';

type Wall = 'white' | 'blue';

export function addWallDecor(scene: THREE.Scene) {
  const housingMaterial = new THREE.MeshStandardMaterial({ color: '#303135', roughness: .38, metalness: .65 });
  const tubeMaterial = new THREE.MeshBasicMaterial({ color: '#ffe3ac', toneMapped: false });

  function wallGroup(wall: Wall, along: number, y: number) {
    const group = new THREE.Group();
    if (wall === 'white') group.position.set(along, y, -5.02);
    else { group.position.set(4.41, y, along); group.rotation.y = -Math.PI / 2; }
    scene.add(group); return group;
  }
  function addTubeLight(wall: Wall, along: number, y: number) {
    const group = wallGroup(wall, along, y);
    group.name = 'Warm LED tube light';
    const mount = new THREE.Mesh(new THREE.BoxGeometry(.78, .095, .08), housingMaterial);
    mount.position.z = .065; group.add(mount);
    const tube = new THREE.Mesh(new THREE.CapsuleGeometry(.033, .62, 4, 12), tubeMaterial);
    tube.rotation.z = Math.PI / 2; tube.position.z = .12; group.add(tube);
    const light = new THREE.PointLight('#ffd39d', .8, 2.2, 2);
    light.position.set(0, -.08, .28); group.add(light);
  }
  addTubeLight('white', 3.0, 5.18);
  addTubeLight('blue', -3.9, 5.18);
  addTubeLight('blue', 1.9, 4.82);
}
