
import * as THREE from 'https://cdn.skypack.dev/three@0.150.1';
import { GLTFLoader } from 'https://cdn.skypack.dev/three@0.150.1/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'https://cdn.skypack.dev/three@0.150.1/examples/jsm/loaders/DRACOLoader.js';
import { OrbitControls } from 'https://cdn.skypack.dev/three@0.150.1/examples/jsm/controls/OrbitControls.js';

let scene, camera, renderer, model, mixer, controls;
let currentUrl = null;
let isAutoRotating = false;

const initAvatar3D = async () => {
    const stage = document.getElementById('avatar-stage');
    // Ensure canvas container inside stage
    let canvasContainer = document.getElementById('avatar-3d-canvas');
    if (!canvasContainer && stage) {
        canvasContainer = document.createElement('div');
        canvasContainer.id = 'avatar-3d-canvas';
        stage.appendChild(canvasContainer);
    }

    if (!stage || !canvasContainer) {
        console.warn('Avatar stage not found.');
        return;
    }

    // fallback & status elements
    const statusEl = document.getElementById('avatar-3d-status');
    const fallbackEl = document.getElementById('avatar-fallback');

    // SCENE
    scene = new THREE.Scene();
    scene.background = null;

    // CAMERA (Standard Default Position)
    const aspect = stage.clientWidth / stage.clientHeight;
    camera = new THREE.PerspectiveCamera(45, aspect, 0.1, 100);
    // Optimized for "Full Body Portrait" feel
    camera.position.set(0, 1.2, 3.2);

    // RENDERER
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true, powerPreference: "high-performance" });
    renderer.setSize(stage.clientWidth, stage.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.outputEncoding = THREE.sRGBEncoding; // Better colors

    canvasContainer.innerHTML = '';
    canvasContainer.appendChild(renderer.domElement);

    // Style canvas
    renderer.domElement.style.width = '100%';
    renderer.domElement.style.height = '100%';
    renderer.domElement.style.display = 'block';

    // LIGHTS (Cinematic Setup)
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8);
    scene.add(ambientLight);

    const dirLight = new THREE.DirectionalLight(0xffffff, 1.2);
    dirLight.position.set(2, 4, 3);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 1024;
    dirLight.shadow.mapSize.height = 1024;
    scene.add(dirLight);

    const backLight = new THREE.DirectionalLight(0xaaccff, 0.5);
    backLight.position.set(-2, 2, -3);
    scene.add(backLight);

    // CONTROLS (Strict Requirements)
    controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.08;
    controls.enableZoom = false; // LOCKED
    controls.enablePan = false;  // LOCKED
    controls.target.set(0, 1.0, 0); // Focus on Torso/Hips

    // Limits
    controls.minPolarAngle = Math.PI / 3; // Prevent looking from too high
    controls.maxPolarAngle = Math.PI / 1.5; // Prevent looking from under
    controls.minDistance = 2.0;
    controls.maxDistance = 5.0;

    controls.update();

    // INTERACTION: Stop auto-rotation on user touch
    controls.addEventListener('start', () => {
        isAutoRotating = false;
    });

    // RESIZE HANDLER
    const onResize = () => {
        if (!stage) return;
        const w = stage.clientWidth;
        const h = stage.clientHeight;
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    };
    window.addEventListener('resize', onResize);

    if (window.ResizeObserver) {
        const ro = new ResizeObserver(onResize);
        ro.observe(stage);
    }

    // ANIMATE
    const clock = new THREE.Clock();
    const animate = () => {
        requestAnimationFrame(animate);
        const delta = clock.getDelta();

        if (mixer) mixer.update(delta);

        // Auto Rotation Logic (Manual for better control than autoRotate)
        if (isAutoRotating) {
            controls.autoRotate = true;
            controls.autoRotateSpeed = 2.0; // Slow & Steady
        } else {
            controls.autoRotate = false;
        }

        controls.update();
        renderer.render(scene, camera);
    };
    animate();

    // LISTEN FOR VIEW EVENTS (Front/Back)
    window.addEventListener('avatar:view', (e) => {
        const view = e.detail;
        console.log('[3D View] Switching to:', view);
        isAutoRotating = false; // Stop rotation

        const dist = 3.2; // Keep consistent distance

        if (view === 'front') {
            // Smoothly interpolate would be nice, but jump is acceptable for responsiveness
            // Reset to front +Z
            camera.position.set(0, 1.2, dist);
            camera.lookAt(0, 1.0, 0);
        } else if (view === 'back') {
            // Move to back -Z
            camera.position.set(0, 1.2, -dist);
            camera.lookAt(0, 1.0, 0);
        }

        controls.update();
    });

    // LOAD MODEL FUNCTION
    const loadModel = async (url) => {
        if (!url) return;
        if (url === currentUrl && model) return;
        currentUrl = url;

        // Show Loading
        if (statusEl) {
            statusEl.classList.remove('hidden');
            statusEl.innerHTML = '<div class="spinner"></div><p>Avatar yükleniyor...</p>';
        }
        if (fallbackEl) fallbackEl.style.opacity = '1';

        try {
            const loader = new GLTFLoader();
            const draco = new DRACOLoader();
            draco.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
            loader.setDRACOLoader(draco);

            const gltf = await new Promise((resolve, reject) => {
                loader.load(url, resolve, undefined, reject);
            });

            if (model) scene.remove(model);
            model = gltf.scene;

            // Shadows
            model.traverse(node => {
                if (node.isMesh) {
                    node.castShadow = true;
                    node.receiveShadow = true;
                }
            });

            scene.add(model);

            // Animation
            if (gltf.animations && gltf.animations.length > 0) {
                mixer = new THREE.AnimationMixer(model);
                const action = mixer.clipAction(gltf.animations[0]);
                action.play();
            }

            // Success State
            if (statusEl) statusEl.classList.add('hidden');

            // Mark stage as ready (CSS hides fallback)
            stage.classList.add('is-3d-ready');

            console.log('[3D Avatar] Loaded Successfully');

            // Trigger One-Time Auto-Rotation
            isAutoRotating = true;
            setTimeout(() => {
                isAutoRotating = false;
            }, 3500); // 3.5s rotation then stop

        } catch (error) {
            console.error('[3D Avatar] Load Error:', error);
            if (statusEl) {
                statusEl.innerHTML = '<p style="color:#ff6b6b">Yükleme Hatası</p>';
            }
            stage.classList.remove('is-3d-ready');
            if (fallbackEl) fallbackEl.style.opacity = '1';
        }
    };

    // Initial Load
    const modelUrl = stage.dataset.modelUrl;
    if (modelUrl) {
        loadModel(modelUrl);
    }

    // Observer and Event Listener for reloads
    const observer = new MutationObserver((mutations) => {
        mutations.forEach(m => {
            if (m.type === 'attributes' && m.attributeName === 'data-model-url') {
                const newUrl = stage.dataset.modelUrl;
                if (newUrl) loadModel(newUrl);
            }
        });
    });
    observer.observe(stage, { attributes: true });

    window.addEventListener('avatar:modelChanged', () => {
        const newUrl = stage.dataset.modelUrl;
        if (newUrl) loadModel(newUrl);
    });
};

document.addEventListener('DOMContentLoaded', initAvatar3D);
