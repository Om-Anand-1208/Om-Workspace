import * as THREE from 'three';

// Keep high-density displays sharp while limiting the size of the WebGL buffer.
export function renderPixelRatio(width: number, height: number): number {
  const mobile = window.matchMedia('(max-width: 640px)').matches;
  const pixelBudget = mobile ? 4_000_000 : 8_000_000;
  const densityLimit = mobile ? 2 : 2.5;
  const budgetLimit = Math.sqrt(pixelBudget / Math.max(1, width * height));
  return Math.max(1, Math.min(Math.max(window.devicePixelRatio || 1, 1.25), densityLimit, budgetLimit));
}

// Sharpen textures seen at an angle without changing their color spaces.
export function improveTextureFiltering(root: THREE.Object3D, maxAnisotropy: number): void {
  const anisotropy = Math.min(maxAnisotropy, 8);
  root.traverse(object => {
    if (!(object instanceof THREE.Mesh)) return;
    const materials = Array.isArray(object.material) ? object.material : [object.material];
    for (const material of materials) {
      for (const value of Object.values(material)) {
        if (value instanceof THREE.Texture) {
          value.anisotropy = anisotropy;
          value.needsUpdate = true;
        }
      }
    }
  });
}
