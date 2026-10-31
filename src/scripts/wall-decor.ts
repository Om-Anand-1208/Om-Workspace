import * as THREE from 'three';

type Wall = 'white' | 'blue';

export function addWallDecor(scene: THREE.Scene) {
  const frameMaterial = new THREE.MeshStandardMaterial({ color: '#29272a', roughness: .6, metalness: .18 });
  const housingMaterial = new THREE.MeshStandardMaterial({ color: '#303135', roughness: .38, metalness: .65 });
  const tubeMaterial = new THREE.MeshBasicMaterial({ color: '#ffe3ac', toneMapped: false });

  function posterTexture(style: 'code' | 'terminal') {
    const canvas = document.createElement('canvas'); canvas.width = 512; canvas.height = 680;
    const ctx = canvas.getContext('2d');
    if (!ctx) return new THREE.CanvasTexture(canvas);
    ctx.fillStyle = style === 'code' ? '#ebe7dd' : '#101820'; ctx.fillRect(0, 0, 512, 680);
    if (style === 'code') {
      ctx.fillStyle = '#555e60'; ctx.font = 'bold 24px monospace'; ctx.fillText('THE DEVELOPMENT PROCESS', 36, 68);
      ctx.fillStyle = '#192a2b'; ctx.font = 'bold 66px sans-serif';
      ctx.fillText('BUILD.', 36, 213); ctx.fillText('BREAK.', 36, 308); ctx.fillText('LEARN.', 36, 403);
      ctx.fillStyle = '#43867c'; ctx.fillRect(36, 445, 125, 8);
      ctx.fillStyle = '#66706f'; ctx.font = '24px monospace'; ctx.fillText('// repeat', 36, 508);
      ctx.font = '20px monospace'; ctx.fillText('ONE IDEA AT A TIME', 36, 625);
    } else {
      ctx.fillStyle = '#719392'; ctx.font = '23px monospace'; ctx.fillText('~/workspace', 34, 61);
      ctx.strokeStyle = '#30484c'; ctx.lineWidth = 3; ctx.strokeRect(27, 27, 458, 626);
      ctx.fillStyle = '#a9c8c1'; ctx.font = 'bold 48px monospace'; ctx.fillText('> create_', 34, 215);
      ctx.fillStyle = '#6aa69a'; ctx.font = '27px monospace'; ctx.fillText('const idea = {', 34, 304);
      ctx.fillStyle = '#d8ded8'; ctx.fillText('  build: true,', 34, 354); ctx.fillText('  learn: true', 34, 404);
      ctx.fillStyle = '#6aa69a'; ctx.fillText('};', 34, 454);
      ctx.fillStyle = '#73918e'; ctx.font = '20px monospace'; ctx.fillText('KEEP CREATING', 34, 594);
    }
    const texture = new THREE.CanvasTexture(canvas); texture.colorSpace = THREE.SRGBColorSpace; texture.anisotropy = 4; return texture;
  }
  function wallGroup(wall: Wall, along: number, y: number) {
    const group = new THREE.Group();
    if (wall === 'white') group.position.set(along, y, -5.02);
    else { group.position.set(4.41, y, along); group.rotation.y = -Math.PI / 2; }
    scene.add(group); return group;
  }
  function addPoster(wall: Wall, along: number, y: number, style: 'code' | 'terminal') {
    const group = wallGroup(wall, along, y);
    group.name = `${style} developer poster`;
    const frame = new THREE.Mesh(new THREE.BoxGeometry(1.12, 1.48, .08), frameMaterial);
    group.add(frame);
    const art = new THREE.Mesh(new THREE.PlaneGeometry(1.01, 1.36), new THREE.MeshBasicMaterial({ map: posterTexture(style), toneMapped: false }));
    art.position.z = .045; group.add(art);
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
  addPoster('blue', -3.9, 4.22, 'code');
  addTubeLight('white', 3.0, 5.18);
  addTubeLight('blue', -3.9, 5.18);
  addTubeLight('blue', 1.9, 4.82);
}
