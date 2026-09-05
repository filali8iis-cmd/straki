/* Offline-STRAKI-Engine – gleiche Regeln wie straki/*.py */
(function (global) {
  const BOARD_SIZE = 11;
  const ROWS = "ABCDEFGHIJK";
  const RED_BACK = 9;
  const RED_FRONT = 8;
  const BLACK_BACK = 1;
  const BLACK_FRONT = 2;
  const KING_DIRS = [
    [1, 0], [-1, 0], [0, 1], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1],
  ];
  const ORTHO_DIRS = [[1, 0], [-1, 0], [0, 1], [0, -1]];
  const DIAG_DIRS = [[1, 1], [1, -1], [-1, 1], [-1, -1]];
  const LEAP_DIRS = [[2, 2], [2, -2], [-2, 2], [-2, -2]];
  const DIRECTIONS = ["N", "E", "S", "W"];
  const DIR_DELTA = { N: [1, 0], E: [0, 1], S: [-1, 0], W: [0, -1] };
  const SCISSORS_RANGE = 4;
  const SMALL_RANGE = 3;
  const BOARD_RANGE = 11;
  const FAR_U = [[1, -1], [2, -1], [2, 0], [2, 1], [1, 1]];
  const CLOSE_U = [[0, -1], [1, -1], [1, 0], [1, 1], [0, 1]];
  const PIECE_VALUE = { 1: 1, 2: 2, 3: 3, 4: 4, B: 5, A: 7, 5: 100 };
  const NAMES = {
    1: "Soldat",
    2: "Frosch",
    3: "Kleiner Leuchtturm",
    4: "Schere",
    5: "Großer Leuchtturm",
    B: "Schild",
    A: "Speer",
  };

  function opponent(player) {
    return player === "red" ? "black" : "red";
  }

  function labelDe(player) {
    return player === "red" ? "Rot" : "Schwarz";
  }

  function forward(player) {
    return player === "red" ? "S" : "N";
  }

  function hasFacing(kind) {
    return kind === "3" || kind === "5";
  }

  function inBounds(row, col) {
    return row >= 0 && row < BOARD_SIZE && col >= 0 && col < BOARD_SIZE;
  }

  function squareName(row, col) {
    return `${ROWS[row]}${col + 1}`;
  }

  function parseSquare(text) {
    const raw = String(text).trim().toUpperCase().replace(/\s+/g, "");
    const row = ROWS.indexOf(raw[0]);
    const number = parseInt(raw.slice(1), 10);
    if (row < 0 || Number.isNaN(number) || number < 1 || number > 11) {
      throw new Error(`Ungültiges Feld: ${text}`);
    }
    return [row, number - 1];
  }

  function piece(player, kind, facing) {
    return { player, kind, facing: facing || null };
  }

  function copyPiece(src) {
    return src ? { player: src.player, kind: src.kind, facing: src.facing } : null;
  }

  function emptyBoard() {
    return Array.from({ length: BOARD_SIZE }, () => Array(BOARD_SIZE).fill(null));
  }

  function get(board, row, col) {
    if (!inBounds(row, col)) return null;
    return board[row][col];
  }

  function set(board, row, col, value) {
    board[row][col] = value;
  }

  function pieces(board, player) {
    const found = [];
    for (let row = 0; row < BOARD_SIZE; row += 1) {
      for (let col = 0; col < BOARD_SIZE; col += 1) {
        const p = board[row][col];
        if (p && (player === undefined || p.player === player)) {
          found.push([row, col, p]);
        }
      }
    }
    return found;
  }

  function find(board, player, kind) {
    return pieces(board, player).filter((item) => item[2].kind === kind);
  }

  function kingSquare(board, player) {
    const found = find(board, player, "5");
    return found.length ? [found[0][0], found[0][1]] : null;
  }

  function copyBoard(board) {
    return board.map((row) => row.map(copyPiece));
  }

  function placeSide(board, player, back, front, facing) {
    const kinds = ["A", "2", "3", "4", "5", "4", "3", "2", "A"];
    kinds.forEach((kind, offset) => {
      set(board, back, 1 + offset, piece(player, kind, hasFacing(kind) ? facing : null));
    });
    for (let col = 1; col < 10; col += 1) {
      if (col === 5) set(board, front, col, piece(player, "B", facing));
      else set(board, front, col, piece(player, "1", null));
    }
  }

  function setupBoard() {
    const board = emptyBoard();
    placeSide(board, "black", BLACK_BACK, BLACK_FRONT, "N");
    placeSide(board, "red", RED_BACK, RED_FRONT, "S");
    return board;
  }

  function applyMove(board, move) {
    if (move.rotateTo) {
      const p = get(board, ...move.start);
      if (!p || !hasFacing(p.kind)) throw new Error("Diese Figur kann nicht rotieren");
      p.facing = move.rotateTo;
      return;
    }
    const p = get(board, ...move.start);
    if (!p) throw new Error("Kein Stein auf dem Startfeld");
    set(board, move.start[0], move.start[1], null);
    set(board, move.end[0], move.end[1], p);
  }

  function quietDestinations(board, row, col) {
    const p = get(board, row, col);
    if (!p) return [];
    const dirs = p.kind === "4" ? ORTHO_DIRS : KING_DIRS;
    const dests = [];
    dirs.forEach(([dr, dc]) => {
      const dest = [row + dr, col + dc];
      if (inBounds(...dest) && !get(board, ...dest)) dests.push(dest);
    });
    return dests;
  }

  function facingDirs(p) {
    return [DIR_DELTA[p.facing || forward(p.player)]];
  }

  function fusionPartner(board, row, col, p) {
    if ((p.kind !== "3" && p.kind !== "5") || !p.facing) return null;
    const other = p.kind === "3" ? "5" : "3";
    const [dr, dc] = DIR_DELTA[p.facing];
    const ahead = get(board, row + dr, col + dc);
    const behind = get(board, row - dr, col - dc);
    if (ahead && ahead.player === p.player && ahead.kind === other && ahead.facing === p.facing) {
      return [row + dr, col + dc, ahead];
    }
    if (behind && behind.player === p.player && behind.kind === other && behind.facing === p.facing) {
      return [row - dr, col - dc, behind];
    }
    return null;
  }

  function fusedRange(board, row, col, p) {
    if (p.kind !== "3" || !p.facing) return null;
    const partner = fusionPartner(board, row, col, p);
    if (!partner) return null;
    const [pr, pc, other] = partner;
    const [dr, dc] = DIR_DELTA[p.facing];
    if (pr === row - dr && pc === col - dc && other.kind === "5") return BOARD_RANGE;
    return null;
  }

  function slideCaptures(board, row, col, player, dirs, maxRange) {
    const dests = [];
    dirs.forEach(([dr, dc]) => {
      for (let step = 1; step <= maxRange; step += 1) {
        const dest = [row + step * dr, col + step * dc];
        if (!inBounds(...dest)) break;
        const occupant = get(board, ...dest);
        if (!occupant) continue;
        if (occupant.player !== player) dests.push(dest);
        break;
      }
    });
    return dests;
  }

  function slideSquares(board, row, col, dirs, maxRange) {
    const squares = [];
    dirs.forEach(([dr, dc]) => {
      for (let step = 1; step <= maxRange; step += 1) {
        const dest = [row + step * dr, col + step * dc];
        if (!inBounds(...dest)) break;
        squares.push(dest);
        if (get(board, ...dest)) break;
      }
    });
    return squares;
  }

  function soldierAttacks(board, row, col, p) {
    const [dr, dc] = DIR_DELTA[forward(p.player)];
    const dest = [row + dr, col + dc];
    const target = inBounds(...dest) ? get(board, ...dest) : null;
    if (target && target.player !== p.player) return [dest];
    return [];
  }

  function frogAttacks(board, row, col, player) {
    const dests = [];
    LEAP_DIRS.forEach(([dr, dc]) => {
      const dest = [row + dr, col + dc];
      const target = inBounds(...dest) ? get(board, ...dest) : null;
      if (target && target.player !== player) dests.push(dest);
    });
    return dests;
  }

  function adjacentCaptures(board, row, col, player, dirs) {
    const dests = [];
    dirs.forEach(([dr, dc]) => {
      const dest = [row + dr, col + dc];
      const target = inBounds(...dest) ? get(board, ...dest) : null;
      if (target && target.player !== player) dests.push(dest);
    });
    return dests;
  }

  function figur5Dirs(p) {
    if (p.kind === "1") return [DIR_DELTA[forward(p.player)]];
    if (p.kind === "2" || p.kind === "4") return DIAG_DIRS;
    if (p.kind === "3" || p.kind === "5") return facingDirs(p);
    if (p.kind === "A") return KING_DIRS;
    return [];
  }

  function figur5Captures(board, row, col, p) {
    const dests = [];
    figur5Dirs(p).forEach(([dr, dc]) => {
      for (let step = 1; step <= BOARD_RANGE; step += 1) {
        const dest = [row + step * dr, col + step * dc];
        if (!inBounds(...dest)) break;
        const occupant = get(board, ...dest);
        if (!occupant) continue;
        if (occupant.player !== p.player && occupant.kind === "5") dests.push(dest);
        break;
      }
    });
    return dests;
  }

  function sameCell(a, b) {
    return a[0] === b[0] && a[1] === b[1];
  }

  function attackDestinations(board, row, col) {
    const p = get(board, row, col);
    if (!p || p.kind === "B") return [];
    let dests;
    if (p.kind === "1") dests = soldierAttacks(board, row, col, p);
    else if (p.kind === "2") dests = frogAttacks(board, row, col, p.player);
    else if (p.kind === "3") {
      dests = slideCaptures(board, row, col, p.player, facingDirs(p), fusedRange(board, row, col, p) || SMALL_RANGE);
    } else if (p.kind === "4") dests = slideCaptures(board, row, col, p.player, DIAG_DIRS, SCISSORS_RANGE);
    else if (p.kind === "5") dests = slideCaptures(board, row, col, p.player, facingDirs(p), BOARD_RANGE);
    else if (p.kind === "A") dests = adjacentCaptures(board, row, col, p.player, KING_DIRS);
    else dests = [];
    figur5Captures(board, row, col, p).forEach((extra) => {
      if (!dests.some((item) => sameCell(item, extra))) dests.push(extra);
    });
    return dests;
  }

  function attackedSquares(board, row, col) {
    const p = get(board, row, col);
    if (!p || p.kind === "B") return [];
    if (p.kind === "1") {
      const [dr, dc] = DIR_DELTA[forward(p.player)];
      const dest = [row + dr, col + dc];
      return inBounds(...dest) ? [dest] : [];
    }
    if (p.kind === "2") {
      return LEAP_DIRS.map(([dr, dc]) => [row + dr, col + dc]).filter((dest) => inBounds(...dest));
    }
    if (p.kind === "A") {
      return KING_DIRS.map(([dr, dc]) => [row + dr, col + dc]).filter((dest) => inBounds(...dest));
    }
    if (p.kind === "4") return slideSquares(board, row, col, DIAG_DIRS, SCISSORS_RANGE);
    if (p.kind === "3") {
      return slideSquares(board, row, col, facingDirs(p), fusedRange(board, row, col, p) || SMALL_RANGE);
    }
    if (p.kind === "5") return slideSquares(board, row, col, facingDirs(p), BOARD_RANGE);
    return [];
  }

  function rawLegalMoves(board, row, col) {
    const p = get(board, row, col);
    if (!p) return [];
    const moves = quietDestinations(board, row, col).map((dest) => ({
      start: [row, col],
      end: dest,
      capture: false,
      rotateTo: null,
    }));
    attackDestinations(board, row, col).forEach((dest) => {
      moves.push({ start: [row, col], end: dest, capture: true, rotateTo: null });
    });
    if (hasFacing(p.kind) && p.facing) {
      DIRECTIONS.forEach((direction) => {
        if (direction !== p.facing) {
          moves.push({ start: [row, col], end: [row, col], capture: false, rotateTo: direction });
        }
      });
    }
    return moves;
  }

  function protectedSquares(board, row, col) {
    const p = get(board, row, col);
    if (!p || p.kind !== "B") return [];
    const facing = p.facing || forward(p.player);
    const [dr, dc] = DIR_DELTA[facing];
    const squares = [];
    [-1, 0, 1].forEach((side) => {
      const dest = dr !== 0 ? [row + dr, col + side] : [row + side, col + dc];
      if (inBounds(...dest)) squares.push(dest);
    });
    return squares;
  }

  function isProtectedByEnemy(board, row, col, attacker) {
    return pieces(board, opponent(attacker)).some(([sr, sc, p]) => (
      p.kind === "B" && protectedSquares(board, sr, sc).some((dest) => sameCell(dest, [row, col]))
    ));
  }

  function encircleSlots(row, col, facing, offsets) {
    const [dr, dc] = DIR_DELTA[facing];
    return offsets.map(([dist, side]) => {
      const dest = dr !== 0 ? [row + dist * dr, col + side] : [row + side, col + dist * dc];
      return inBounds(...dest) ? dest : null;
    });
  }

  function orthogonallyBoxed(board, row, col, owner) {
    let sawEnemy = false;
    for (const [dr, dc] of ORTHO_DIRS) {
      const dest = [row + dr, col + dc];
      if (!inBounds(...dest)) continue;
      const occupant = get(board, ...dest);
      if (!occupant || occupant.player === owner) return false;
      sawEnemy = true;
    }
    return sawEnemy;
  }

  function uClosedByEnemy(board, row, col, owner, facing, offsets) {
    let sawEnemy = false;
    for (const dest of encircleSlots(row, col, facing, offsets)) {
      if (!dest) continue;
      const occupant = get(board, ...dest);
      if (!occupant || occupant.player === owner) return false;
      sawEnemy = true;
    }
    return sawEnemy;
  }

  function shieldIsEncircled(board, row, col) {
    const p = get(board, row, col);
    if (!p || p.kind !== "B") return false;
    if (orthogonallyBoxed(board, row, col, p.player)) return true;
    return DIRECTIONS.some((facing) => (
      uClosedByEnemy(board, row, col, p.player, facing, CLOSE_U)
      || uClosedByEnemy(board, row, col, p.player, facing, FAR_U)
    ));
  }

  class Game {
    constructor(vsAi = false, setup = true) {
      this.board = setup ? setupBoard() : emptyBoard();
      this.turn = "red";
      this.vsAi = vsAi;
      this.aiPlayer = "black";
      this.selected = null;
      this.winner = null;
      this.winReason = null;
      this.score = 0;
      this.message = "Rot beginnt.";
      this.lastMove = null;
      this.check = false;
      this.captured = { red: [], black: [] };
    }

    reset(vsAi) {
      const next = vsAi === undefined ? this.vsAi : vsAi;
      Object.assign(this, new Game(next, true));
    }

    click(row, col) {
      if (this.winner) return false;
      const dests = this.movesForSelected().filter((m) => !m.rotateTo).map((m) => m.end);
      if (this.selected && dests.some((dest) => sameCell(dest, [row, col]))) {
        return this._play(this._moveTo(row, col));
      }
      const occupant = get(this.board, row, col);
      if (occupant && occupant.player === this.turn) {
        this.selected = [row, col];
        this.message = `${labelDe(this.turn)} hat ${squareName(row, col)} (${NAMES[occupant.kind]}) gewählt.`;
        return true;
      }
      this.selected = null;
      this.message = `${labelDe(this.turn)} ist am Zug.`;
      return true;
    }

    rotate(direction) {
      if (!this.selected || this.winner) return false;
      if (!DIRECTIONS.includes(direction)) return false;
      const move = this.movesForSelected().find((item) => item.rotateTo === direction);
      return move ? this._play(move) : false;
    }

    claimHalfWin() {
      if (this.winner) return false;
      for (const player of ["red", "black"]) {
        if (this.bothSpearsCaptured(player)) {
          this._setWinner(player, "half", 0.5);
          return true;
        }
      }
      return false;
    }

    applyTurn(move) {
      this._play(move);
    }

    movesForSelected() {
      if (!this.selected) return [];
      return this.legalMovesFrom(...this.selected);
    }

    legalMovesFrom(row, col) {
      const p = get(this.board, row, col);
      if (!p || p.player !== this.turn) return [];
      return rawLegalMoves(this.board, row, col).filter((move) => this._isPlayable(move));
    }

    allLegalMoves() {
      const moves = [];
      pieces(this.board, this.turn).forEach(([row, col]) => {
        moves.push(...this.legalMovesFrom(row, col));
      });
      return moves;
    }

    bothSpearsCaptured(player) {
      return find(this.board, opponent(player), "A").length === 0;
    }

    inCheck(player) {
      const king = kingSquare(this.board, player);
      if (!king) return true;
      return this._squareAttacked(king[0], king[1], opponent(player));
    }

    _play(move) {
      if (!move || this.winner) return false;
      const captured = move.rotateTo ? null : get(this.board, ...move.end);
      applyMove(this.board, move);
      if (captured) this.captured[this.turn].push(captured.kind);
      const removed = this._removeEncircledShields();
      this.lastMove = {
        from: [...move.start],
        to: [...move.end],
        capture: move.capture,
        rotate: move.rotateTo,
      };
      this.selected = null;
      const other = opponent(this.turn);
      if (!kingSquare(this.board, other) || (this.inCheck(other) && !this._hasLegalReply(other))) {
        const score = this.bothSpearsCaptured(this.turn) ? 1.5 : 1.0;
        let reason;
        if (captured && captured.kind === "5") reason = score === 1.5 ? "perfect" : "captured";
        else reason = score === 1.5 ? "perfect" : "nullus";
        this._setWinner(this.turn, reason, score);
        if (removed) this.message = `Figur B wurde umkreist und aus dem Spiel entfernt. ${this.message}`;
        return true;
      }
      this.turn = other;
      this.check = this.inCheck(this.turn);
      if (this.check) {
        this.message = `Angriff auf Figur 5! ${labelDe(this.turn)} muss reagieren.`;
      } else {
        this.message = `${labelDe(this.turn)} ist am Zug.`;
        if (this.bothSpearsCaptured(other)) {
          this.message += ` ${labelDe(other)} hat beide Speere geschlagen (0,5 Punkte möglich).`;
        }
      }
      if (removed) {
        this.message = `Figur B wurde umkreist und aus dem Spiel entfernt. ${this.message}`;
      }
      return true;
    }

    _moveTo(row, col) {
      return this.movesForSelected().find((move) => !move.rotateTo && sameCell(move.end, [row, col])) || null;
    }

    _isPlayable(move) {
      if (!this._followsPieceRules(move)) return false;
      const mover = get(this.board, ...move.start);
      if (!mover || mover.kind !== "5") return true;
      if (!move.rotateTo) {
        const target = get(this.board, ...move.end);
        if (target && target.kind === "5") return true;
      }
      return this._escapesCheck(move);
    }

    _followsPieceRules(move) {
      if (move.rotateTo) return true;
      const target = get(this.board, ...move.end);
      if (!target) return true;
      if (target.player === this.turn) return false;
      if (target.kind === "5") return true;
      const attacker = get(this.board, ...move.start);
      if (!attacker) return false;
      if (target.kind === "B" && attacker.kind !== "A") return false;
      if (isProtectedByEnemy(this.board, move.end[0], move.end[1], this.turn) && attacker.kind !== "A") {
        return false;
      }
      return true;
    }

    _escapesCheck(move) {
      const clone = copyBoard(this.board);
      applyMove(clone, move);
      const probe = new Game(false, false);
      probe.board = clone;
      probe.turn = this.turn;
      probe._removeEncircledShields();
      return !probe.inCheck(this.turn);
    }

    _hasLegalReply(player) {
      const saved = this.turn;
      this.turn = player;
      try {
        return this._rawMoves(player).some((move) => this._followsPieceRules(move) && this._escapesCheck(move));
      } finally {
        this.turn = saved;
      }
    }

    _rawMoves(player) {
      const moves = [];
      pieces(this.board, player).forEach(([row, col]) => {
        moves.push(...rawLegalMoves(this.board, row, col));
      });
      return moves;
    }

    _squareAttacked(row, col, byPlayer) {
      for (const [ar, ac, attacker] of pieces(this.board, byPlayer)) {
        if (!attackedSquares(this.board, ar, ac).some((dest) => sameCell(dest, [row, col]))) continue;
        if (attacker.kind === "B") continue;
        const target = get(this.board, row, col);
        if (target && target.kind === "B" && attacker.kind !== "A") continue;
        if (
          target
          && target.kind !== "5"
          && isProtectedByEnemy(this.board, row, col, byPlayer)
          && attacker.kind !== "A"
        ) continue;
        return true;
      }
      return false;
    }

    _removeEncircledShields() {
      const doomed = [];
      pieces(this.board).forEach(([row, col, p]) => {
        if (p.kind === "B" && shieldIsEncircled(this.board, row, col)) {
          doomed.push([row, col, p.player]);
        }
      });
      doomed.forEach(([row, col, owner]) => {
        set(this.board, row, col, null);
        this.captured[opponent(owner)].push("B");
      });
      return doomed.length;
    }

    _setWinner(player, reason, score) {
      this.winner = player;
      this.winReason = reason;
      this.score = score;
      if (reason === "captured") {
        this.message = `${labelDe(player)} gewinnt – Figur 5 wurde geschlagen (1,0 Punkt)!`;
      } else if (reason === "nullus") {
        this.message = `${labelDe(player)} gewinnt durch Nullus motus (1,0 Punkt)!`;
      } else if (reason === "perfect") {
        this.message = `${labelDe(player)} gewinnt perfekt – Nullus motus und beide Speere (1,5 Punkte)!`;
      } else {
        this.message = `${labelDe(player)} gewinnt mit 0,5 Punkten (beide gegnerischen Speere).`;
      }
    }

    toDict() {
      const moves = this.movesForSelected();
      const listed = [];
      pieces(this.board).forEach(([row, col, p]) => {
        listed.push({
          row,
          col,
          square: squareName(row, col),
          player: p.player,
          kind: p.kind,
          name: NAMES[p.kind],
          facing: p.facing,
        });
      });
      return {
        size: 11,
        pieces: listed,
        turn: this.turn,
        vsAi: this.vsAi,
        aiPlayer: this.aiPlayer,
        selected: this.selected ? [...this.selected] : null,
        quietMoves: moves.filter((m) => !m.capture && !m.rotateTo).map((m) => [...m.end]),
        captures: moves.filter((m) => m.capture).map((m) => [...m.end]),
        rotations: moves.filter((m) => m.rotateTo).map((m) => m.rotateTo),
        winner: this.winner,
        winReason: this.winReason,
        score: this.score,
        message: this.message,
        check: this.check,
        lastMove: this.lastMove,
        canClaimHalf: !this.winner && (this.bothSpearsCaptured("red") || this.bothSpearsCaptured("black")),
        captured: { red: [...this.captured.red], black: [...this.captured.black] },
      };
    }
  }

  function snapshot(game) {
    return {
      board: copyBoard(game.board),
      turn: game.turn,
      winner: game.winner,
      winReason: game.winReason,
      score: game.score,
      message: game.message,
      check: game.check,
      selected: game.selected ? [...game.selected] : null,
      lastMove: game.lastMove ? { ...game.lastMove, from: [...game.lastMove.from], to: [...game.lastMove.to] } : null,
      captured: { red: [...game.captured.red], black: [...game.captured.black] },
      vsAi: game.vsAi,
    };
  }

  function restore(game, snap) {
    game.board = snap.board;
    game.turn = snap.turn;
    game.winner = snap.winner;
    game.winReason = snap.winReason;
    game.score = snap.score;
    game.message = snap.message;
    game.check = snap.check;
    game.selected = snap.selected;
    game.lastMove = snap.lastMove;
    game.captured = snap.captured;
    game.vsAi = snap.vsAi;
  }

  function evaluate(game, player) {
    if (game.winner === player) return 10000 + game.score * 100;
    if (game.winner && game.winner !== player) return -10000;
    let score = 0;
    pieces(game.board).forEach(([, , p]) => {
      const value = PIECE_VALUE[p.kind];
      score += p.player === player ? value : -value;
    });
    if (game.inCheck(opponent(player))) score += 25;
    if (game.inCheck(player)) score -= 25;
    if (game.bothSpearsCaptured(player)) score += 40;
    if (!kingSquare(game.board, player)) score -= 500;
    return score;
  }

  function chooseTurn(game) {
    const moves = game.allLegalMoves();
    if (!moves.length) return null;
    const player = game.turn;
    let best = -Infinity;
    const chosen = [];
    moves.forEach((move) => {
      const snap = snapshot(game);
      game.applyTurn(move);
      const score = evaluate(game, player);
      restore(game, snap);
      if (score > best) {
        best = score;
        chosen.length = 0;
        chosen.push(move);
      } else if (score === best) {
        chosen.push(move);
      }
    });
    return chosen[Math.floor(Math.random() * chosen.length)];
  }

  const api = {
    Game,
    parseSquare,
    squareName,
    quietDestinations,
    attackDestinations,
    protectedSquares,
    shieldIsEncircled,
    fusionPartner,
    chooseTurn,
    get,
    set,
    piece,
  };

  if (typeof module !== "undefined" && module.exports) module.exports = api;
  global.Straki = api;
}(typeof window !== "undefined" ? window : globalThis));
