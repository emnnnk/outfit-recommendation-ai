import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';
import { OrbitControls } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/controls/OrbitControls.js';
import { GLTFLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/GLTFLoader.js';
import { DRACOLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/DRACOLoader.js';
import { FBXLoader } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/loaders/FBXLoader.js';
import { RoomEnvironment } from 'https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/environments/RoomEnvironment.js';

const isWebGLAvailable = () => {
    try {
        const canvas = document.createElement('canvas');
        const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
        return Boolean(gl && window.WebGLRenderingContext);
    } catch {
        return false;
    }
};

const getFileExt = (url) => {
    const clean = String(url || '').split('?')[0].split('#')[0];
    const idx = clean.lastIndexOf('.');
    return idx === -1 ? '' : clean.slice(idx + 1).toLowerCase();
};

const setStatus = (statusEl, message, kind) => {
    if (!statusEl) return;

    statusEl.classList.remove('hidden');
    statusEl.dataset.kind = kind || '';

    const p = statusEl.querySelector('p');
    if (p) p.textContent = message;

    const spinner = statusEl.querySelector('.spinner');
    if (spinner) spinner.style.display = kind === 'loading' ? '' : 'none';
};

const prepareModel = (root) => {
    root.traverse((obj) => {
        if (!obj || !obj.isMesh) return;
        obj.castShadow = true;
        obj.receiveShadow = false;
        if (obj.material && obj.material.isMaterial) {
            obj.material.side = THREE.FrontSide;
        }
    });
};

const centerAndGroundModel = (root) => {
    const box = new THREE.Box3().setFromObject(root);
    const center = new THREE.Vector3();
    box.getCenter(center);
    root.position.sub(center);

    const box2 = new THREE.Box3().setFromObject(root);
    root.position.y -= box2.min.y;

    const box3 = new THREE.Box3().setFromObject(root);
    const size = new THREE.Vector3();
    box3.getSize(size);

    return { box: box3, size };
};

const fitCameraToBox = (camera, controls, box, fitOffset = 1.25) => {
    const size = new THREE.Vector3();
    box.getSize(size);

    const center = new THREE.Vector3();
    box.getCenter(center);

    const maxDim = Math.max(size.x, size.y, size.z);
    const fov = (camera.fov * Math.PI) / 180;
    let cameraZ = Math.abs((maxDim / 2) / Math.tan(fov / 2));
    cameraZ *= fitOffset;

    camera.position.set(center.x, center.y + size.y * 0.15, center.z + cameraZ);
    camera.near = Math.max(0.01, cameraZ / 100);
    camera.far = Math.max(50, cameraZ * 10);
    camera.updateProjectionMatrix();

    if (controls) {
        controls.target.set(center.x, center.y + size.y * 0.15, center.z);
        controls.minDistance = cameraZ * 0.55;
        controls.maxDistance = cameraZ * 2.25;
        controls.update();
    }
};

const loadModel = async (url) => {
    const ext = getFileExt(url);
    console.log('[3D Avatar] Loading model with extension:', ext);

    // First, fetch to check file size and status
    try {
        console.log('[3D Avatar] Fetching model file:', url);
        // Direct load without HEAD check to support dynamic URLs like Ready Player Me
        // especially since they might have redirects or missing content-length
    } catch (fetchError) {
        console.error('[3D Avatar] ❌ Fetch setup failed:', fetchError);
    }

    if (ext === 'glb' || ext === 'gltf') {
        console.log('[3D Avatar] Using GLTFLoader...');
        const loader = new GLTFLoader();
        const draco = new DRACOLoader();
        draco.setDecoderPath('https://www.gstatic.com/draco/v1/decoders/');
        loader.setDRACOLoader(draco);

        const gltf = await new Promise((resolve, reject) => {
            loader.load(
                url,
                (result) => {
                    console.log('[3D Avatar] ✅ GLTFLoader SUCCESS:', result);
                    resolve(result);
                },
                (progress) => {
                    if (progress.lengthComputable) {
                        const percent = Math.round((progress.loaded / progress.total) * 100);
                        console.log('[3D Avatar] Loading progress:', percent + '%');
                    }
                },
                (error) => {
                    console.error('[3D Avatar] ❌ GLTFLoader ERROR:', error);
                    reject(error);
                }
            );
        });

        return { root: gltf.scene, animations: gltf.animations || [] };
    }

    if (ext === 'fbx') {
        console.log('[3D Avatar] Using FBXLoader...');
        const loader = new FBXLoader();
        const obj = await new Promise((resolve, reject) => {
            loader.load(
                url,
                (result) => {
                    console.log('[3D Avatar] ✅ FBXLoader SUCCESS:', result);
                    resolve(result);
                },
                (progress) => {
                    if (progress.lengthComputable) {
                        const percent = Math.round((progress.loaded / progress.total) * 100);
                        console.log('[3D Avatar] Loading progress:', percent + '%');
                    }
                },
                (error) => {
                    console.error('[3D Avatar] ❌ FBXLoader ERROR:', error);
                    reject(error);
                }
            );
        });

        return { root: obj, animations: obj.animations || [] };
    }

    throw new Error(`Desteklenmeyen format: .${ext}. .glb, .gltf veya .fbx kullanın.`);
};

const initAvatar3D = async () => {
    console.log('[3D Avatar] Initialization started...');

    const stage = document.getElementById('avatar-stage');
    if (!stage) {
        console.error('[3D Avatar] ❌ #avatar-stage element NOT FOUND in DOM!');
        return;
    }
    console.log('[3D Avatar] ✅ #avatar-stage element found:', stage);

    const canvasHost = document.getElementById('avatar-3d-canvas');
    const statusEl = document.getElementById('avatar-3d-status');
    if (!canvasHost || !statusEl) {
        console.error('[3D Avatar] ❌ Missing required elements:', { canvasHost, statusEl });
        return;
    }
    console.log('[3D Avatar] ✅ Canvas host and status overlay found');

    const modelUrlFromDom = stage.getAttribute('data-model-url') || '';
    const params = new URLSearchParams(window.location.search);
    const modelOverride = params.get('avatar') || '';
    const modelUrl = modelOverride || modelUrlFromDom;

    console.log('[3D Avatar] Model URL resolution:', {
        fromDomAttribute: modelUrlFromDom,
        fromQueryParam: modelOverride,
        finalUrl: modelUrl
    });

    if (!isWebGLAvailable()) {
        console.error('[3D Avatar] ❌ WebGL NOT available!');
        setStatus(statusEl, 'WebGL desteklenmiyor. 3D avatar önizleme kapalı.', 'error');
        return;
    }
    console.log('[3D Avatar] ✅ WebGL is available');

    if (!modelUrl) {
        console.error('[3D Avatar] ❌ No model URL specified!');
        setStatus(statusEl, '3D avatar modeli tanımlı değil. data-model-url ekleyin veya ?avatar=URL kullanın.', 'error');
        return;
    }

    console.log('[3D Avatar] 🚀 Starting model fetch:', modelUrl);
    setStatus(statusEl, '3D avatar yükleniyor...', 'loading');

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setClearColor(0x000000, 0);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.05;
    renderer.outputColorSpace = THREE.SRGBColorSpace;

    canvasHost.innerHTML = '';
    canvasHost.appendChild(renderer.domElement);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 100);

    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.enablePan = false;
    controls.rotateSpeed = 0.6;
    controls.minPolarAngle = Math.PI * 0.25;
    controls.maxPolarAngle = Math.PI * 0.62;

    const pmrem = new THREE.PMREMGenerator(renderer);
    scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

    scene.add(new THREE.HemisphereLight(0xffffff, 0x2b2b2b, 0.35));

    const key = new THREE.DirectionalLight(0xffffff, 2.0);
    key.position.set(3.5, 6.0, 3.0);
    key.castShadow = true;
    key.shadow.mapSize.set(1024, 1024);
    key.shadow.normalBias = 0.03;
    scene.add(key);

    const fill = new THREE.DirectionalLight(0xffffff, 0.85);
    fill.position.set(-3.0, 3.0, 2.5);
    scene.add(fill);

    const rim = new THREE.DirectionalLight(0xffffff, 1.1);
    rim.position.set(0.0, 4.0, -4.5);
    scene.add(rim);

    const ground = new THREE.Mesh(
        new THREE.CircleGeometry(1, 64),
        new THREE.ShadowMaterial({ opacity: 0.22 })
    );
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    let mixer = null;

    try {
        const loaded = await loadModel(modelUrl);
        const model = loaded.root;
        const animations = loaded.animations;

        console.log('[3D Avatar] Model loaded successfully:', {
            model,
            animations: animations.length,
            children: model.children.length
        });

        prepareModel(model);
        const { box, size } = centerAndGroundModel(model);

        console.log('[3D Avatar] Model centered and grounded. Size:', size);

        const groundScale = Math.max(size.x, size.z) * 0.75;
        ground.scale.setScalar(Math.max(0.001, groundScale));

        scene.add(model);
        fitCameraToBox(camera, controls, box, 1.35);

        if (animations && animations.length > 0) {
            console.log('[3D Avatar] Playing animation:', animations[0].name);
            mixer = new THREE.AnimationMixer(model);
            mixer.clipAction(animations[0]).play();
        }

        console.log('[3D Avatar] ✅ Adding is-3d-ready class to stage');
        stage.classList.add('is-3d-ready');

        console.log('[3D Avatar] ✅ Hiding status overlay');
        statusEl.classList.add('hidden');

        // Explicitly hide SVG layers
        const svgLayers = stage.querySelectorAll('.avatar-layer');
        console.log('[3D Avatar] Hiding', svgLayers.length, 'SVG avatar layers');
        svgLayers.forEach(layer => {
            layer.style.opacity = '0';
            layer.style.pointerEvents = 'none';
        });

        console.log('[3D Avatar] 🎉 3D Avatar viewer successfully activated!');
    } catch (e) {
        console.error('[3D Avatar] ❌ LOAD FAILED:', e);
        const msg = e && e.message ? e.message : 'Bilinmeyen hata';
        const errorMessage = `3D model yüklenemedi: ${msg}`;
        setStatus(statusEl, errorMessage, 'error');
        return;
    }

    const resize = () => {
        const rect = stage.getBoundingClientRect();
        const w = Math.max(1, Math.floor(rect.width));
        const h = Math.max(1, Math.floor(rect.height));
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
    };

    resize();

    if (window.ResizeObserver) {
        const ro = new ResizeObserver(() => resize());
        ro.observe(stage);
    } else {
        window.addEventListener('resize', resize);
    }

    const clock = new THREE.Clock();
    const animate = () => {
        const dt = clock.getDelta();
        if (mixer) mixer.update(dt);
        controls.update();
        renderer.render(scene, camera);
        requestAnimationFrame(animate);
    };

    requestAnimationFrame(animate);
};

document.addEventListener('DOMContentLoaded', () => {
    initAvatar3D();
});
