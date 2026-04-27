import { Chessboard } from "react-chessboard";

export const STATIC_ANALYSIS_FEN =
  "r2q1rk1/pp2bppp/2npbn2/2pNp3/2P1P3/2N2Q2/PP2BPPP/R1B2RK1 w - - 0 10";

export function StaticBoard({ fen = STATIC_ANALYSIS_FEN }: { fen?: string }) {
  return (
    <div
      aria-label="Analysis chessboard"
      className="aspect-square w-full max-w-[34rem] rounded-lg border border-emerald-300/30 bg-neutral-950 p-2 shadow-inner shadow-emerald-950"
      data-fen={fen}
      data-testid="static-board"
    >
      <div className="h-full w-full overflow-hidden rounded-lg">
        <Chessboard
          options={{
            id: "static-analysis-board",
            position: fen,
            allowDragging: false,
            allowDrawingArrows: false,
            showAnimations: false,
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
