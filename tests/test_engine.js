const assert = require("assert");
const path = require("path");
const { Game, parseSquare, attackDestinations, quietDestinations, protectedSquares, shieldIsEncircled, piece, set } = require(path.join(__dirname, "..", "straki", "static", "engine.js"));

function place(game, square, player, kind, facing) {
  const [row, col] = parseSquare(square);
  set(game.board, row, col, piece(player, kind, facing || null));
}

function kings(game) {
  place(game, "K1", "red", "5", "S");
  place(game, "A11", "black", "5", "N");
}

function ends(game) {
  return game.movesForSelected().filter((m) => !m.rotateTo).map((m) => m.end.join(","));
}

const tests = {
  figur5ForwardOnFile() {
    const game = new Game(false, false);
    game.turn = "red";
    place(game, "H6", "red", "5", "S");
    place(game, "H5", "red", "B", "S");
    place(game, "H7", "red", "1");
    place(game, "B6", "black", "5", "N");
    place(game, "A2", "red", "A");
    place(game, "A10", "red", "A");
    place(game, "K2", "black", "A");
    place(game, "K10", "black", "A");
    assert(game.inCheck("red"));
    game.click(...parseSquare("H6"));
    const quiet = new Set(game.movesForSelected().filter((m) => !m.capture && !m.rotateTo).map((m) => m.end.join(",")));
    assert(quiet.has(parseSquare("G6").join(",")));
    assert(game.click(...parseSquare("G6")));
    assert.strictEqual(game.board[parseSquare("G6")[0]][parseSquare("G6")[1]].kind, "5");
    assert.strictEqual(game.turn, "black");
  },
  openingSoldier() {
    const game = new Game();
    game.click(...parseSquare("I5"));
    const dests = new Set(ends(game));
    assert(dests.has(parseSquare("H5").join(",")));
    assert(dests.has(parseSquare("H4").join(",")));
    assert(!dests.has(parseSquare("J5").join(",")));
  },
  shieldKingMove() {
    const game = new Game(false, false);
    game.turn = "red";
    place(game, "G6", "red", "B", "S");
    place(game, "K1", "red", "5", "S");
    place(game, "A11", "black", "5", "N");
    game.click(...parseSquare("G6"));
    const quiet = new Set(game.movesForSelected().filter((m) => !m.capture && !m.rotateTo).map((m) => m.end.join(",")));
    ["F5", "F6", "F7", "G5", "G7", "H5", "H6", "H7"].forEach((sq) => {
      assert(quiet.has(parseSquare(sq).join(",")), sq);
    });
    assert(!quiet.has(parseSquare("A1").join(",")));
    game.click(...parseSquare("A1"));
    assert.strictEqual(game.board[parseSquare("G6")[0]][parseSquare("G6")[1]].kind, "B");
    game.click(...parseSquare("G6"));
    game.click(...parseSquare("H7"));
    assert.strictEqual(game.board[parseSquare("H7")[0]][parseSquare("H7")[1]].kind, "B");
  },
  soldierWhileCheck() {
    const game = new Game();
    set(game.board, ...parseSquare("I6"), null);
    set(game.board, ...parseSquare("C6"), null);
    place(game, "G8", "red", "B", "S");
    place(game, "E4", "black", "B", "N");
    game.turn = "red";
    assert(game.inCheck("red"));
    game.click(...parseSquare("I7"));
    const quiet = new Set(game.movesForSelected().filter((m) => !m.capture && !m.rotateTo).map((m) => m.end.join(",")));
    ["H6", "H7", "H8", "I6"].forEach((sq) => assert(quiet.has(parseSquare(sq).join(",")), sq));
    assert(game.click(...parseSquare("H7")));
    assert.strictEqual(game.board[parseSquare("H7")[0]][parseSquare("H7")[1]].kind, "1");
    assert.strictEqual(game.turn, "black");
  },
  scissorsOrtho() {
    const game = new Game(false, false);
    game.turn = "red";
    kings(game);
    place(game, "F6", "red", "4");
    game.click(...parseSquare("F6"));
    const quiet = new Set(game.movesForSelected().filter((m) => !m.capture).map((m) => m.end.join(",")));
    assert.deepStrictEqual(quiet, new Set(["G6", "E6", "F5", "F7"].map((sq) => parseSquare(sq).join(","))));
  },
  soldierForwardCapture() {
    const game = new Game(false, false);
    place(game, "D5", "black", "1");
    place(game, "E5", "red", "2");
    place(game, "D6", "red", "2");
    const attacks = attackDestinations(game.board, ...parseSquare("D5")).map((d) => d.join(","));
    assert.deepStrictEqual(attacks, [parseSquare("E5").join(",")]);
  },
  protectThree() {
    const game = new Game(false, false);
    place(game, "I6", "red", "B");
    const prot = new Set(protectedSquares(game.board, ...parseSquare("I6")).map((d) => d.join(",")));
    assert.deepStrictEqual(prot, new Set(["H5", "H6", "H7"].map((sq) => parseSquare(sq).join(","))));
  },
  openingNotEncircled() {
    const game = new Game();
    assert(!shieldIsEncircled(game.board, ...parseSquare("I6")));
    assert(!shieldIsEncircled(game.board, ...parseSquare("C6")));
  },
  captureFigur5() {
    const game = new Game(false, false);
    game.turn = "red";
    place(game, "E5", "red", "A");
    place(game, "E6", "black", "5", "N");
    place(game, "J6", "red", "5", "S");
    place(game, "A1", "black", "A");
    place(game, "A11", "black", "A");
    assert(attackDestinations(game.board, ...parseSquare("E5")).some((d) => d.join(",") === parseSquare("E6").join(",")));
    game.click(...parseSquare("E5"));
    game.click(...parseSquare("E6"));
    assert.strictEqual(game.winner, "red");
    assert.strictEqual(game.winReason, "captured");
  },
  eighteenEach() {
    const game = new Game();
    const red = game.board.flat().filter((p) => p && p.player === "red");
    const black = game.board.flat().filter((p) => p && p.player === "black");
    assert.strictEqual(red.length, 18);
    assert.strictEqual(black.length, 18);
  },
  quietBlocked() {
    const game = new Game();
    const dests = quietDestinations(game.board, ...parseSquare("J6")).map((d) => d.join(","));
    assert(!dests.includes(parseSquare("J5").join(",")));
    assert(!dests.includes(parseSquare("J7").join(",")));
  },
};

let failed = 0;
Object.entries(tests).forEach(([name, fn]) => {
  try {
    fn();
    console.log("ok", name);
  } catch (error) {
    failed += 1;
    console.error("FAIL", name, error);
  }
});
if (failed) {
  process.exit(1);
}
console.log("all js engine tests passed");
