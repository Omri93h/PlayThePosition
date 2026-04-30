import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("react-chessboard", () => ({
  Chessboard: ({
    options,
  }: {
    options: {
      allowDragging?: boolean;
      boardOrientation?: "white" | "black";
      onPieceClick?: (args: {
        isSparePiece: boolean;
        piece: { pieceType: string };
        square: string | null;
      }) => void;
      onPieceDrop?: (args: {
        piece: { isSparePiece: boolean; pieceType: string; position: string };
        sourceSquare: string;
        targetSquare: string | null;
      }) => boolean;
      onSquareClick?: (args: {
        piece: { pieceType: string } | null;
        square: string;
      }) => void;
      position?: string;
      squareStyles?: Record<string, unknown>;
      darkSquareStyle?: Record<string, unknown>;
      lightSquareStyle?: Record<string, unknown>;
    };
  }) => (
    <>
      <button
        type="button"
        data-interactive={String(options.allowDragging)}
        data-orientation={options.boardOrientation}
        data-position={options.position}
        data-square-styles={JSON.stringify(options.squareStyles ?? {})}
        data-dark-square-style={JSON.stringify(options.darkSquareStyle ?? {})}
        data-light-square-style={JSON.stringify(options.lightSquareStyle ?? {})}
        data-testid="mock-chessboard"
        onClick={() =>
          options.onPieceDrop?.({
            piece: { isSparePiece: false, pieceType: "wP", position: "c4" },
            sourceSquare: "c4",
            targetSquare: "e5",
          })
        }
      >
        Mock chessboard
      </button>
      <button
        type="button"
        data-testid="mock-piece"
        onClick={() =>
          options.onPieceClick?.({
            isSparePiece: false,
            piece: { pieceType: "wP" },
            square: "c4",
          })
        }
      >
        Mock piece
      </button>
      <button
        type="button"
        data-testid="mock-empty-square"
        onClick={() => options.onSquareClick?.({ piece: null, square: "d4" })}
      >
        Mock empty square
      </button>
      <button
        type="button"
        data-testid="mock-occupied-square"
        onClick={() =>
          options.onSquareClick?.({
            piece: { pieceType: "wP" },
            square: "c4",
          })
        }
      >
        Mock occupied square
      </button>
    </>
  ),
}));

import { App } from "./App";
import { AnalysisShell } from "./components/AnalysisShell";
import { STATIC_ANALYSIS_FEN } from "./components/StaticBoard";

const MOVED_STATIC_FEN =
  "r2q1rk1/pp2bppp/2npbn2/2pNP3/4P3/2N2Q2/PP2BPPP/R1B2RK1 w - - 0 10";
const REMOVED_STATIC_FEN =
  "r2q1rk1/pp2bppp/2npbn2/2pNp3/4P3/2N2Q2/PP2BPPP/R1B2RK1 w - - 0 10";
const ADDED_STATIC_FEN =
  "r2q1rk1/pp2bppp/2npbn2/2pNp3/2PQP3/2N2Q2/PP2BPPP/R1B2RK1 w - - 0 10";
const REPLACED_STATIC_FEN =
  "r2q1rk1/pp2bppp/2npbn2/2pNp3/2q1P3/2N2Q2/PP2BPPP/R1B2RK1 w - - 0 10";
const BLACK_TO_MOVE_STATIC_FEN =
  "r2q1rk1/pp2bppp/2npbn2/2pNp3/2P1P3/2N2Q2/PP2BPPP/R1B2RK1 b - - 0 10";

function mockClipboard(writeText = vi.fn().mockResolvedValue(undefined)) {
  Object.defineProperty(navigator, "clipboard", {
    configurable: true,
    value: { writeText },
  });

  return writeText;
}

function setPath(path: string) {
  window.history.pushState({}, "", path);
}

describe("App", () => {
  afterEach(() => {
    cleanup();
    vi.useRealTimers();
    vi.unstubAllGlobals();
    setPath("/");
  });

  it("renders the idle upload screen UI", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Upload a chess position screenshot" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Choose a board image")).toBeInTheDocument();
    expect(screen.getByText("Click to upload")).toBeInTheDocument();
    expect(
      screen.getByText("or drag and drop a chess screenshot here"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Choose chess screenshot")).toHaveAttribute(
      "type",
      "file",
    );
    expect(
      screen.queryByRole("button", { name: "Analysis shell" }),
    ).not.toBeInTheDocument();
  });

  it("opens file selection when the dropzone rectangle is clicked", () => {
    const inputClickSpy = vi
      .spyOn(HTMLInputElement.prototype, "click")
      .mockImplementation(() => undefined);

    render(<App />);

    fireEvent.click(screen.getByTestId("upload-dropzone"));

    expect(inputClickSpy).toHaveBeenCalledTimes(1);

    inputClickSpy.mockRestore();
  });

  it("loads a shared position route and renders the returned FEN", async () => {
    const sharedFen = "8/8/8/8/8/8/8/8 b - - 0 1";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "shared-123",
          fen: sharedFen,
          source: "share",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    setPath("/share/shared-123");

    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Loading shared position" }),
    ).toBeInTheDocument();

    expect(
      await screen.findByRole("heading", { name: "Position workspace" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute("data-fen", sharedFen);
    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/share/shared-123");
  });

  it("shows an error state when a shared position cannot be loaded", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            ok: false,
            error: {
              code: "share_not_found",
              message: "Shared position was not found.",
            },
          }),
          { status: 404, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );
    setPath("/share/missing");

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Shared position was not found.",
    );
    expect(
      screen.getByRole("heading", { name: "Shared position unavailable" }),
    ).toBeInTheDocument();
  });

  it("renders the static analysis shell areas with a static board", () => {
    render(<AnalysisShell />);

    expect(
      screen.getByRole("heading", { name: "Position workspace" }),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Analysis chessboard")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-interactive",
      "true",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-orientation",
      "white",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-edit-mode",
      "false",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-board-visual-state",
      "analysis",
    );
    expect(screen.getByTestId("static-board")).toHaveClass("analysis-mode-board");
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-remove-mode",
      "false",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "",
    );
    expect(screen.getByTestId("mock-chessboard")).toHaveAttribute(
      "data-interactive",
      "true",
    );
    expect(
      screen.getByTestId("mock-chessboard").getAttribute("data-dark-square-style"),
    ).toContain("backgroundColor");
    expect(
      screen.getByTestId("mock-chessboard").getAttribute("data-light-square-style"),
    ).toContain("backgroundColor");
    expect(screen.getByLabelText("Analysis actions")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Edit mode" })).toHaveTextContent("Edit");
    expect(screen.getByTestId("analysis-action-buttons")).toHaveClass("justify-center");
    expect(screen.getByTestId("analysis-action-buttons")).toHaveTextContent("FEN");
    expect(screen.getByTestId("analysis-action-buttons")).toHaveTextContent("Share");
    expect(screen.getByTestId("analysis-action-buttons")).toHaveTextContent("Reset");
    expect(screen.getByTestId("analysis-action-buttons")).toHaveTextContent("Flip");
    expect(screen.getByRole("button", { name: "Copy FEN" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Share" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Reset" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Flip" })).toBeInTheDocument();
    expect(screen.getByTestId("side-to-move-group")).toHaveClass("gap-2");
    expect(screen.getByTestId("side-to-move-group")).toContainElement(
      screen.getByRole("button", { name: "White" }),
    );
    expect(screen.getByTestId("side-to-move-group")).toContainElement(
      screen.getByRole("button", { name: "Black" }),
    );
    expect(screen.getByRole("button", { name: "White" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("button", { name: "Black" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
    expect(
      screen.queryByRole("button", { name: "Remove piece" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Undo" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Redo" })).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "White queen" }),
    ).not.toBeInTheDocument();
  });

  it("toggles edit mode visual state without mutating the board", () => {
    render(<AnalysisShell />);

    const editModeToggle = screen.getByRole("button", { name: "Edit mode" });

    expect(editModeToggle).toHaveAttribute("aria-pressed", "false");
    expect(
      screen.queryByRole("button", { name: "Remove piece" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "White queen" }),
    ).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Black" })).toBeInTheDocument();
    expect(screen.queryByText("Edit mode inactive.")).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-edit-mode",
      "false",
    );

    fireEvent.click(editModeToggle);

    expect(editModeToggle).toHaveAttribute("aria-pressed", "true");
    expect(screen.getByRole("button", { name: "Remove piece" })).toBeEnabled();
    expect(screen.getByLabelText("Edit tools")).toContainElement(
      screen.getByRole("button", { name: "Remove piece" }),
    );
    expect(screen.getByRole("button", { name: "White queen" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Black" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Redo" })).toBeDisabled();
    expect(screen.getByTestId("analysis-action-buttons")).toHaveTextContent("Undo");
    expect(screen.getByTestId("analysis-action-buttons")).toHaveTextContent("Redo");
    expect(screen.getByText("Edit mode active.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-edit-mode",
      "true",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-board-visual-state",
      "edit",
    );
    expect(screen.getByTestId("static-board")).toHaveClass("edit-mode-board");
    expect(screen.getByLabelText("Edit tools")).toHaveTextContent("Remove");
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "",
    );
  });

  it("copies the current fallback FEN outside edit mode", async () => {
    const writeText = mockClipboard();

    render(<AnalysisShell />);

    fireEvent.click(screen.getByRole("button", { name: "Copy FEN" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(STATIC_ANALYSIS_FEN);
    });
    expect(await screen.findByText("FEN copied.")).toBeInTheDocument();
  });

  it("creates a share link for the current fallback FEN outside edit mode", async () => {
    const shareUrl = new URL("/share/generated-123", window.location.origin).toString();
    const writeText = mockClipboard();
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "generated-123",
          path: "/share/generated-123",
          fen: STATIC_ANALYSIS_FEN,
          source: "share",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<AnalysisShell />);

    fireEvent.click(screen.getByRole("button", { name: "Share" }));

    expect(await screen.findByText("Share link copied.")).toBeInTheDocument();
    expect(screen.getByRole("link", { name: shareUrl })).toHaveAttribute(
      "href",
      shareUrl,
    );
    expect(writeText).toHaveBeenCalledWith(shareUrl);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/share",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fen: STATIC_ANALYSIS_FEN }),
      }),
    );
  });

  it("shows an error state when share creation fails", async () => {
    mockClipboard();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            ok: false,
            error: {
              code: "share_failed",
              message: "Share link could not be created.",
            },
          }),
          { status: 500, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    render(<AnalysisShell />);

    fireEvent.click(screen.getByRole("button", { name: "Share" }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Share link could not be created.",
    );
    expect(screen.queryByText("Share link copied.")).not.toBeInTheDocument();
  });

  it("shows a copy failure state when clipboard writing fails", async () => {
    mockClipboard(vi.fn().mockRejectedValue(new Error("Permission denied")));

    render(<AnalysisShell />);

    fireEvent.click(screen.getByRole("button", { name: "Copy FEN" }));

    expect(await screen.findByText("Could not copy FEN.")).toBeInTheDocument();
  });

  it("updates side to move metadata without enabling edit mode", async () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Black" }));

    expect(screen.queryByRole("button", { name: "Undo" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Redo" })).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      BLACK_TO_MOVE_STATIC_FEN,
    );
    expect(screen.getByRole("button", { name: "Black" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );

    const writeText = mockClipboard();

    fireEvent.click(screen.getByRole("button", { name: "Copy FEN" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(BLACK_TO_MOVE_STATIC_FEN);
    });

    fireEvent.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByRole("button", { name: "White" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
  });

  it("shares updated side-to-move metadata", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "black-to-move",
          path: "/share/black-to-move",
          fen: BLACK_TO_MOVE_STATIC_FEN,
          source: "share",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    mockClipboard();

    render(<AnalysisShell />);

    fireEvent.click(screen.getByRole("button", { name: "Black" }));
    fireEvent.click(screen.getByRole("button", { name: "Share" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://127.0.0.1:8000/share",
        expect.objectContaining({
          body: JSON.stringify({ fen: BLACK_TO_MOVE_STATIC_FEN }),
        }),
      );
    });
  });

  it("keeps add-piece controls non-mutating outside edit mode", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByTestId("mock-empty-square"));

    expect(screen.queryByText("No piece selected.")).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "",
    );
  });

  it("highlights a selected piece square while edit mode is active", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByTestId("mock-piece"));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "c4",
    );
    expect(
      screen.getByTestId("mock-chessboard").getAttribute("data-square-styles"),
    ).toContain("c4");
  });

  it("adds selected pieces while edit mode is active", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByRole("button", { name: "White queen" }));
    fireEvent.click(screen.getByTestId("mock-empty-square"));

    expect(screen.getByText("Selected piece: wQ.")).toBeInTheDocument();
    expect(screen.getByText("Last interaction: Place wQ on d4.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      ADDED_STATIC_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "d4",
    );
    expect(screen.getByRole("button", { name: "Undo" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Redo" })).toBeDisabled();

    fireEvent.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "",
    );
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Redo" })).toBeDisabled();
    expect(screen.getByText("No piece selected.")).toBeInTheDocument();
  });

  it("undoes and redoes add-piece edits", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByRole("button", { name: "White queen" }));
    fireEvent.click(screen.getByTestId("mock-empty-square"));

    fireEvent.click(screen.getByRole("button", { name: "Undo" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByText("Last interaction: Undo edit.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Redo" })).toBeEnabled();

    fireEvent.click(screen.getByRole("button", { name: "Redo" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      ADDED_STATIC_FEN,
    );
    expect(screen.getByText("Last interaction: Redo edit.")).toBeInTheDocument();
  });

  it("replaces occupied squares when adding a selected piece", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByRole("button", { name: "Black queen" }));
    fireEvent.click(screen.getByTestId("mock-occupied-square"));

    expect(screen.getByText("Last interaction: Place bQ on c4.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      REPLACED_STATIC_FEN,
    );
  });

  it("keeps remove attempts non-mutating outside edit mode", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByTestId("mock-piece"));

    expect(
      screen.queryByText("Last interaction: Remove wP from c4."),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
  });

  it("removes pieces while remove mode is active", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByRole("button", { name: "Remove piece" }));
    fireEvent.click(screen.getByTestId("mock-piece"));

    expect(
      screen.getByText("Last interaction: Remove wP from c4."),
    ).toBeInTheDocument();
    expect(screen.getByText("Remove tool active.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-remove-mode",
      "true",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "c4",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      REMOVED_STATIC_FEN,
    );

    fireEvent.click(screen.getByRole("button", { name: "Undo" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );

    fireEvent.click(screen.getByRole("button", { name: "Redo" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      REMOVED_STATIC_FEN,
    );

    fireEvent.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-remove-mode",
      "false",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "",
    );
  });

  it("keeps board interaction attempts non-mutating outside edit mode", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByTestId("mock-chessboard"));

    expect(
      screen.queryByText("Last interaction: wP c4 to e5."),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
  });

  it("moves pieces freely while edit mode is active", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByTestId("mock-chessboard"));

    expect(screen.getByText("Last interaction: wP c4 to e5.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      MOVED_STATIC_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "e5",
    );

    fireEvent.click(screen.getByRole("button", { name: "Undo" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );

    fireEvent.click(screen.getByRole("button", { name: "Redo" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      MOVED_STATIC_FEN,
    );

    fireEvent.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Redo" })).toBeDisabled();
  });

  it("copies edited FEN and then reset FEN", async () => {
    const writeText = mockClipboard();

    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByTestId("mock-chessboard"));

    fireEvent.click(screen.getByRole("button", { name: "Copy FEN" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenLastCalledWith(MOVED_STATIC_FEN);
    });

    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    fireEvent.click(screen.getByRole("button", { name: "Copy FEN" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenLastCalledWith(STATIC_ANALYSIS_FEN);
    });
  });

  it("shares edited FEN after a move", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          id: "moved-position",
          path: "/share/moved-position",
          fen: MOVED_STATIC_FEN,
          source: "share",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);
    mockClipboard();

    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByTestId("mock-chessboard"));
    fireEvent.click(screen.getByRole("button", { name: "Share" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        "http://127.0.0.1:8000/share",
        expect.objectContaining({
          body: JSON.stringify({ fen: MOVED_STATIC_FEN }),
        }),
      );
    });
  });

  it("clears redo history after a new edit follows undo", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit mode" }));
    fireEvent.click(screen.getByRole("button", { name: "White queen" }));
    fireEvent.click(screen.getByTestId("mock-empty-square"));
    fireEvent.click(screen.getByRole("button", { name: "Undo" }));

    expect(screen.getByRole("button", { name: "Redo" })).toBeEnabled();

    fireEvent.click(screen.getByRole("button", { name: "Black queen" }));
    fireEvent.click(screen.getByTestId("mock-occupied-square"));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      REPLACED_STATIC_FEN,
    );
    expect(screen.getByRole("button", { name: "Redo" })).toBeDisabled();
  });

  it("flips board orientation and resets session state", () => {
    render(<AnalysisShell />);

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-orientation",
      "white",
    );

    fireEvent.click(screen.getByRole("button", { name: "Flip" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-orientation",
      "black",
    );

    fireEvent.click(screen.getByTestId("mock-chessboard"));
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-orientation",
      "white",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-selected-square",
      "",
    );
    expect(screen.queryByText("Board interaction ready.")).not.toBeInTheDocument();
  });

  it("updates drag presentation without uploading", () => {
    render(<App />);

    const dropzone = screen.getByTestId("upload-dropzone");

    fireEvent.dragEnter(dropzone);

    expect(screen.getByText("Drop screenshot here")).toBeInTheDocument();
    expect(
      screen.getByText("Release to return to the upload prompt."),
    ).toBeInTheDocument();

    fireEvent.dragLeave(dropzone);

    expect(screen.getByText("Choose a board image")).toBeInTheDocument();
  });

  it("uploads a selected file and opens the analysis board with the returned FEN", async () => {
    vi.useFakeTimers();
    const uploadedFen = "8/8/8/8/8/8/8/8 w - - 0 1";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          fen: uploadedFen,
          source: "placeholder",
          confidence: null,
          message: "Received position.png; detection is not implemented yet.",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    const input = screen.getByLabelText("Choose chess screenshot");
    const file = new File(["fake image"], "position.png", { type: "image/png" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByTestId("upload-dropzone")).toHaveAttribute("aria-busy", "true");
    expect(screen.getByRole("dialog")).toBeInTheDocument();
    expect(screen.getByText("Uploading image")).toBeInTheDocument();
    expect(screen.getByText("Uploading screenshot")).toBeInTheDocument();

    await flushPromises();

    expect(screen.getByText("Analyzing position")).toBeInTheDocument();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(120);
    });

    expect(screen.getByText("Opening board")).toBeInTheDocument();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(120);
    });

    expect(
      screen.getByRole("heading", { name: "Position workspace" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    vi.useRealTimers();
    expect(screen.getByTestId("static-board")).toHaveAttribute("data-fen", uploadedFen);
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-orientation",
      "white",
    );

    const writeText = mockClipboard();

    fireEvent.click(screen.getByRole("button", { name: "Copy FEN" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenCalledWith(uploadedFen);
    });

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/upload",
      expect.objectContaining({ method: "POST", body: expect.any(FormData) }),
    );
  });

  it("uploads a dropped file and opens the analysis board with the returned FEN", async () => {
    vi.useFakeTimers();
    const uploadedFen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w - - 0 1";
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          fen: uploadedFen,
          source: "placeholder",
          confidence: null,
          message: "Received dropped-position.png; detection is not implemented yet.",
        }),
        { status: 200, headers: { "Content-Type": "application/json" } },
      ),
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    const dropzone = screen.getByTestId("upload-dropzone");
    const file = new File(["fake image"], "dropped-position.png", {
      type: "image/png",
    });

    fireEvent.drop(dropzone, {
      dataTransfer: {
        files: {
          item: () => file,
          0: file,
        },
      },
    });

    expect(screen.getByText("Uploading image")).toBeInTheDocument();

    await flushPromises();

    expect(screen.getByText("Analyzing position")).toBeInTheDocument();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(120);
    });

    expect(screen.getByText("Opening board")).toBeInTheDocument();

    await act(async () => {
      await vi.advanceTimersByTimeAsync(120);
    });

    expect(
      screen.getByRole("heading", { name: "Position workspace" }),
    ).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute("data-fen", uploadedFen);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/upload",
      expect.objectContaining({ method: "POST", body: expect.any(FormData) }),
    );
  });

  it("displays structured API errors", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            ok: false,
            error: {
              code: "unsupported_file_type",
              message: "Only PNG and JPEG images are supported.",
            },
          }),
          { status: 415, headers: { "Content-Type": "application/json" } },
        ),
      ),
    );

    render(<App />);

    const input = screen.getByLabelText("Choose chess screenshot");
    const file = new File(["not image"], "position.txt", { type: "text/plain" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByText("Uploading image")).toBeInTheDocument();

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Only PNG and JPEG images are supported.",
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  it("displays network failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Failed to fetch")));

    render(<App />);

    const input = screen.getByLabelText("Choose chess screenshot");
    const file = new File(["fake image"], "position.png", { type: "image/png" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByText("Uploading image")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Network error. Check your connection and try again.",
      );
    });
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Retry upload" }));

    expect(screen.getByText("Ready to retry")).toBeInTheDocument();
    expect(screen.getByTestId("upload-dropzone")).toHaveAttribute("aria-busy", "false");
  });
});

async function flushPromises() {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}
