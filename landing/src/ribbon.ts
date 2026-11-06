import * as THREE from 'three';

export interface RibbonController {
  setScrollProgress: (progress: number, sectionIndex?: number) => void;
  destroy: () => void;
}

export function initRibbon(canvasId: string): RibbonController | null {
  const canvas = document.getElementById(canvasId) as HTMLCanvasElement | null;
  if (!canvas) return null;

  // Check prefers-reduced-motion
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    return null;
  }

  let renderer: THREE.WebGLRenderer;
  try {
    renderer = new THREE.WebGLRenderer({
      canvas,
      antialias: true,
      alpha: true,
      powerPreference: 'high-performance',
    });
  } catch (e) {
    console.warn('WebGL initialization failed, falling back to CSS styling:', e);
    return null;
  }

  const dpr = Math.min(window.devicePixelRatio || 1, 1.75);
  renderer.setPixelRatio(dpr);
  renderer.setSize(window.innerWidth, window.innerHeight);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 0, 5);

  // Mouse tracking with smooth lerp
  const mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
  let scrollProgress = 0;
  let targetScrollProgress = 0;
  let isTabVisible = true;
  let animationFrameId: number;

  const onMouseMove = (e: MouseEvent) => {
    // Normalize to [-1, 1]
    mouse.targetX = (e.clientX / window.innerWidth) * 2 - 1;
    mouse.targetY = -(e.clientY / window.innerHeight) * 2 + 1;
  };
  window.addEventListener('mousemove', onMouseMove, { passive: true });

  // Custom Shader Material for Additive Flowing Ribbons
  const vertexShader = `
    uniform float uTime;
    uniform float uScroll;
    uniform vec2 uMouse;
    uniform float uRibbonIndex;
    
    varying vec2 vUv;
    varying float vEdgeFalloff;
    varying float vFlow;

    void main() {
      vUv = uv;
      vEdgeFalloff = 1.0 - abs(uv.y - 0.5) * 2.0;
      
      float t = uTime * 0.8 + uRibbonIndex * 1.57;
      float u = uv.x;
      
      // Base trajectory: curve from left-center to bottom-right
      vec3 pos;
      pos.x = mix(-3.2, 3.4, u);
      
      // Base sweeping arc
      float arcY = sin(u * 3.14159 * 0.9 + 0.4) * 0.85;
      float baseSlopeY = mix(0.4, -1.3, u);
      pos.y = baseSlopeY + arcY;
      
      // Depth
      pos.z = mix(-0.8, 0.8, sin(u * 3.14159));

      // Wave harmonics
      float wave1 = sin(u * 5.0 - t * 1.2) * 0.22;
      float wave2 = cos(u * 8.0 + t * 0.9) * 0.12;
      float wave3 = sin(u * 12.0 - t * 1.8) * 0.05;
      
      // Scroll influence: sweeps deeper, tilts, expands waves
      float scrollWave = sin(uScroll * 3.14159 * 2.0 + u * 4.0) * 0.45;
      pos.y += (wave1 + wave2 + wave3) * (1.0 + uScroll * 0.5) + scrollWave;
      pos.x += cos(u * 4.0 - t * 0.8) * 0.15;
      pos.z += sin(u * 6.0 + t) * 0.3 * (1.0 + uScroll);

      // Mouse distortion (Gaussian localized pull)
      vec2 screenUv = vec2(pos.x / 3.0, pos.y / 2.0);
      float mouseDist = distance(screenUv, uMouse);
      float mouseInfluence = exp(-mouseDist * mouseDist * 3.5) * 0.35;
      pos.x += (uMouse.x - screenUv.x) * mouseInfluence;
      pos.y += (uMouse.y - screenUv.y) * mouseInfluence;

      // Ribbon width extrusion along normal / tangent
      float ribbonWidth = (0.28 + 0.12 * sin(u * 6.0 + t)) * (1.0 + uScroll * 0.3);
      float offset = (uv.y - 0.5) * ribbonWidth;
      
      // Compute normal vector perpendicular to flow
      vec3 tangent = normalize(vec3(1.0, -0.6 + cos(u * 3.0) * 0.3, 0.0));
      vec3 normal = vec3(-tangent.y, tangent.x, 0.5);
      pos += normal * offset;

      vFlow = sin(u * 10.0 - t * 2.5);

      vec4 mvPosition = modelViewMatrix * vec4(pos, 1.0);
      gl_Position = projectionMatrix * mvPosition;
    }
  `;

  const fragmentShader = `
    uniform float uTime;
    uniform float uScroll;
    uniform float uRibbonIndex;

    varying vec2 vUv;
    varying float vEdgeFalloff;
    varying float vFlow;

    void main() {
      float u = vUv.x;
      
      // Color Palette:
      // Neon Green #00FF9C = vec3(0.0, 1.0, 0.61)
      // Neon Cyan  #00E5FF = vec3(0.0, 0.90, 1.0)
      // Neon Violet #8B5CFF = vec3(0.55, 0.36, 1.0)
      vec3 colGreen  = vec3(0.0, 1.0, 0.61);
      vec3 colCyan   = vec3(0.0, 0.90, 1.0);
      vec3 colViolet = vec3(0.55, 0.36, 1.0);
      
      // Shift gradient with scroll
      float shift = uScroll * 0.35;
      float colorU = clamp(u + shift * 0.5, 0.0, 1.0);
      
      vec3 color;
      if (colorU < 0.45) {
        float f = colorU / 0.45;
        color = mix(colGreen, colCyan, f);
      } else {
        float f = (colorU - 0.45) / 0.55;
        color = mix(colCyan, colViolet, f);
      }

      // Bright Core with soft glowing exponential falloff
      float core = pow(vEdgeFalloff, 2.4);
      float glow = pow(vEdgeFalloff, 0.8) * 0.4;
      float pulse = 0.85 + 0.15 * vFlow;

      // Alpha with smooth entry and fadeout at the ends
      float edgeFade = smoothstep(0.0, 0.15, u) * smoothstep(1.0, 0.85, u);
      float alpha = (core + glow) * pulse * edgeFade * 0.75;

      // Slight intensity boost per ribbon layer
      vec3 finalCol = color * (1.1 + core * 0.6);
      
      gl_FragColor = vec4(finalCol, alpha);
    }
  `;

  // Create Ribbon Meshes
  const ribbonCount = 4;
  const ribbons: THREE.Mesh[] = [];
  const uniformsList: Array<{ [key: string]: THREE.IUniform }> = [];

  const geometrySegmentsU = 160;
  const geometrySegmentsV = 16;
  const baseGeometry = new THREE.PlaneGeometry(1, 1, geometrySegmentsU, geometrySegmentsV);

  for (let i = 0; i < ribbonCount; i++) {
    const uniforms = {
      uTime: { value: 0 },
      uScroll: { value: 0 },
      uMouse: { value: new THREE.Vector2(0, 0) },
      uRibbonIndex: { value: i },
    };
    uniformsList.push(uniforms);

    const material = new THREE.ShaderMaterial({
      vertexShader,
      fragmentShader,
      uniforms,
      transparent: true,
      blending: THREE.AdditiveBlending,
      depthWrite: false,
      side: THREE.DoubleSide,
    });

    const mesh = new THREE.Mesh(baseGeometry, material);
    mesh.position.z = -i * 0.25;
    scene.add(mesh);
    ribbons.push(mesh);
  }

  // Handle Resize
  const onResize = () => {
    const width = window.innerWidth;
    const height = window.innerHeight;
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
  };
  window.addEventListener('resize', onResize);

  // Tab Visibility change (pause loop when hidden)
  const onVisibilityChange = () => {
    isTabVisible = document.visibilityState === 'visible';
    if (isTabVisible) {
      clock.start();
      tick();
    } else {
      clock.stop();
      cancelAnimationFrame(animationFrameId);
    }
  };
  document.addEventListener('visibilitychange', onVisibilityChange);

  // Animation Loop
  const clock = new THREE.Clock();

  const tick = () => {
    if (!isTabVisible) return;
    animationFrameId = requestAnimationFrame(tick);

    const elapsedTime = clock.getElapsedTime();

    // Smooth lerp mouse
    mouse.x += (mouse.targetX - mouse.x) * 0.05;
    mouse.y += (mouse.targetY - mouse.y) * 0.05;

    // Smooth lerp scroll
    scrollProgress += (targetScrollProgress - scrollProgress) * 0.08;

    // Update uniforms for each ribbon
    for (let i = 0; i < ribbonCount; i++) {
      const u = uniformsList[i];
      u.uTime.value = elapsedTime;
      u.uScroll.value = scrollProgress;
      u.uMouse.value.set(mouse.x, mouse.y);
    }

    renderer.render(scene, camera);
  };

  tick();

  return {
    setScrollProgress: (progress: number) => {
      targetScrollProgress = Math.max(0, Math.min(1, progress));
    },
    destroy: () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('resize', onResize);
      document.removeEventListener('visibilitychange', onVisibilityChange);
      
      ribbons.forEach((mesh) => {
        mesh.geometry.dispose();
        (mesh.material as THREE.ShaderMaterial).dispose();
      });
      renderer.dispose();
    },
  };
}

