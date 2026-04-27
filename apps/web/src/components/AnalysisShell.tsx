import { useState } from "react";

import { movePieceInFen, removePieceFromFen } from "../utils/fen";
import { STATIC_ANALYSIS_FEN, StaticBoard } from "./StaticBoard";
import type {
  BoardMoveAttempt,
  BoardOrientation,
  BoardRemoveAttempt,
} from "./StaticBoard";

function formatMoveAttempt({ piece, sourceSquare, targetSquare }: BoardMoveAttempt) {
  return `${piece} ${sourceSquare} to ${targetSquare ?? "off board"}`;
}

export function AnalysisShell({ fen }: { fen?: string }) {
  const initialFen = fen ?? STATIC_ANALYSIS_FEN;
  const [currentFen, setCurrentFen] = useState(initialFen);
  const [orientation, setOrientation] = useState<BoardOrientation>("white");
  const [isEditMode, setIsEditMode] = useState(false);
  const [isRemoveMode, setIsRemoveMode] = useState(false);
  const [lastInteraction, setLastInteraction] = useState<string | null>(null);

  function handleMoveAttempt(move: BoardMoveAttempt) {
    setLastInteraction(formatMoveAttempt(move));

    const targetSquare = move.targetSquare;

    if (!isEditMode || isRemoveMode || !targetSquare) {
      return false;
    }

    setCurrentFen((fenToUpdate) =>
      movePieceInFen({
        fen: fenToUpdate,
        piece: move.piece,
        sourceSquare: move.sourceSquare,
        targetSquare,
      }),
    );

    return true;
  }

  function handleRemoveAttempt({ piece, square }: BoardRemoveAttempt) {
    setLastInteraction(`Remove ${piece} from ${square}`);

    if (!isEditMode || !isRemoveMode) {
      return;
    }

    setCurrentFen((fenToUpdate) => removePieceFromFen({ fen: fenToUpdate, square }));
  }

  function handleReset() {
    setCurrentFen(initialFen);
    setOrientation("white");
    setIsRemoveMode(false);
    setLastInteraction(null);
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
    }
  }

  function handleRemoveModeToggle() {
    if (isEditMode) {
      setIsRemoveMode((currentMode) => !currentMode);
    }
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
        <p className="mt-3 text-sm leading-6 text-neutral-300">
          Board loaded from the current FEN. Piece drops and removal update the position
          only while edit mode is active.
        </p>
      </aside>
    </section>
  );
}
