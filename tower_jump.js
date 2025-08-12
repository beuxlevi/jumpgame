const canvas = document.getElementById('game');
const ctx = canvas.getContext('2d');
const WIDTH = canvas.width;
const HEIGHT = canvas.height;

// Player constants
const PLAYER_WIDTH = 50;
const PLAYER_HEIGHT = 60;
const ACC_GROUND = 1.0;
const ACC_AIR = 0.5;
const MAX_SPEED = 5;
const JUMP_VELOCITY = 22;
const GRAVITY = -1.0;

// Platform constants
const PLATFORM_WIDTH = 120;
const PLATFORM_HEIGHT = 22;
const INITIAL_GAP_MIN = 110;
const INITIAL_GAP_MAX = 130;
const INITIAL_OFFSET_MAX = 140;
const MAX_GAP_CAP = Math.floor(0.85 * (JUMP_VELOCITY ** 2) / (-2 * GRAVITY));

const AUTOSCROLL_SPEED = 1.6;
const INCREASE_EVERY = 10;
const GAP_INCREASE = 10;
const OFFSET_INCREASE = 10;
const SCROLL_INCREASE = 0.1;

let keys = {};
window.addEventListener('keydown', e => {
  keys[e.code] = true;
  if (e.code === 'Space') player.jump();
  if (['ArrowLeft', 'ArrowRight', 'KeyA', 'KeyD', 'Space'].includes(e.code)) e.preventDefault();
});
window.addEventListener('keyup', e => { keys[e.code] = false; });

class Platform {
  constructor(x, y, width = PLATFORM_WIDTH) {
    this.x = x;
    this.y = y;
    this.width = width;
    this.passed = false;
  }
}

class Player {
  constructor() {
    this.width = PLAYER_WIDTH;
    this.height = PLAYER_HEIGHT;
    this.x = WIDTH / 2 - this.width / 2;
    this.y = 0;
    this.vx = 0;
    this.vy = 0;
    this.grounded = true;
  }
  update() {
    let target = 0;
    if (keys['ArrowLeft'] || keys['KeyA']) target -= MAX_SPEED;
    if (keys['ArrowRight'] || keys['KeyD']) target += MAX_SPEED;
    if (this.grounded) {
      this.vx += ACC_GROUND * (target - this.vx);
      if (Math.abs(target) < 0.1) this.vx *= 0.8;
    } else {
      this.vx += ACC_AIR * (target - this.vx);
      this.vx *= 0.98;
    }
    this.x += this.vx;
    this.x = Math.max(0, Math.min(this.x, WIDTH - this.width));

    this.vy += GRAVITY;
    this.y += this.vy;

    let newGround = false;
    for (let p of platforms) {
      if (this.vy <= 0 && this.y - this.vy >= p.y && this.y <= p.y) {
        if (this.x + this.width > p.x && this.x < p.x + p.width) {
          this.y = p.y;
          this.vy = 0;
          newGround = true;
        }
      }
    }
    this.grounded = newGround;
  }
  jump() {
    if (this.grounded) {
      this.vy = JUMP_VELOCITY;
      this.grounded = false;
    }
  }
  draw() {
    const screenY = HEIGHT - ((this.y - cameraY) + this.height);
    ctx.fillStyle = '#c83232';
    ctx.fillRect(this.x, screenY, this.width, this.height);
  }
}

let player;
let platforms;
let lastPlatformX;
let lastPlatformY;
let cameraY;
let autoscroll;
let scrollSpeed;
let score;
let gapMax;
let offsetMax;

function resetGame() {
  player = new Player();
  platforms = [new Platform(0, 0, WIDTH)];
  lastPlatformX = 0;
  lastPlatformY = 0;
  cameraY = 0;
  autoscroll = false;
  scrollSpeed = AUTOSCROLL_SPEED;
  score = 0;
  gapMax = INITIAL_GAP_MAX;
  offsetMax = INITIAL_OFFSET_MAX;
  spawnPlatforms();
}

function spawnPlatforms() {
  gapMax = Math.min(INITIAL_GAP_MAX + Math.floor(score / INCREASE_EVERY) * GAP_INCREASE, MAX_GAP_CAP);
  offsetMax = INITIAL_OFFSET_MAX + Math.floor(score / INCREASE_EVERY) * OFFSET_INCREASE;
  while (lastPlatformY < cameraY + HEIGHT * 2) {
    const gap = randInt(INITIAL_GAP_MIN, gapMax);
    const newY = lastPlatformY + gap;
    const dx = randInt(-offsetMax, offsetMax);
    const newX = clamp(lastPlatformX + dx, 0, WIDTH - PLATFORM_WIDTH);
    platforms.push(new Platform(newX, newY));
    lastPlatformX = newX;
    lastPlatformY = newY;
  }
}

function removePlatforms() {
  platforms = platforms.filter(p => p.y > cameraY - 100);
}

function randInt(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }
function clamp(v, min, max) { return Math.max(min, Math.min(max, v)); }

function update() {
  player.update();

  if (!autoscroll && (player.y - cameraY) > HEIGHT / 2) autoscroll = true;
  if (autoscroll) {
    cameraY += scrollSpeed;
    if (score && score % INCREASE_EVERY === 0) scrollSpeed += SCROLL_INCREASE;
  }
  if (autoscroll && player.y + player.height < cameraY) {
    resetGame();
  }

  for (let p of platforms) {
    if (!p.passed && player.y > p.y) {
      p.passed = true;
      if (p.y > 0) score++;
    }
  }
  spawnPlatforms();
  removePlatforms();
  document.getElementById('score').textContent = score;
}

function draw() {
  ctx.fillStyle = '#1e1e28';
  ctx.fillRect(0, 0, WIDTH, HEIGHT);
  ctx.fillStyle = '#cccccc';
  for (let p of platforms) {
    const screenY = HEIGHT - ((p.y - cameraY) + PLATFORM_HEIGHT);
    ctx.fillRect(p.x, screenY, p.width, PLATFORM_HEIGHT);
  }
  player.draw();
}

function loop() {
  update();
  draw();
  requestAnimationFrame(loop);
}

resetGame();
requestAnimationFrame(loop);
