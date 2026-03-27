"""
Snake Game for Google Colab
Run this cell and the game will appear below.
Controls: Arrow keys or WASD
"""

from IPython.display import display, HTML

html = """
<style>
  #snake-wrapper {
    display: flex;
    flex-direction: column;
    align-items: center;
    font-family: monospace;
    background: #1e1e1e;
    padding: 16px;
    border-radius: 8px;
    user-select: none;
  }
  #snake-canvas {
    border: 2px solid #444;
    background: #282828;
    display: block;
  }
  #snake-hud {
    color: #fff;
    font-size: 18px;
    margin-bottom: 8px;
    letter-spacing: 2px;
  }
  #snake-msg {
    color: #00e000;
    font-size: 22px;
    font-weight: bold;
    margin-top: 10px;
    min-height: 28px;
  }
  #snake-sub {
    color: #aaa;
    font-size: 14px;
    margin-top: 4px;
    min-height: 18px;
  }
  #snake-btn {
    margin-top: 12px;
    padding: 8px 32px;
    font-size: 16px;
    font-family: monospace;
    background: #333;
    color: #00e000;
    border: 2px solid #00e000;
    border-radius: 4px;
    cursor: pointer;
  }
  #snake-btn:hover { background: #00e000; color: #000; }
</style>

<div id="snake-wrapper">
  <div id="snake-hud">Score: <span id="snake-score">0</span></div>
  <canvas id="snake-canvas" width="600" height="400"></canvas>
  <div id="snake-msg">S N A K E</div>
  <div id="snake-sub">Press Start or any arrow key to begin</div>
  <button id="snake-btn" onclick="snakeStart()">Start / Restart</button>
</div>

<script>
(function () {
  const CELL = 20, COLS = 30, ROWS = 20;
  const canvas = document.getElementById('snake-canvas');
  const ctx = canvas.getContext('2d');
  const scoreEl = document.getElementById('snake-score');
  const msgEl = document.getElementById('snake-msg');
  const subEl = document.getElementById('snake-sub');

  let snake, dir, nextDir, food, score, loop, running;

  function rand(min, max) { return Math.floor(Math.random() * (max - min + 1)) + min; }

  function placeFood() {
    const occupied = new Set(snake.map(s => s[0] + ',' + s[1]));
    let p;
    do { p = [rand(0, COLS-1), rand(0, ROWS-1)]; }
    while (occupied.has(p[0] + ',' + p[1]));
    return p;
  }

  function draw() {
    ctx.fillStyle = '#282828';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Grid
    ctx.strokeStyle = '#303030';
    ctx.lineWidth = 0.5;
    for (let x = 0; x <= COLS; x++) {
      ctx.beginPath(); ctx.moveTo(x*CELL, 0); ctx.lineTo(x*CELL, ROWS*CELL); ctx.stroke();
    }
    for (let y = 0; y <= ROWS; y++) {
      ctx.beginPath(); ctx.moveTo(0, y*CELL); ctx.lineTo(COLS*CELL, y*CELL); ctx.stroke();
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
        // Eyes
        ctx.fillStyle = '#000';
        const [ex, ey] = [dir[0], dir[1]];
        const offsets = ex !== 0
          ? [[ex===1?14:2, 4], [ex===1?14:2, 14]]
          : [[4, ey===1?14:2], [14, ey===1?14:2]];
        offsets.forEach(([ox, oy]) => ctx.fillRect(x*CELL+ox, y*CELL+oy, 3, 3));
      }
    });
  }

  function tick() {
    dir = nextDir;
    const [hx, hy] = snake[0];
    const nh = [
      (hx + dir[0] + COLS) % COLS,
      (hy + dir[1] + ROWS) % ROWS,
    ];

    if (snake.some(s => s[0] === nh[0] && s[1] === nh[1])) {
      clearInterval(loop);
      running = false;
      msgEl.textContent = 'Game Over! ' + score + ' pts';
      subEl.textContent = 'Press Start or any arrow key to play again';
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

  window.snakeStart = function () {
    if (loop) clearInterval(loop);
    const midX = Math.floor(COLS / 2), midY = Math.floor(ROWS / 2);
    snake = [[midX, midY], [midX-1, midY], [midX-2, midY]];
    dir = [1, 0]; nextDir = [1, 0];
    food = placeFood();
    score = 0;
    scoreEl.textContent = 0;
    msgEl.textContent = '';
    subEl.textContent = 'Arrow keys or WASD to move  |  q to quit';
    running = true;
    draw();
    loop = setInterval(tick, 120);
  };

  document.addEventListener('keydown', function (e) {
    const map = {
      ArrowUp:    [0,-1], w: [0,-1],
      ArrowDown:  [0, 1], s: [0, 1],
      ArrowLeft:  [-1,0], a: [-1,0],
      ArrowRight: [ 1,0], d: [ 1,0],
    };
    if (map[e.key]) {
      e.preventDefault();
      if (!running) { snakeStart(); return; }
      const nd = map[e.key];
      if (nd[0] !== -dir[0] || nd[1] !== -dir[1]) nextDir = nd;
    }
    if (e.key === 'q') { clearInterval(loop); running = false; msgEl.textContent = 'Goodbye!'; }
  });

  // Draw start screen
  ctx.fillStyle = '#282828';
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.fillStyle = '#00e000';
  ctx.font = 'bold 48px monospace';
  ctx.textAlign = 'center';
  ctx.fillText('SNAKE', canvas.width/2, canvas.height/2);
  ctx.fillStyle = '#aaa';
  ctx.font = '18px monospace';
  ctx.fillText('Press Start to play', canvas.width/2, canvas.height/2 + 40);
})();
</script>
"""

display(HTML(html))
