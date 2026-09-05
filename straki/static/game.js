const ROWS = "ABCDEFGHIJK";
const boardEl = document.getElementById("board");
const statusEl = document.getElementById("status");
const checkEl = document.getElementById("check-banner");
const endHalfBtn = document.getElementById("half");
const newGameBtn = document.getElementById("new-game");
const vsAiEl = document.getElementById("vs-ai");
const ranksEl = document.getElementById("ranks");
const filesEl = document.getElementById("files");
const rotationsEl = document.getElementById("rotations");
const panel = document.querySelector(".panel");

const game = new Straki.Game();
let busy = false;

function labels() {
  ranksEl.innerHTML = "";
  filesEl.innerHTML = "";
  for (let i = 10; i >= 0; i -= 1) {
    const span = document.createElement("span");
    span.textContent = ROWS[i];
    ranksEl.appendChild(span);
  }
  for (let n = 1; n <= 11; n += 1) {
    const span = document.createElement("span");
    span.textContent = String(n);
    filesEl.appendChild(span);
  }
}

function has(list, row, col) {
  return (list || []).some((item) => item[0] === row && item[1] === col);
}

function render(state) {
  boardEl.innerHTML = "";
  vsAiEl.checked = Boolean(state.vsAi);
  statusEl.textContent = state.message;
  checkEl.hidden = !state.check;
  endHalfBtn.hidden = !state.canClaimHalf;
  panel.classList.toggle("winner", Boolean(state.winner));
  const canRotate = (state.rotations || []).length > 0;
  rotationsEl.hidden = !canRotate;

  for (let row = 10; row >= 0; row -= 1) {
    for (let col = 0; col < 11; col += 1) {
      const cell = document.createElement("button");
      cell.type = "button";
      cell.className = "cell";
      if (state.selected && state.selected[0] === row && state.selected[1] === col) {
        cell.classList.add("selected");
      }
      if (has(state.quietMoves, row, col)) cell.classList.add("quiet");
      if (has(state.captures, row, col)) cell.classList.add("capture");
      if (state.lastMove) {
        const from = state.lastMove.from;
        const to = state.lastMove.to;
        if ((from[0] === row && from[1] === col) || (to[0] === row && to[1] === col)) {
          cell.classList.add("last");
        }
      }
      const piece = state.pieces.find((item) => item.row === row && item.col === col);
      if (piece) {
        const stone = document.createElement("span");
        stone.className = `stone ${piece.player} k${piece.kind}`;
        stone.textContent = piece.facing ? `${piece.kind}${arrow(piece.facing)}` : piece.kind;
        cell.appendChild(stone);
      }
      cell.addEventListener("click", () => onCellClick(row, col));
      boardEl.appendChild(cell);
    }
  }
}

function arrow(facing) {
  return { N: "↑", E: "→", S: "↓", W: "←" }[facing] || "";
}

function state() {
  return game.toDict();
}

function maybeAi() {
  const current = state();
  if (!current.vsAi || current.winner || current.turn !== current.aiPlayer) {
    render(current);
    return;
  }
  busy = true;
  statusEl.textContent = "Computer denkt …";
  window.setTimeout(() => {
    try {
      const move = Straki.chooseTurn(game);
      if (move) game.applyTurn(move);
      render(state());
    } finally {
      busy = false;
    }
  }, 180);
}

function onCellClick(row, col) {
  if (busy) return;
  game.click(row, col);
  maybeAi();
}

rotationsEl.querySelectorAll("button").forEach((button) => {
  button.addEventListener("click", () => {
    if (busy) return;
    game.rotate(button.dataset.dir);
    maybeAi();
  });
});

endHalfBtn.addEventListener("click", () => {
  game.claimHalfWin();
  render(state());
});

newGameBtn.addEventListener("click", () => {
  game.reset(vsAiEl.checked);
  maybeAi();
});

vsAiEl.addEventListener("change", () => {
  game.reset(vsAiEl.checked);
  maybeAi();
});

labels();
render(state());
