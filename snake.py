"""
Snake Game — Google Colab + iPhone friendly
Run this cell. Works with keyboard, swipe gestures, and on-screen D-pad.
"""

from IPython.display import display, HTML

html = """
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  * { box-sizing: border-box; }
  #snake-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: monospace;
    background: #1e1e1e;
    padding: 12px;
    border-radius: 8px;
    user-select: none;
    touch-action: none;
    max-width: 100%;
  }
  #snake-hud {
    color: #fff;
    font-size: 18px;
    margin-bottom: 8px;
    letter-spacing: 2px;
  }
  #snake-canvas {
    border: 2px solid #444;
    background: #282828;
    display: block;
    max-width: 100%;
    touch-action: none;
  }
  #snake-msg {
    color: #00e000;
    font-size: 20px;
    font-weight: bold;
    margin-top: 10px;
    min-height: 26px;
    text-align: center;
  }
  #snake-sub {
    color: #aaa;
    font-size: 13px;
    margin-top: 4px;
    min-height: 18px;
    text-align: center;
  }
  #snake-btn {
    margin-top: 10px;
    padding: 10px 36px;
    font-size: 16px;
    font-family: monospace;
    background: #333;
    color: #00e000;
    border: 2px solid #00e000;
    border-radius: 4px;
    cursor: pointer;
    -webkit-tap-highlight-color: transparent;
  }
  #snake-btn:hover, #snake-btn:active { background: #00e000; color: #000; }

  /* D-pad */
  #dpad {
    display: grid;
    grid-template-areas: ". up ." "left . right" ". down .";
    grid-template-columns: 60px 60px 60px;
    grid-template-rows: 60px 60px 60px;
    gap: 4px;
    margin-top: 14px;
  }
  .dpad-btn {
    background: #333;
    color: #00e000;
    border: 2px solid #555;
    border-radius: 8px;
    font-size: 22px;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;
  }
  .dpad-btn:active { background: #00e000; color: #000; }
  #dpad-up    { grid-area: up; }
  #dpad-left  { grid-area: left; }
  #dpad-right { grid-area: right; }
  #dpad-down  { grid-area: down; }
</style>

<div id="snake-wrapper">
  <div id="snake-hud">Score: <span id="snake-score">0</span></div>
  <canvas id="snake-canvas"></canvas>
  <div id="snake-msg">S N A K E</div>
  <div id="snake-sub">Tap Start, swipe, or use D-pad</div>
  <button id="snake-btn" onclick="snakeStart()">Start / Restart</button>
  <div id="dpad">
    <button class="dpad-btn" id="dpad-up"    ontouchstart="dpadPress([0,-1])" onclick="dpadPress([0,-1])">&#8679;</button>
    <button class="dpad-btn" id="dpad-left"  ontouchstart="dpadPress([-1,0])" onclick="dpadPress([-1,0])">&#8678;</button>
    <button class="dpad-btn" id="dpad-right" ontouchstart="dpadPress([1,0])"  onclick="dpadPress([1,0])">&#8680;</button>
    <button class="dpad-btn" id="dpad-down"  ontouchstart="dpadPress([0,1])"  onclick="dpadPress([0,1])">&#8681;</button>
  </div>
</div>

<script>
(function () {
  const COLS = 20, ROWS = 20;

  // Responsive: fit canvas to available width (max 400px)
  const wrapper = document.getElementById('snake-wrapper');
  const maxW = Math.min(wrapper.offsetWidth - 24, 400);
  const CELL = Math.floor(maxW / COLS);
  const CW = CELL * COLS, CH = CELL * ROWS;

  const canvas = document.getElementById('snake-canvas');
  canvas.width = CW;
  canvas.height = CH;
  const ctx = canvas.getContext('2d');

  const scoreEl = document.getElementById('snake-score');
  const msgEl   = document.getElementById('snake-msg');
  const subEl   = document.getElementById('snake-sub');

  let snake, dir, nextDir, food, score, loop, running;

  // ---- helpers ----
  function rand(a, b) { return Math.floor(Math.random() * (b - a + 1)) + a; }

  function placeFood() {
    const occ = new Set(snake.map(s => s[0] + ',' + s[1]));
    let p;
    do { p = [rand(0, COLS-1), rand(0, ROWS-1)]; }
    while (occ.has(p[0] + ',' + p[1]));
    return p;
  }

  function applyDir(nd) {
    if (!running) { snakeStart(); return; }
    if (nd[0] !== -dir[0] || nd[1] !== -dir[1]) nextDir = nd;
  }

  window.dpadPress = function(nd) { applyDir(nd); };

  // ---- draw ----
  function draw() {
    ctx.fillStyle = '#282828';
    ctx.fillRect(0, 0, CW, CH);

    // Grid
    ctx.strokeStyle = '#303030';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= COLS; x++) {
      ctx.beginPath(); ctx.moveTo(x*CELL, 0); ctx.lineTo(x*CELL, CH); ctx.stroke();
    }
    for (let y = 0; y <= ROWS; y++) {
      ctx.beginPath(); ctx.moveTo(0, y*CELL); ctx.lineTo(CW, y*CELL); ctx.stroke();
    }

    // Food
    ctx.fillStyle = '#e03030';
    ctx.beginPath();
    ctx.arc(food[0]*CELL + CELL/2, food[1]*CELL + CELL/2, CELL/2 - 2, 0, Math.PI*2);
    ctx.fill();

    // Snake
    snake.forEach(([x, y], i) => {
      ctx.fillStyle = i === 0 ? '#00e000' : '#009900';
      ctx.fillRect(x*CELL+1, y*CELL+1, CELL-2, CELL-2);
      if (i === 0) {
        ctx.fillStyle = '#000';
        const [ex, ey] = dir;
        const offsets = ex !== 0
          ? [[ex===1 ? CELL-5 : 2, 3], [ex===1 ? CELL-5 : 2, CELL-6]]
          : [[3, ey===1 ? CELL-5 : 2], [CELL-6, ey===1 ? CELL-5 : 2]];
        offsets.forEach(([ox, oy]) => ctx.fillRect(x*CELL+ox, y*CELL+oy, 3, 3));
      }
    });
  }

  // ---- game tick ----
  function tick() {
    dir = nextDir;
    const [hx, hy] = snake[0];
    const nh = [(hx + dir[0] + COLS) % COLS, (hy + dir[1] + ROWS) % ROWS];

    if (snake.some(s => s[0] === nh[0] && s[1] === nh[1])) {
      clearInterval(loop);
      running = false;
      msgEl.textContent = 'Game Over!  ' + score + ' pts';
      subEl.textContent = 'Tap Start or swipe to play again';
      return;
    }

    snake.unshift(nh);
    if (nh[0] === food[0] && nh[1] === food[1]) {
      score += 10;
      scoreEl.textContent = score;
      food = placeFood();
    } else {
      snake.pop();
    }
    draw();
  }

  // ---- start ----
  window.snakeStart = function () {
    if (loop) clearInterval(loop);
    const mx = Math.floor(COLS / 2), my = Math.floor(ROWS / 2);
    snake = [[mx, my], [mx-1, my], [mx-2, my]];
    dir = [1, 0]; nextDir = [1, 0];
    food = placeFood();
    score = 0;
    scoreEl.textContent = 0;
    msgEl.textContent = '';
    subEl.textContent = 'Swipe  |  D-pad  |  Arrow keys / WASD';
    running = true;
    draw();
    loop = setInterval(tick, 120);
  };

  // ---- keyboard ----
  const keyMap = {
    ArrowUp:[0,-1], w:[0,-1], ArrowDown:[0,1], s:[0,1],
    ArrowLeft:[-1,0], a:[-1,0], ArrowRight:[1,0], d:[1,0],
  };
  document.addEventListener('keydown', e => {
    if (keyMap[e.key]) { e.preventDefault(); applyDir(keyMap[e.key]); }
    if (e.key === 'q') { clearInterval(loop); running = false; msgEl.textContent = 'Goodbye!'; }
  });

  // ---- swipe (touch) ----
  let tx0, ty0;
  canvas.addEventListener('touchstart', e => {
    e.preventDefault();
    tx0 = e.touches[0].clientX;
    ty0 = e.touches[0].clientY;
  }, { passive: false });

  canvas.addEventListener('touchend', e => {
    e.preventDefault();
    const dx = e.changedTouches[0].clientX - tx0;
    const dy = e.changedTouches[0].clientY - ty0;
    if (Math.abs(dx) < 10 && Math.abs(dy) < 10) return; // tap — ignore
    if (Math.abs(dx) > Math.abs(dy)) {
      applyDir(dx > 0 ? [1, 0] : [-1, 0]);
    } else {
      applyDir(dy > 0 ? [0, 1] : [0, -1]);
    }
  }, { passive: false });

  // ---- start screen ----
  ctx.fillStyle = '#282828';
  ctx.fillRect(0, 0, CW, CH);
  ctx.fillStyle = '#00e000';
  ctx.font = `bold ${Math.floor(CELL * 2)}px monospace`;
  ctx.textAlign = 'center';
  ctx.fillText('SNAKE', CW/2, CH/2);
  ctx.fillStyle = '#aaa';
  ctx.font = `${Math.floor(CELL * 0.8)}px monospace`;
  ctx.fillText('Tap Start to play', CW/2, CH/2 + CELL * 2.2);
})();
</script>
"""

display(HTML(html))
