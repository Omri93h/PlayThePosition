import type { ReactNode } from "react";
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
  { code: "wK", label: "White king", symbol: "♔" },
  { code: "wQ", label: "White queen", symbol: "♕" },
  { code: "wR", label: "White rook", symbol: "♖" },
  { code: "wB", label: "White bishop", symbol: "♗" },
  { code: "wN", label: "White knight", symbol: "♘" },
  { code: "wP", label: "White pawn", symbol: "♙" },
  { code: "bK", label: "Black king", symbol: "♚" },
  { code: "bQ", label: "Black queen", symbol: "♛" },
  { code: "bR", label: "Black rook", symbol: "♜" },
  { code: "bB", label: "Black bishop", symbol: "♝" },
  { code: "bN", label: "Black knight", symbol: "♞" },
  { code: "bP", label: "Black pawn", symbol: "♟" },
];

type ActionIconName = "copy" | "edit" | "remove" | "undo" | "redo" | "reset" | "flip";

type CopyStatus = "idle" | "success" | "error";

const actionButtonBase =
  "inline-flex h-12 w-12 items-center justify-center rounded-lg transition focus:outline-none focus:ring-2 focus:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50";

function formatMoveAttempt({ piece, sourceSquare, targetSquare }: BoardMoveAttempt) {
  return `${piece} ${sourceSquare} to ${targetSquare ?? "off board"}`;
}

function ActionIcon({ name }: { name: ActionIconName }) {
  const paths: Record<ActionIconName, ReactNode> = {
    copy: (
      <>
        <path d="M8 8h10v12H8z" />
        <path d="M6 16H4V4h10v2" />
      </>
    ),
    edit: (
      <>
        <path d="M4 16v4h4L18.5 9.5l-4-4L4 16Z" />
        <path d="m13.5 6.5 4 4" />
      </>
    ),
    remove: (
      <>
        <path d="M5 7h14" />
        <path d="M9 7V5h6v2" />
        <path d="M8 10v8" />
        <path d="M12 10v8" />
        <path d="M16 10v8" />
        <path d="M7 7l1 13h8l1-13" />
      </>
    ),
    undo: (
      <>
        <path d="M9 7 5 11l4 4" />
        <path d="M5 11h9a5 5 0 0 1 0 10h-2" />
      </>
    ),
    redo: (
      <>
        <path d="m15 7 4 4-4 4" />
        <path d="M19 11h-9a5 5 0 0 0 0 10h2" />
      </>
    ),
    reset: (
      <>
        <path d="M4 12a8 8 0 1 0 2.34-5.66" />
        <path d="M4 4v6h6" />
      </>
    ),
    flip: (
      <>
        <path d="M7 7h10l-3-3" />
        <path d="m17 7-3 3" />
        <path d="M17 17H7l3 3" />
        <path d="m7 17 3-3" />
      </>
    ),
  };

  return (
    <svg
      aria-hidden="true"
      className="h-5 w-5"
      fill="none"
      stroke="currentColor"
      strokeLinecap="round"
      strokeLinejoin="round"
      strokeWidth="2"
      viewBox="0 0 24 24"
    >
      {paths[name]}
    </svg>
  );
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
  const [selectedSquare, setSelectedSquare] = useState<string | null>(null);
  const [lastInteraction, setLastInteraction] = useState<string | null>(null);
  const [copyStatus, setCopyStatus] = useState<CopyStatus>("idle");
  const activeColor = getFenActiveColor(currentFen);

  function applyFenEdit(nextFen: string) {
    if (nextFen === currentFen) {
      return false;
    }

    setUndoStack((history) => [...history, currentFen]);
    setRedoStack([]);
    setCurrentFen(nextFen);
    setCopyStatus("idle");

    return true;
  }

  function handleMoveAttempt(move: BoardMoveAttempt) {
    setLastInteraction(formatMoveAttempt(move));

    const targetSquare = move.targetSquare;

    if (!isEditMode || isRemoveMode || !targetSquare) {
      return false;
    }

    setSelectedSquare(targetSquare);

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

    if (!isEditMode) {
      return;
    }

    setSelectedSquare(square);

    if (!isRemoveMode) {
      return;
    }

    applyFenEdit(removePieceFromFen({ fen: currentFen, square }));
  }

  function handleSquareSelect({ square }: BoardSquareSelection) {
    if (!isEditMode) {
      return;
    }

    setSelectedSquare(square);

    if (!selectedPiece) {
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
    setSelectedSquare(null);
    setLastInteraction(null);
    setCopyStatus("idle");
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
    setCopyStatus("idle");
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
    setCopyStatus("idle");
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
      setSelectedSquare(null);
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
    setLastInteraction(`Side to move: ${activeColor === "w" ? "White" : "Black"}`);
    setCurrentFen((fen) => setFenActiveColor({ fen, activeColor }));
    setCopyStatus("idle");
  }

  async function handleCopyFen() {
    try {
      await navigator.clipboard.writeText(currentFen);
      setCopyStatus("success");
    } catch {
      setCopyStatus("error");
    }
  }

  return (
    <section
      aria-labelledby="analysis-shell-title"
      className={`grid flex-1 gap-6 py-8 ${
        isEditMode ? "lg:grid-cols-[minmax(0,1fr)_20rem]" : ""
      }`}
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
              aria-label="Edit mode"
              aria-pressed={isEditMode}
              title="Edit mode"
              onClick={handleEditModeToggle}
              className={`${actionButtonBase} ${
                isEditMode
                  ? "bg-emerald-300 text-neutral-950"
                  : "bg-neutral-800 text-neutral-200 hover:text-white"
              }`}
            >
              <ActionIcon name="edit" />
            </button>
          </div>
        </div>

        <div
          aria-label="Position metadata"
          className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800 px-5 py-4"
        >
          <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
            Side to move
          </p>
          <div aria-label="Side to move" className="flex gap-2">
            <button
              type="button"
              aria-pressed={activeColor === "w"}
              onClick={() => handleActiveColorChange("w")}
              className={`rounded-lg border px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
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
              onClick={() => handleActiveColorChange("b")}
              className={`rounded-lg border px-4 py-2 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
                activeColor === "b"
                  ? "border-emerald-200 bg-emerald-300 text-neutral-950"
                  : "border-neutral-700 bg-neutral-900 text-neutral-200 hover:border-neutral-500 hover:text-white"
              }`}
            >
              Black
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
            selectedSquare={isEditMode ? selectedSquare : null}
            onMoveAttempt={handleMoveAttempt}
            onRemoveAttempt={handleRemoveAttempt}
            onSquareSelect={handleSquareSelect}
          />
        </div>

        <div
          aria-label="Analysis actions"
          className="flex flex-wrap items-center justify-between gap-3 border-t border-neutral-800 px-5 py-4"
        >
          {isEditMode ? (
            <span className="text-sm text-neutral-400">
              {lastInteraction
                ? `Last interaction: ${lastInteraction}.`
                : "Board interaction ready."}
            </span>
          ) : (
            <span aria-hidden="true" />
          )}
          <div className="flex flex-wrap gap-2">
            <button
              type="button"
              aria-label="Copy FEN"
              title="Copy FEN"
              onClick={() => void handleCopyFen()}
              className={`${actionButtonBase} border border-emerald-300/60 text-emerald-200 hover:border-emerald-200 hover:text-emerald-100`}
            >
              <ActionIcon name="copy" />
            </button>
            {isEditMode ? (
              <>
                <button
                  type="button"
                  aria-label="Undo"
                  disabled={undoStack.length === 0}
                  title="Undo"
                  onClick={handleUndo}
                  className={`${actionButtonBase} border border-neutral-700 text-neutral-200 hover:border-neutral-500 hover:text-white`}
                >
                  <ActionIcon name="undo" />
                </button>
                <button
                  type="button"
                  aria-label="Redo"
                  disabled={redoStack.length === 0}
                  title="Redo"
                  onClick={handleRedo}
                  className={`${actionButtonBase} border border-neutral-700 text-neutral-200 hover:border-neutral-500 hover:text-white`}
                >
                  <ActionIcon name="redo" />
                </button>
              </>
            ) : null}
            <button
              type="button"
              aria-label="Reset"
              title="Reset"
              onClick={handleReset}
              className={`${actionButtonBase} border border-neutral-700 text-neutral-200 hover:border-neutral-500 hover:text-white`}
            >
              <ActionIcon name="reset" />
            </button>
            <button
              type="button"
              aria-label="Flip"
              title="Flip"
              onClick={handleFlip}
              className={`${actionButtonBase} border border-emerald-300/60 text-emerald-200 hover:border-emerald-200 hover:text-emerald-100`}
            >
              <ActionIcon name="flip" />
            </button>
          </div>
          {copyStatus === "success" ? (
            <p className="w-full text-right text-sm font-semibold text-emerald-200">
              FEN copied.
            </p>
          ) : null}
          {copyStatus === "error" ? (
            <p className="w-full text-right text-sm font-semibold text-rose-200">
              Could not copy FEN.
            </p>
          ) : null}
        </div>
      </div>

      {isEditMode ? (
        <aside className="rounded-lg border border-neutral-800 bg-neutral-900/60 p-5 shadow-xl shadow-neutral-950/40">
          <h2 className="text-lg font-semibold text-white">Position details</h2>
          <p className="mt-3 text-sm font-semibold text-emerald-200">
            Edit mode active.
          </p>
          <p className="mt-2 text-sm font-semibold text-neutral-300">
            {isRemoveMode ? "Remove tool active." : "Remove tool inactive."}
          </p>
          <div className="mt-5" aria-label="Edit tools">
            <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
              Edit tools
            </p>
            <div className="mt-3 flex gap-2">
              <button
                type="button"
                aria-label="Remove piece"
                aria-pressed={isRemoveMode}
                title="Remove piece"
                onClick={handleRemoveModeToggle}
                className={`${actionButtonBase} ${
                  isRemoveMode
                    ? "bg-rose-200 text-rose-950"
                    : "bg-neutral-800 text-neutral-200 hover:text-white"
                }`}
              >
                <ActionIcon name="remove" />
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
                  key={piece.code}
                  type="button"
                  aria-label={piece.label}
                  aria-pressed={selectedPiece === piece.code}
                  onClick={() => handlePieceSelection(piece.code)}
                  className={`rounded-lg border px-2 py-2 text-2xl leading-none transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
                    selectedPiece === piece.code
                      ? "border-emerald-200 bg-emerald-300 text-neutral-950"
                      : "border-neutral-700 bg-neutral-900 text-neutral-200 hover:border-neutral-500 hover:text-white"
                  }`}
                >
                  {piece.symbol}
                </button>
              ))}
            </div>
          </div>
          <p className="mt-3 text-sm font-semibold text-neutral-300">
            {selectedPiece ? `Selected piece: ${selectedPiece}.` : "No piece selected."}
          </p>
          <p className="mt-3 text-sm leading-6 text-neutral-300">
            Board loaded from the current FEN. Piece drops, removal, and placement
            update the position only while edit mode is active. Side-to-move changes
            update FEN metadata.
          </p>
        </aside>
      ) : null}
    </section>
  );
}
