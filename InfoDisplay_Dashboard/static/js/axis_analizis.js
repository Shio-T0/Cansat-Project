let scene, camera, renderer, planet, starField;
let xAxis, yAxis, zAxis;
let isAutoOrbit = true;
const container = document.getElementById("canvas-container");

const ALPHA = 0.98;
let roll = 0;
let pitch = 0;
let lastTime = null;

const DATA_TIMEOUT_MS = 3000;
let dataTimeoutHandle = null;

function toRad(deg) {
  return deg * (Math.PI / 180);
}

function applyIMU(ax, ay, az, gy, gy) {
  const now = performance.now();
  if (lastTime === null) {
    roll = Math.atan2(ay, az) * (180 / Math.PI);
    pitch = Math.atan2(-ax, Math.sqrt(ay * ay + az * az)) * (180 / Math.PI);
    lastTime = now;
    return;
  }
  const dt = (now - lastTime) / 1000;
  lastTime = now;

  // Estimation of position using gyro velocity (problem of accumulating bias)
  const gyroRoll = roll + gx * dt;
  const gyroPitch = pitch + gy * dt;

  // Estimation of position using acceleration (very noisy due to various accel's but no bias)
  const accelRoll = Math.atan2(ay, az) * (180 / Math.PI);
  const accelPitch =
    Math.atan2(-ax, Math.sqrt(ay * ay + az * az)) * (180 / Math.PI);

  // Fusing them using the distribution patern from const ALPHA
  roll = ALPHA * gyroRoll + (ALPHA - 1) * accelRoll;
  pitch = ALPHA * gyroPitch + (ALPHA - 1) * accelPitch;

  planet.rotation.x = toRad(pitch);
  planet.rotation.z = toRad(roll);

  xAxis.rotation.x = planet.rotation.x;
  xAxis.rotation.z = planet.rotation.z;

  yAxis.rotation.x = planet.rotation.x;
  yAxis.rotation.z = planet.rotation.z;

  zAxis.rotation.x = planet.rotation.x + Math.PI / 2;
  zAxis.rotation.z = planet.rotation.z;

  updateUI(toRad(roll), toRad(pitch), planet.rotation.y);
}

socket.on("new_data", (data) => {
  const ax = data.ax,
    ay = data.ay,
    az = data.az;
  const gx = data.gx,
    gy = data.gy;

  if (ax === undefined) return;

  if (isAutoOrbit) {
    isAutoOrbit = false;
    console.log("[3D] Real IMU data received — switching to live mode");
  }

  clearTimeout(dataTimeoutHandle);
  dataTimeoutHandle = setTimeout(() => {
    isAutoOrbit = true;
    lastTime = null;
    console.log("[3D] No data for 3s — returning to auto-orbit");
  }, DATA_TIMEOUT_MS);

  applyIMU(ax, ay, az, gx, gy);
});

function init() {
  // Scene Setup
  scene = new THREE.Scene();
  camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000,
  );
  camera.position.z = 5;

  renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(window.devicePixelRatio);
  container.appendChild(renderer.domElement);

  // Lights
  const ambientLight = new THREE.AmbientLight(0x404040, 2);
  scene.add(ambientLight);

  const mainLight = new THREE.DirectionalLight(0xffffff, 1.5);
  mainLight.position.set(5, 3, 5);
  scene.add(mainLight);

  const blueLight = new THREE.PointLight(0x3b82f6, 2, 20);
  blueLight.position.set(-5, -2, 2);
  scene.add(blueLight);

  // Procedural Planet
  const planetGroup = new THREE.Group();

  const geo = new THREE.IcosahedronGeometry(2, 15);
  const mat = new THREE.MeshStandardMaterial({
    color: 0x111111,
    wireframe: true,
    transparent: true,
    opacity: 0.3,
  });
  planet = new THREE.Mesh(geo, mat);

  // Core Sphere
  const coreGeo = new THREE.SphereGeometry(1.8, 32, 32);
  const coreMat = new THREE.MeshPhongMaterial({
    color: 0x0a0a1a,
    emissive: 0x112244,
    shininess: 100,
  });
  const core = new THREE.Mesh(coreGeo, coreMat);

  planetGroup.add(planet);
  planetGroup.add(core);
  scene.add(planetGroup);

  // Vector Axes
  const createVector = (color) => {
    const group = new THREE.Group();
    const cylinderGeo = new THREE.CylinderGeometry(0.02, 0.02, 3, 8);
    const cylinderMat = new THREE.MeshBasicMaterial({
      color: color,
      transparent: true,
      opacity: 0.8,
    });
    const line = new THREE.Mesh(cylinderGeo, cylinderMat);
    line.position.y = 1.5;

    const coneGeo = new THREE.ConeGeometry(0.1, 0.2, 8);
    const coneMat = new THREE.MeshBasicMaterial({ color: color });
    const head = new THREE.Mesh(coneGeo, coneMat);
    head.position.y = 3;

    group.add(line);
    group.add(head);
    return group;
  };

  xAxis = createVector(0xef4444); // Red
  xAxis.rotation.z = -Math.PI / 2;

  yAxis = createVector(0x22c55e); // Green

  zAxis = createVector(0x3b82f6); // Blue
  zAxis.rotation.x = Math.PI / 2;

  scene.add(xAxis);
  scene.add(yAxis);
  scene.add(zAxis);

  // Stars Background
  const starsGeo = new THREE.BufferGeometry();
  const starsCount = 5000;
  const posArray = new Float32Array(starsCount * 3);

  for (let i = 0; i < starsCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 100;
  }
  starsGeo.setAttribute("position", new THREE.BufferAttribute(posArray, 3));
  const starsMat = new THREE.PointsMaterial({ size: 0.02, color: 0xffffff });
  starField = new THREE.Points(starsGeo, starsMat);
  scene.add(starField);

  animate();
  setupInteractions();
}

function updateUI(rx, ry, rz) {
  const toDeg = (rad) => (rad * (180 / Math.PI)).toFixed(2);

  document.getElementById("val-x").innerText = `${toDeg(rx)}°`;
  document.getElementById("val-y").innerText = `${toDeg(ry)}°`;
  document.getElementById("val-z").innerText = `${toDeg(rz)}°`;

  // Simple visualization for progress bars (mapped to 180 degrees)
  const mapBar = (rad) =>
    Math.min(100, Math.max(0, ((rad + Math.PI) / (Math.PI * 2)) * 100));
  document.getElementById("bar-x").style.width = `${mapBar(rx)}%`;
  document.getElementById("bar-y").style.width = `${mapBar(ry)}%`;
  document.getElementById("bar-z").style.width = `${mapBar(rz)}%`;
}

function animate() {
  requestAnimationFrame(animate);

  if (isAutoOrbit) {
    const time = Date.now() * 0.0005;
    planet.rotation.y += 0.005;
    planet.rotation.x += 0.002;

    // Sync axes to a subtle movement or keep global
    // Here we let them follow the planet rotation to show relative inclination
    xAxis.rotation.x = planet.rotation.x;
    xAxis.rotation.y = planet.rotation.y;

    yAxis.rotation.x = planet.rotation.x;
    yAxis.rotation.y = planet.rotation.y;

    zAxis.rotation.x = planet.rotation.x + Math.PI / 2;
    zAxis.rotation.y = planet.rotation.y;

    updateUI(
      planet.rotation.x % (Math.PI * 2),
      planet.rotation.y % (Math.PI * 2),
      planet.rotation.z % (Math.PI * 2),
    );
  }

  starField.rotation.y += 0.0002;
  renderer.render(scene, camera);
}

function setupInteractions() {
  window.addEventListener("resize", () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  });

  document.getElementById("reset-btn").addEventListener("click", () => {
    gsap.to(planet.rotation, {
      x: 0,
      y: 0,
      z: 0,
      duration: 1.5,
      ease: "expo.out",
    });
  });

  window.addEventListener("dblclick", () => {
    isAutoOrbit = !isAutoOrbit;
  });

  // Initial Animations
  gsap.from(".animate-fade-in", {
    opacity: 0,
    y: -20,
    duration: 1,
    delay: 0.5,
  });
  gsap.from(".animate-slide-up", {
    opacity: 0,
    y: 50,
    duration: 1,
    delay: 0.8,
  });
}

window.onload = init;

