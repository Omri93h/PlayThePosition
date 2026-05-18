import type { CSSProperties } from "react";
import { useCallback, useMemo } from "react";
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

export type BoardSquarePress = {
  piece: string | null;
  square: string;
};

export type BoardOrientation = "white" | "black";

export function StaticBoard({
  fen = STATIC_ANALYSIS_FEN,
  orientation = "white",
  isEditMode = false,
  isInteractive = false,
  isRemoveMode = false,
  lastEditedSquare = null,
  onMoveAttempt,
  onRemoveAttempt,
  onSquarePress,
}: {
  fen?: string;
  orientation?: BoardOrientation;
  isEditMode?: boolean;
  isInteractive?: boolean;
  isRemoveMode?: boolean;
  lastEditedSquare?: string | null;
  onMoveAttempt?: (move: BoardMoveAttempt) => boolean | void;
  onRemoveAttempt?: (attempt: BoardRemoveAttempt) => void;
  onSquarePress?: (press: BoardSquarePress) => void;
}) {
  const darkSquareStyle = useMemo<CSSProperties>(
    () => ({
      backgroundColor: isEditMode ? "#3f6f54" : "#315844",
    }),
    [isEditMode],
  );
  const lightSquareStyle = useMemo<CSSProperties>(
    () => ({
      backgroundColor: isEditMode ? "#8fba8c" : "#76966f",
    }),
    [isEditMode],
  );
  const squareStyles = useMemo<Record<string, CSSProperties>>(() => {
    if (!isEditMode || !lastEditedSquare) {
      return {};
    }

    return {
      [lastEditedSquare]: {
        background:
          "linear-gradient(135deg, rgba(254, 240, 138, 0.28), rgba(250, 204, 21, 0.18))",
        boxShadow: "inset 0 0 0 2px rgba(254, 249, 195, 0.45)",
      },
    };
  }, [isEditMode, lastEditedSquare]);

  const handlePieceDrop = useCallback(
    ({ piece, sourceSquare, targetSquare }: PieceDropHandlerArgs) =>
      onMoveAttempt?.({
        piece: piece.pieceType,
        sourceSquare,
        targetSquare,
      }) ?? false,
    [onMoveAttempt],
  );

  const handlePieceClick = useCallback(
    ({ isSparePiece, piece, square }: PieceHandlerArgs) => {
      if (isSparePiece || !square) {
        return;
      }

      onRemoveAttempt?.({
        piece: piece.pieceType,
        square,
      });
    },
    [onRemoveAttempt],
  );

  const handleSquareClick = useCallback(
    ({ piece, square }: SquareHandlerArgs) => {
      onSquarePress?.({ piece: piece?.pieceType ?? null, square });
    },
    [onSquarePress],
  );

  const boardOptions = useMemo(
    () => ({
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
    }),
    [
      darkSquareStyle,
      fen,
      handlePieceClick,
      handlePieceDrop,
      handleSquareClick,
      isEditMode,
      isInteractive,
      lightSquareStyle,
      orientation,
      squareStyles,
    ],
  );

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
      data-delete-tool-active={isRemoveMode}
      data-last-edited-square={lastEditedSquare ?? ""}
      data-testid="static-board"
    >
      <div className="h-full w-full overflow-hidden rounded-lg">
        <Chessboard options={boardOptions} />
      </div>
    </div>
  );
}
