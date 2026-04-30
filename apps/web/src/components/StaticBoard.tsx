import type { CSSProperties } from "react";
import { Chessboard } from "react-chessboard";
import type {
  PieceDropHandlerArgs,
  PieceHandlerArgs,
  SquareHandlerArgs,
} from "react-chessboard";

export const STATIC_ANALYSIS_FEN =
  "r2q1rk1/pp2bppp/2npbn2/2pNp3/2P1P3/2N2Q2/PP2BPPP/R1B2RK1 w - - 0 10";

export type BoardMoveAttempt = {
  piece: string;
  sourceSquare: string;
  targetSquare: string | null;
};

export type BoardRemoveAttempt = {
  piece: string;
  square: string;
};

export type BoardSquareSelection = {
  square: string;
};

export type BoardOrientation = "white" | "black";

export function StaticBoard({
  fen = STATIC_ANALYSIS_FEN,
  orientation = "white",
  isEditMode = false,
  isInteractive = false,
  isRemoveMode = false,
  selectedSquare = null,
  onMoveAttempt,
  onRemoveAttempt,
  onSquareSelect,
}: {
  fen?: string;
  orientation?: BoardOrientation;
  isEditMode?: boolean;
  isInteractive?: boolean;
  isRemoveMode?: boolean;
  selectedSquare?: string | null;
  onMoveAttempt?: (move: BoardMoveAttempt) => boolean | void;
  onRemoveAttempt?: (attempt: BoardRemoveAttempt) => void;
  onSquareSelect?: (selection: BoardSquareSelection) => void;
}) {
  const darkSquareStyle: CSSProperties = {
    backgroundColor: isEditMode ? "#3f6f54" : "#315844",
  };
  const lightSquareStyle: CSSProperties = {
    backgroundColor: isEditMode ? "#8fba8c" : "#76966f",
  };
  const squareStyles: Record<string, CSSProperties> =
    isEditMode && selectedSquare
      ? {
          [selectedSquare]: {
            background:
              "linear-gradient(135deg, rgba(254, 240, 138, 0.65), rgba(250, 204, 21, 0.45))",
            boxShadow: "inset 0 0 0 3px rgba(254, 249, 195, 0.75)",
          },
        }
      : {};

  function handlePieceDrop({
    piece,
    sourceSquare,
    targetSquare,
  }: PieceDropHandlerArgs) {
    return (
      onMoveAttempt?.({
        piece: piece.pieceType,
        sourceSquare,
        targetSquare,
      }) ?? false
    );
  }

  function handlePieceClick({ isSparePiece, piece, square }: PieceHandlerArgs) {
    if (isSparePiece || !square) {
      return;
    }

    onRemoveAttempt?.({
      piece: piece.pieceType,
      square,
    });
  }

  function handleSquareClick({ square }: SquareHandlerArgs) {
    onSquareSelect?.({ square });
  }

  return (
    <div
      aria-label="Analysis chessboard"
      className={`aspect-square w-full max-w-[min(34rem,calc(100vw-2rem))] rounded-lg border p-1.5 shadow-inner transition sm:p-2 ${
        isEditMode
          ? "edit-mode-board border-amber-200/80 bg-emerald-950/30 shadow-emerald-800/30 ring-4 ring-amber-200/20"
          : "analysis-mode-board border-emerald-300/30 bg-neutral-950 shadow-emerald-950"
      }`}
      data-board-visual-state={isEditMode ? "edit" : "analysis"}
      data-edit-mode={isEditMode}
      data-fen={fen}
      data-interactive={isInteractive}
      data-orientation={orientation}
      data-remove-mode={isRemoveMode}
      data-selected-square={selectedSquare ?? ""}
      data-testid="static-board"
    >
      <div className="h-full w-full overflow-hidden rounded-lg">
        <Chessboard
          options={{
            id: "static-analysis-board",
            position: fen,
            boardOrientation: orientation,
            allowDragging: isInteractive,
            allowDrawingArrows: false,
            showAnimations: false,
            onPieceClick: isInteractive ? handlePieceClick : undefined,
            onPieceDrop: isInteractive ? handlePieceDrop : undefined,
            onSquareClick: isInteractive ? handleSquareClick : undefined,
            squareStyles,
            boardStyle: {
              borderRadius: "0.5rem",
              width: "100%",
              height: "100%",
            },
            darkSquareStyle,
            lightSquareStyle,
            darkSquareNotationStyle: {
              color: isEditMode ? "#ecfdf5" : "#d1fae5",
            },
            lightSquareNotationStyle: {
              color: isEditMode ? "#064e3b" : "#ecfdf5",
            },
          }}
        />
      </div>
    </div>
  );
}
