import type { ReactNode } from "react";
import { useEffect, useState } from "react";

import { trackEvent } from "../analytics";
import { createSharedPosition } from "../api/share";
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
  { code: "K", color: "white", label: "White king", symbol: "♔" },
  { code: "Q", color: "white", label: "White queen", symbol: "♕" },
  { code: "R", color: "white", label: "White rook", symbol: "♖" },
  { code: "B", color: "white", label: "White bishop", symbol: "♗" },
  { code: "N", color: "white", label: "White knight", symbol: "♘" },
  { code: "P", color: "white", label: "White pawn", symbol: "♙" },
  { code: "k", color: "black", label: "Black king", symbol: "♚" },
  { code: "q", color: "black", label: "Black queen", symbol: "♛" },
  { code: "r", color: "black", label: "Black rook", symbol: "♜" },
  { code: "b", color: "black", label: "Black bishop", symbol: "♝" },
  { code: "n", color: "black", label: "Black knight", symbol: "♞" },
  { code: "p", color: "black", label: "Black pawn", symbol: "♟" },
];

type ActionIconName =
  | "copy"
  | "edit"
  | "play"
  | "select"
  | "remove"
  | "undo"
  | "redo"
  | "reset"
  | "flip"
  | "share";

type CopyStatus = "idle" | "success" | "error";
type ShareStatus = "idle" | "loading" | "success" | "error";

const actionButtonBase =
  "inline-flex h-11 w-11 items-center justify-center rounded-lg transition focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-300 disabled:cursor-not-allowed disabled:opacity-50 sm:h-14 sm:w-14";
const actionCaptionBase = "text-center text-[0.7rem] font-semibold text-neutral-400";

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
    play: <path d="m8 5 11 7-11 7V5Z" />,
    select: (
      <>
        <path d="m5 4 8 17 1.8-7.2L22 12 5 4Z" />
        <path d="m13 13 5 5" />
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
        <path d="M8 7a6 6 0 0 1 10.4 4" />
        <path d="M18 5v6h-6" />
        <path d="M16 17A6 6 0 0 1 5.6 13" />
        <path d="M6 19v-6h6" />
      </>
    ),
    share: (
      <>
        <path d="M4 12v7a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-7" />
        <path d="M12 16V4" />
        <path d="m7 9 5-5 5 5" />
      </>
    ),
  };

  return (
    <svg
      aria-hidden="true"
      className="h-5 w-5 sm:h-6 sm:w-6"
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

function ActionControl({
  label,
  title,
  children,
}: {
  label: string;
  title?: string;
  children: ReactNode;
}) {
  return (
    <div className="flex min-w-11 flex-col items-center gap-1 sm:min-w-[4.25rem]">
      {children}
      <span className={actionCaptionBase} title={title ?? label}>
        {label}
      </span>
    </div>
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
  const [shareStatus, setShareStatus] = useState<ShareStatus>("idle");
  const [shareUrl, setShareUrl] = useState("");
  const [shareMessage, setShareMessage] = useState("");
  const [shareError, setShareError] = useState("");
  const activeColor = getFenActiveColor(currentFen);

  useEffect(() => {
    setCurrentFen(initialFen);
    setUndoStack([]);
    setRedoStack([]);
    setOrientation("white");
    setIsRemoveMode(false);
    setSelectedPiece(null);
    setSelectedSquare(null);
    setLastInteraction(null);
    setCopyStatus("idle");
    setShareStatus("idle");
    setShareUrl("");
    setShareMessage("");
    setShareError("");
  }, [initialFen]);

  function clearShareResult() {
    setShareStatus("idle");
    setShareUrl("");
    setShareMessage("");
    setShareError("");
  }

  function applyFenEdit(nextFen: string) {
    if (nextFen === currentFen) {
      return false;
    }

    setUndoStack((history) => [...history, currentFen]);
    setRedoStack([]);
    setCurrentFen(nextFen);
    setCopyStatus("idle");
    clearShareResult();

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
    if (!isEditMode) {
      return;
    }

    setSelectedSquare(square);

    if (!isRemoveMode) {
      return;
    }

    setLastInteraction(`Deleted ${piece} from ${square}`);
    applyFenEdit(removePieceFromFen({ fen: currentFen, square }));
  }

  function handleSquareSelect({ piece, square }: BoardSquareSelection) {
    if (!isEditMode) {
      return;
    }

    setSelectedSquare(square);

    if (isRemoveMode) {
      if (!piece) {
        return;
      }

      setLastInteraction(`Deleted ${piece} from ${square}`);
      applyFenEdit(removePieceFromFen({ fen: currentFen, square }));
      return;
    }

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
    clearShareResult();
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
    clearShareResult();
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
    clearShareResult();
  }

  function handleFlip() {
    setOrientation((currentOrientation) =>
      currentOrientation === "white" ? "black" : "white",
    );
  }

  function handleModeChange(nextMode: boolean) {
    if (nextMode === isEditMode) {
      return;
    }

    setIsEditMode(nextMode);

    if (nextMode) {
      trackEvent("edit_mode_opened", {
        fen_length: currentFen.length,
      });
    }

    if (!nextMode) {
      setIsRemoveMode(false);
      setSelectedPiece(null);
      setSelectedSquare(null);
    }
  }

  function handleSelectTool() {
    if (isEditMode) {
      setIsRemoveMode(false);
    }
  }

  function handleDeleteTool() {
    if (isEditMode) {
      setIsRemoveMode(true);
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
    clearShareResult();
  }

  async function handleCopyFen() {
    try {
      await navigator.clipboard.writeText(currentFen);
      trackEvent("fen_copied", {
        fen_length: currentFen.length,
      });
      setCopyStatus("success");
    } catch {
      setCopyStatus("error");
    }
  }

  async function handleSharePosition() {
    setShareStatus("loading");
    setShareError("");

    try {
      const result = await createSharedPosition(currentFen);
      const nextShareUrl = new URL(result.path, window.location.origin).toString();

      setShareUrl(nextShareUrl);

      try {
        await navigator.clipboard.writeText(nextShareUrl);
        setShareMessage("Share link copied.");
      } catch {
        setShareMessage("Share link ready.");
      }

      trackEvent("share_created", {
        fen_length: currentFen.length,
        share_path_length: result.path.length,
      });
      setShareStatus("success");
    } catch (error) {
      trackEvent("share_failed", {
        reason: getShareFailureReason(error),
        fen_length: currentFen.length,
      });
      setShareStatus("error");
      setShareUrl("");
      setShareMessage("");
      setShareError(getShareErrorMessage(error));
    }
  }

  async function handleCopyShareUrl() {
    if (!shareUrl) {
      return;
    }

    try {
      await navigator.clipboard.writeText(shareUrl);
      setShareMessage("Share link copied.");
    } catch {
      setShareMessage("Could not copy share link.");
    }
  }

  const editFeedback = isEditMode
    ? lastInteraction
      ? `Last interaction: ${lastInteraction}.`
      : "Board interaction ready."
    : "";
  const feedbackMessage =
    shareStatus === "loading"
      ? "Creating share link..."
      : shareStatus === "success"
        ? shareMessage
        : shareStatus === "error"
          ? shareError
          : copyStatus === "success"
            ? "FEN copied."
            : copyStatus === "error"
              ? "Could not copy FEN."
              : editFeedback;
  const isFeedbackError = shareStatus === "error" || copyStatus === "error";
  const isFeedbackSuccess = shareStatus === "success" || copyStatus === "success";

  return (
    <section
      aria-label="Analysis board"
      data-testid="analysis-shell"
      className={`grid min-w-0 flex-1 gap-3 py-3 sm:gap-6 sm:py-8 ${
        isEditMode ? "lg:grid-cols-[minmax(0,1fr)_20rem]" : ""
      }`}
    >
      <div
        className={`flex min-h-0 min-w-0 flex-col overflow-hidden rounded-lg border border-neutral-800 bg-neutral-900/70 shadow-2xl shadow-emerald-950/20 ${
          isEditMode ? "sm:min-h-[32rem]" : ""
        }`}
        data-testid="analysis-board-card"
      >
        <div
          className="flex flex-col items-center gap-3 px-4 py-2 sm:px-5 sm:py-3"
          data-testid="analysis-primary-controls"
        >
          <div
            aria-label="Board mode"
            className="inline-flex rounded-lg border border-neutral-700 bg-neutral-950/80 p-1"
            data-testid="board-mode-toggle"
          >
            <button
              type="button"
              aria-label="Play"
              aria-pressed={!isEditMode}
              title="Play mode"
              onClick={() => handleModeChange(false)}
              className={`inline-flex min-h-9 items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
                !isEditMode
                  ? "bg-neutral-100 text-neutral-950"
                  : "text-neutral-300 hover:text-white"
              }`}
            >
              <ActionIcon name="play" />
              <span>Play</span>
            </button>
            <button
              type="button"
              aria-label="Edit Board"
              aria-pressed={isEditMode}
              title="Edit board"
              onClick={() => handleModeChange(true)}
              className={`inline-flex min-h-9 items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-semibold transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
                isEditMode
                  ? "bg-emerald-300 text-neutral-950"
                  : "text-neutral-300 hover:text-white"
              }`}
            >
              <ActionIcon name="edit" />
              <span>Edit Board</span>
            </button>
          </div>
          {!isEditMode ? (
            <div
              aria-label="Position metadata"
              className="flex flex-wrap items-center justify-center gap-2 sm:gap-3"
              data-testid="position-metadata-controls"
            >
              <p className="text-xs font-medium uppercase tracking-wide text-neutral-500">
                Side to move
              </p>
              <div
                aria-label="Side to move"
                className="flex flex-wrap justify-center gap-2"
                data-testid="side-to-move-group"
              >
                <button
                  type="button"
                  aria-pressed={activeColor === "w"}
                  onClick={() => handleActiveColorChange("w")}
                  className={`min-h-9 rounded-lg border bg-white px-3 py-1.5 text-sm font-semibold text-neutral-950 transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
                    activeColor === "w"
                      ? "border-white ring-2 ring-emerald-300 ring-offset-2 ring-offset-neutral-900"
                      : "border-white/60 opacity-80 hover:opacity-100"
                  }`}
                >
                  White
                </button>
                <button
                  type="button"
                  aria-pressed={activeColor === "b"}
                  onClick={() => handleActiveColorChange("b")}
                  className={`min-h-9 rounded-lg border bg-neutral-950 px-3 py-1.5 text-sm font-semibold text-white transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${
                    activeColor === "b"
                      ? "border-white ring-2 ring-emerald-300 ring-offset-2 ring-offset-neutral-900"
                      : "border-neutral-500 opacity-80 hover:opacity-100"
                  }`}
                >
                  Black
                </button>
              </div>
            </div>
          ) : null}
        </div>

        <div
          className={`flex items-center justify-center px-2 ${
            isEditMode ? "flex-1 py-1 sm:p-5" : "py-2 sm:py-3"
          }`}
          data-testid="analysis-board-frame"
        >
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
          data-testid="analysis-actions"
          className="flex flex-col items-center justify-center gap-2 px-1 pb-3 pt-1 sm:flex-row sm:flex-wrap sm:gap-3 sm:px-5 sm:py-4"
        >
          <div
            className="flex w-full min-w-0 flex-col items-center gap-3"
            data-testid="analysis-action-buttons"
          >
            <div
              className="flex w-full min-w-0 flex-nowrap justify-center gap-x-1 sm:w-auto sm:flex-wrap sm:gap-x-4 sm:gap-y-3"
              data-testid="primary-board-actions"
            >
              <ActionControl label="Flip" title="Flip board orientation">
                <button
                  type="button"
                  aria-label="Flip"
                  title="Flip board orientation"
                  onClick={handleFlip}
                  className={`${actionButtonBase} border border-emerald-300/60 text-emerald-200 hover:border-emerald-200 hover:text-emerald-100`}
                >
                  <ActionIcon name="flip" />
                </button>
              </ActionControl>
              <ActionControl label="Reset" title="Reset board position">
                <button
                  type="button"
                  aria-label="Reset"
                  title="Reset board position"
                  onClick={handleReset}
                  className={`${actionButtonBase} border border-neutral-700 text-neutral-200 hover:border-neutral-500 hover:text-white`}
                >
                  <ActionIcon name="reset" />
                </button>
              </ActionControl>
              {isEditMode ? (
                <>
                  <ActionControl label="Undo" title="Undo last edit">
                    <button
                      type="button"
                      aria-label="Undo"
                      disabled={undoStack.length === 0}
                      title="Undo last edit"
                      onClick={handleUndo}
                      className={`${actionButtonBase} border border-neutral-700 text-neutral-200 hover:border-neutral-500 hover:text-white`}
                    >
                      <ActionIcon name="undo" />
                    </button>
                  </ActionControl>
                  <ActionControl label="Redo" title="Redo last edit">
                    <button
                      type="button"
                      aria-label="Redo"
                      disabled={redoStack.length === 0}
                      title="Redo last edit"
                      onClick={handleRedo}
                      className={`${actionButtonBase} border border-neutral-700 text-neutral-200 hover:border-neutral-500 hover:text-white`}
                    >
                      <ActionIcon name="redo" />
                    </button>
                  </ActionControl>
                </>
              ) : null}
            </div>
            <div
              className="flex w-full min-w-0 flex-nowrap justify-center gap-x-1 sm:w-auto sm:gap-x-4"
              data-testid="secondary-share-actions"
            >
              <ActionControl label="FEN" title="Copy FEN">
                <button
                  type="button"
                  aria-label="Copy FEN"
                  title="Copy FEN"
                  onClick={() => void handleCopyFen()}
                  className={`${actionButtonBase} border border-neutral-700 text-neutral-300 hover:border-neutral-500 hover:text-white`}
                >
                  <ActionIcon name="copy" />
                </button>
              </ActionControl>
              <ActionControl label="Share" title="Create internal share link">
                <button
                  type="button"
                  aria-label="Share"
                  title="Create internal share link"
                  disabled={shareStatus === "loading"}
                  onClick={() => void handleSharePosition()}
                  className={`${actionButtonBase} border border-neutral-700 text-neutral-300 hover:border-neutral-500 hover:text-white`}
                >
                  <ActionIcon name="share" />
                </button>
              </ActionControl>
            </div>
          </div>

          <div
            aria-live="polite"
            data-testid="analysis-feedback"
            className={`flex h-20 w-full flex-col items-center justify-center overflow-hidden px-2 text-center text-sm sm:h-16 ${
              isFeedbackError
                ? "font-semibold text-rose-200"
                : isFeedbackSuccess
                  ? "font-semibold text-emerald-200"
                  : "text-neutral-400"
            }`}
            role={isFeedbackError ? "alert" : "status"}
          >
            {feedbackMessage ? (
              <p className="max-w-full truncate">{feedbackMessage}</p>
            ) : null}
            {shareStatus === "success" && shareUrl ? (
              <div className="mt-1 flex w-full max-w-xl overflow-hidden rounded-lg border border-emerald-200/70 bg-white text-neutral-950 shadow-sm">
                <input
                  readOnly
                  aria-label="Share link"
                  className="min-w-0 flex-1 truncate bg-white px-3 py-1.5 text-xs font-medium text-neutral-950 outline-none"
                  title={shareUrl}
                  value={shareUrl}
                />
                <button
                  type="button"
                  aria-label="Copy share link"
                  title="Copy share link"
                  onClick={() => void handleCopyShareUrl()}
                  className="inline-flex min-h-9 w-10 items-center justify-center border-l border-neutral-300 text-neutral-700 transition hover:bg-neutral-100 hover:text-neutral-950 focus:outline-none focus-visible:ring-2 focus-visible:ring-emerald-600"
                >
                  <ActionIcon name="copy" />
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {isEditMode ? (
        <aside
          className="rounded-lg border border-neutral-800 bg-neutral-900/60 p-4 shadow-xl shadow-neutral-950/40 sm:p-5"
          data-testid="edit-tools-panel"
        >
          <div aria-label="Edit tools" data-testid="edit-tool-mode-controls">
            <div className="flex gap-2">
              <ActionControl label="Select" title="Select/place pieces">
                <button
                  type="button"
                  aria-label="Select or place pieces"
                  aria-pressed={!isRemoveMode}
                  title="Select or place pieces"
                  onClick={handleSelectTool}
                  className={`${actionButtonBase} ${
                    !isRemoveMode
                      ? "border border-emerald-300/70 text-emerald-100 ring-2 ring-emerald-300/50"
                      : "bg-neutral-800 text-neutral-200 hover:text-white"
                  }`}
                >
                  <ActionIcon name="select" />
                </button>
              </ActionControl>
              <ActionControl label="Delete" title="Delete pieces">
                <button
                  type="button"
                  aria-label="Delete pieces"
                  aria-pressed={isRemoveMode}
                  title="Delete pieces"
                  onClick={handleDeleteTool}
                  className={`${actionButtonBase} ${
                    isRemoveMode
                      ? "border border-rose-200 text-rose-100 ring-2 ring-rose-200/50"
                      : "bg-neutral-800 text-neutral-200 hover:text-white"
                  }`}
                >
                  <ActionIcon name="remove" />
                </button>
              </ActionControl>
            </div>
          </div>
          <div className="mt-4" aria-label="Piece palette" data-testid="piece-palette">
            <div className="grid grid-cols-6 gap-2" data-testid="piece-palette-grid">
              {pieceOptions.map((piece) => {
                const pieceTone =
                  piece.color === "white"
                    ? "border-white/70 bg-white text-neutral-950 hover:border-emerald-200"
                    : "border-neutral-600 bg-neutral-950 text-white hover:border-emerald-200";

                return (
                  <button
                    key={piece.code}
                    type="button"
                    aria-label={piece.label}
                    aria-pressed={selectedPiece === piece.code}
                    onClick={() => handlePieceSelection(piece.code)}
                    className={`min-h-11 rounded-lg border px-2 py-2 text-2xl leading-none transition focus:outline-none focus:ring-2 focus:ring-emerald-300 ${pieceTone} ${
                      selectedPiece === piece.code
                        ? "ring-2 ring-emerald-300 ring-offset-2 ring-offset-neutral-900"
                        : ""
                    }`}
                  >
                    {piece.symbol}
                  </button>
                );
              })}
            </div>
          </div>
        </aside>
      ) : null}
    </section>
  );
}

function getShareErrorMessage(error: unknown) {
  const fallback = "Could not create a share link. Try again in a moment.";

  if (!(error instanceof Error)) {
    return fallback;
  }

  if (error.message.toLowerCase().includes("network")) {
    return "Could not reach the share service. Check your connection and try again.";
  }

  return fallback;
}

function getShareFailureReason(error: unknown) {
  if (!(error instanceof Error)) {
    return "unknown";
  }

  return error.message.toLowerCase().includes("network") ? "network" : "api_error";
}
