---
name: webgl-threejs-creative-dev
description: Interactive 3D web experiences, WebGL canvases, Three.js, and React Three Fiber (R3F) (inspired by freshtechbro/claudedesignskills 3D & WebGL bundle and SOTA creative dev). Covers scene composition, smooth lerped camera parallax, GLTF/GLB loading with DRACO compression, custom GLSL vertex/fragment shaders, post-processing pipelines, and 60fps mobile performance budgets.
---

# WebGL, Three.js & Creative 3D Web Development

A comprehensive creative development guide for building interactive 3D web applications, WebGL visualizers, and hero landing pages using Three.js and React Three Fiber (R3F).

## 1. Scene Setup & Camera Parallax

Set up performant, responsive Three.js rendering loops with smooth cursor parallax:

```javascript
import * as THREE from 'three';

export class Interactive3DScene {
  constructor(canvas) {
    this.canvas = canvas;
    this.scene = new THREE.Scene();
    
    // Camera: 45 deg FOV, calibrated near/far planes
    this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
    this.camera.position.set(0, 0, 5);

    // Renderer with power preference & pixel ratio cap (vital for mobile 60fps)
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.0;

    // Mouse Parallax Targets
    this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
    window.addEventListener('mousemove', (e) => this.onMouseMove(e));
    window.addEventListener('resize', () => this.onResize());

    this.initLights();
    this.animate = this.animate.bind(this);
    requestAnimationFrame(this.animate);
  }

  onMouseMove(e) {
    this.mouse.targetX = (e.clientX / window.innerWidth) * 2 - 1;
    this.mouse.targetY = -(e.clientY / window.innerHeight) * 2 + 1;
  }

  onResize() {
    this.camera.aspect = window.innerWidth / window.innerHeight;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(window.innerWidth, window.innerHeight);
  }

  initLights() {
    const ambient = new THREE.AmbientLight(0xffffff, 0.4);
    const directional = new THREE.DirectionalLight(0xffeedd, 1.2);
    directional.position.set(5, 8, 4);
    this.scene.add(ambient, directional);
  }

  animate() {
    requestAnimationFrame(this.animate);

    // Smooth Lerp Camera Parallax
    this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.05;
    this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.05;
    this.camera.position.x = this.mouse.x * 0.6;
    this.camera.position.y = this.mouse.y * 0.4;
    this.camera.lookAt(0, 0, 0);

    this.renderer.render(this.scene, this.camera);
  }
}
```

---

## 2. React Three Fiber (R3F) Declarative Patterns

For modern Next.js / React ecosystems:

```tsx
import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Float, MeshDistortMaterial, Environment, OrbitControls } from '@react-three/drei';
import * as THREE from 'three';

function HeroOrb() {
  const meshRef = useRef<THREE.Mesh>(null!);

  useFrame((state, delta) => {
    meshRef.current.rotation.x += delta * 0.2;
    meshRef.current.rotation.y += delta * 0.25;
  });

  return (
    <Float speed={2} rotationIntensity={0.8} floatIntensity={1.2}>
      <mesh ref={meshRef} scale={1.8}>
        <sphereGeometry args={[1, 64, 64]} />
        <MeshDistortMaterial
          color="#f59e0b"
          roughness={0.15}
          metalness={0.8}
          distort={0.35}
          speed={2.2}
        />
      </mesh>
    </Float>
  );
}

export function HeroScene() {
  return (
    <div className="w-full h-[600px] relative">
      <Canvas camera={{ position: [0, 0, 4.5], fov: 45 }} gl={{ powerPreference: 'high-performance' }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1.5} />
        <HeroOrb />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}
```

---

## 3. Custom GLSL Shader Passes (Noise, Hologram, Distortion)

Avoid generic stock materials when a bespoke shader gives immediate visual signature:

```glsl
// Vertex Shader (vertex.glsl)
varying vec2 vUv;
varying vec3 vNormal;
uniform float uTime;

void main() {
  vUv = uv;
  vNormal = normalize(normalMatrix * normal);
  vec3 pos = position;
  pos.z += sin(pos.x * 4.0 + uTime * 2.0) * 0.08;
  gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
}

// Fragment Shader (fragment.glsl)
varying vec2 vUv;
varying vec3 vNormal;
uniform float uTime;
uniform vec3 uColorA;
uniform vec3 uColorB;

void main() {
  // Fresnel Edge Glow
  float fresnel = pow(1.0 - abs(dot(vNormal, vec3(0.0, 0.0, 1.0))), 2.5);
  vec3 color = mix(uColorA, uColorB, vUv.y + sin(uTime * 0.5) * 0.2);
  color += fresnel * 0.6;
  gl_FragColor = vec4(color, 0.9);
}
```

---

## 4. Performance & Memory Budgeting Checklist

- **Device Pixel Ratio**: Always clamp to `Math.min(window.devicePixelRatio, 2)`. Rendering at 3x or 4x on Retina screens crushes GPU fillrate with zero perceived visual benefit.
- **DRACO Geometry Compression**: Always compress `.glb` assets using DRACO or Meshopt compression.
- **Dispose Unused Assets**: Call `geometry.dispose()`, `material.dispose()`, and `texture.dispose()` on component unmount to prevent severe memory leaks in SPAs.
- **Frustum Culling**: Ensure `mesh.frustumCulled = true` (default in Three.js).
