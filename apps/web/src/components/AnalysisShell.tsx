import { useState } from "react";

import {
  getFenActiveColor,
  movePieceInFen,
  placePieceInFen,
  removePieceFromFen,
  setFenActiveColor,
} from "../utils/fen";
import type { FenActiveColor } from "../utils/fen";
import { STATIC_ANALYSIS_FEN, StaticBoard } from "./StaticBoard";
import type {
  BoardMoveAttempt,
  BoardOrientation,
  BoardRemoveAttempt,
  BoardSquareSelection,
} from "./StaticBoard";

const pieceOptions = [
  "wP",
  "wN",
  "wB",
  "wR",
  "wQ",
  "wK",
  "bP",
  "bN",
  "bB",
  "bR",
  "bQ",
  "bK",
];

function formatMoveAttempt({ piece, sourceSquare, targetSquare }: BoardMoveAttempt) {
  return `${piece} ${sourceSquare} to ${targetSquare ?? "off board"}`;
}

export function AnalysisShell({ fen }: { fen?: string }) {
  const initialFen = fen ?? STATIC_ANALYSIS_FEN;
  const [currentFen, setCurrentFen] = useState(initialFen);
  const [undoStack, setUndoStack] = useState<string[]>([]);
  const [redoStack, setRedoStack] = useState<string[]>([]);
  const [orientation, setOrientation] = useState<BoardOrientation>("white");
  const [isEditMode, setIsEditMode] = useState(false);
  const [isRemoveMode, setIsRemoveMode] = useState(false);
  const [selectedPiece, setSelectedPiece] = useState<string | null>(null);
  const [lastInteraction, setLastInteraction] = useState<string | null>(null);
  const activeColor = getFenActiveColor(currentFen);

  function applyFenEdit(nextFen: string) {
    if (nextFen === currentFen) {
      return false;
    }

    setUndoStack((history) => [...history, currentFen]);
    setRedoStack([]);
    setCurrentFen(nextFen);

    return true;
  }

  function handleMoveAttempt(move: BoardMoveAttempt) {
    setLastInteraction(formatMoveAttempt(move));

    const targetSquare = move.targetSquare;

    if (!isEditMode || isRemoveMode || !targetSquare) {
      return false;
    }

    return applyFenEdit(
      movePieceInFen({
        fen: currentFen,
        piece: move.piece,
        sourceSquare: move.sourceSquare,
        targetSquare,
      }),
    );
  }

  function handleRemoveAttempt({ piece, square }: BoardRemoveAttempt) {
    setLastInteraction(`Remove ${piece} from ${square}`);

    if (!isEditMode || !isRemoveMode) {
      return;
    }

    applyFenEdit(removePieceFromFen({ fen: currentFen, square }));
  }

  function handleSquareSelect({ square }: BoardSquareSelection) {
    if (!isEditMode || !selectedPiece) {
      return;
    }

    setLastInteraction(`Place ${selectedPiece} on ${square}`);
    applyFenEdit(placePieceInFen({ fen: currentFen, piece: selectedPiece, square }));
  }

  function handleReset() {
    setCurrentFen(initialFen);
    setUndoStack([]);
    setRedoStack([]);
    setOrientation("white");
    setIsRemoveMode(false);
    setSelectedPiece(null);
    setLastInteraction(null);
  }

  function handleUndo() {
    const previousFen = undoStack[undoStack.length - 1];

    if (!previousFen) {
      return;
    }

    setUndoStack((history) => history.slice(0, -1));
    setRedoStack((history) => [...history, currentFen]);
    setCurrentFen(previousFen);
    setLastInteraction("Undo edit");
  }

  function handleRedo() {
    const nextFen = redoStack[redoStack.length - 1];

    if (!nextFen) {
      return;
    }

    setRedoStack((history) => history.slice(0, -1));
    setUndoStack((history) => [...history, currentFen]);
    setCurrentFen(nextFen);
    setLastInteraction("Redo edit");
  }

  function handleFlip() {
    setOrientation((currentOrientation) =>
      currentOrientation === "white" ? "black" : "white",
    );
  }

  function handleEditModeToggle() {
    const nextMode = !isEditMode;

    setIsEditMode(nextMode);

    if (!nextMode) {
      setIsRemoveMode(false);
      setSelectedPiece(null);
    }
  }

  function handleRemoveModeToggle() {
    if (isEditMode) {
      setIsRemoveMode((currentMode) => !currentMode);
      setSelectedPiece(null);
    }
  }

  function handlePieceSelection(piece: string) {
    if (!isEditMode) {
      return;
    }

    setIsRemoveMode(false);
    setSelectedPiece((currentPiece) => (currentPiece === piece ? null : piece));
  }

  function handleActiveColorChange(activeColor: FenActiveColor) {
    if (!isEditMode) {
      return;
    }

    setLastInteraction(`Side to move: ${activeColor === "w" ? "White" : "Black"}`);
    applyFenEdit(setFenActiveColor({ fen: currentFen, activeColor }));
  }

  return (
    <section
      aria-labelledby="analysis-shell-title"
      className="grid flex-1 gap-6 py-8 lg:grid-cols-[minmax(0,1fr)_20rem]"
    >
      <div className="flex min-h-[32rem] flex-col rounded-lg border border-neutral-800 bg-neutral-900/70 shadow-2xl shadow-emerald-950/20">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800 px-5 py-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-emerald-300">
              Analysis board
            </p>
            <h1
              id="analysis-shell-title"
              className="mt-1 text-2xl font-semibold tracking-normal text-white"
            >
              Position workspace
            </h1>
          </div>
          <div
            aria-label="Analysis toolbar"
            className="flex flex-wrap items-center gap-2"
          >
            <button
              type="button"
              aria-pressed={isEditMode}
              onClick={handleEditModeToggle}
              className={`rounded-lg px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
                isEditMode
                  ? "bg-emerald-300 text-neutral-950"
                  : "bg-neutral-800 text-neutral-200 hover:text-white"
              }`}
            >
              Edit mode
            </button>
            <button
              type="button"
              aria-pressed={isRemoveMode}
              disabled={!isEditMode}
              onClick={handleRemoveModeToggle}
              className={`rounded-lg px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50 ${
                isRemoveMode
                  ? "bg-rose-200 text-rose-950"
                  : "bg-neutral-800 text-neutral-200 hover:text-white"
              }`}
            >
              Remove piece
            </button>
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center p-5">
          <StaticBoard
            fen={currentFen}
            orientation={orientation}
            isEditMode={isEditMode}
            isInteractive
            isRemoveMode={isRemoveMode}
            onMoveAttempt={handleMoveAttempt}
            onRemoveAttempt={handleRemoveAttempt}
            onSquareSelect={handleSquareSelect}
          />
        </div>

        <div
          aria-label="Analysis actions"
          className="flex flex-wrap items-center justify-between gap-3 border-t border-neutral-800 px-5 py-4"
        >
          <span className="text-sm text-neutral-400">
            {lastInteraction
              ? `Last interaction: ${lastInteraction}.`
              : "Board interaction ready."}
          </span>
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              disabled={undoStack.length === 0}
              onClick={handleUndo}
              className="rounded-lg border border-neutral-700 px-4 py-2 text-sm font-semibold text-neutral-200 transition hover:border-neutral-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Undo
            </button>
            <button
              type="button"
              disabled={redoStack.length === 0}
              onClick={handleRedo}
              className="rounded-lg border border-neutral-700 px-4 py-2 text-sm font-semibold text-neutral-200 transition hover:border-neutral-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50"
            >
              Redo
            </button>
            <button
              type="button"
              onClick={handleReset}
              className="rounded-lg border border-neutral-700 px-4 py-2 text-sm font-semibold text-neutral-200 transition hover:border-neutral-500 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              Reset
            </button>
            <button
              type="button"
              onClick={handleFlip}
              className="rounded-lg border border-emerald-300/60 px-4 py-2 text-sm font-semibold text-emerald-200 transition hover:border-emerald-200 hover:text-emerald-100 focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              Flip
            </button>
          </div>
        </div>
      </div>

      <aside className="rounded-lg border border-neutral-800 bg-neutral-900/60 p-5 shadow-xl shadow-neutral-950/40">
        <h2 className="text-lg font-semibold text-white">Position details</h2>
        <p className="mt-3 text-sm font-semibold text-emerald-200">
          {isEditMode ? "Edit mode active." : "Edit mode inactive."}
        </p>
        <p className="mt-2 text-sm font-semibold text-neutral-300">
          {isRemoveMode ? "Remove mode active." : "Remove mode inactive."}
        </p>
        <div className="mt-5" aria-label="Side to move">
          <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
            Side to move
          </p>
          <div className="mt-3 grid grid-cols-2 gap-2">
            <button
              type="button"
              aria-pressed={activeColor === "w"}
              disabled={!isEditMode}
              onClick={() => handleActiveColorChange("w")}
              className={`rounded-lg border px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50 ${
                activeColor === "w"
                  ? "border-emerald-200 bg-emerald-300 text-neutral-950"
                  : "border-neutral-700 bg-neutral-900 text-neutral-200 hover:border-neutral-500 hover:text-white"
              }`}
            >
              White
            </button>
            <button
              type="button"
              aria-pressed={activeColor === "b"}
              disabled={!isEditMode}
              onClick={() => handleActiveColorChange("b")}
              className={`rounded-lg border px-3 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50 ${
                activeColor === "b"
                  ? "border-emerald-200 bg-emerald-300 text-neutral-950"
                  : "border-neutral-700 bg-neutral-900 text-neutral-200 hover:border-neutral-500 hover:text-white"
              }`}
            >
              Black
            </button>
          </div>
        </div>
        <div className="mt-5" aria-label="Piece palette">
          <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
            Add piece
          </p>
          <div className="mt-3 grid grid-cols-6 gap-2">
            {pieceOptions.map((piece) => (
              <button
                key={piece}
                type="button"
                aria-pressed={selectedPiece === piece}
                disabled={!isEditMode}
                onClick={() => handlePieceSelection(piece)}
                className={`rounded-lg border px-2 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50 ${
                  selectedPiece === piece
                    ? "border-emerald-200 bg-emerald-300 text-neutral-950"
                    : "border-neutral-700 bg-neutral-900 text-neutral-200 hover:border-neutral-500 hover:text-white"
                }`}
              >
                {piece}
              </button>
            ))}
          </div>
        </div>
        <p className="mt-3 text-sm font-semibold text-neutral-300">
          {selectedPiece ? `Selected piece: ${selectedPiece}.` : "No piece selected."}
        </p>
        <p className="mt-3 text-sm leading-6 text-neutral-300">
          Board loaded from the current FEN. Piece drops, removal, and placement update
          the position only while edit mode is active. Side-to-move changes update FEN
          metadata.
        </p>
      </aside>
    </section>
  );
}
