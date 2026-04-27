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
  onMoveAttempt,
  onRemoveAttempt,
  onSquareSelect,
}: {
  fen?: string;
  orientation?: BoardOrientation;
  isEditMode?: boolean;
  isInteractive?: boolean;
  isRemoveMode?: boolean;
  onMoveAttempt?: (move: BoardMoveAttempt) => boolean | void;
  onRemoveAttempt?: (attempt: BoardRemoveAttempt) => void;
  onSquareSelect?: (selection: BoardSquareSelection) => void;
}) {
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
      className={`aspect-square w-full max-w-[34rem] rounded-lg border bg-neutral-950 p-2 shadow-inner shadow-emerald-950 transition ${
        isEditMode
          ? "border-emerald-200 ring-2 ring-emerald-300/30"
          : "border-emerald-300/30"
      }`}
      data-edit-mode={isEditMode}
      data-fen={fen}
      data-interactive={isInteractive}
      data-orientation={orientation}
      data-remove-mode={isRemoveMode}
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
            boardStyle: {
              borderRadius: "0.5rem",
              width: "100%",
              height: "100%",
            },
            darkSquareStyle: {
              backgroundColor: "#1f2937",
            },
            lightSquareStyle: {
              backgroundColor: "#475569",
            },
            darkSquareNotationStyle: {
              color: "#d1fae5",
            },
            lightSquareNotationStyle: {
              color: "#ecfdf5",
            },
          }}
        />
      </div>
    </div>
  );
}
