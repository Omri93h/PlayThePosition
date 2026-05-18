import {
  act,
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { subscribeToAnalytics } from "./analytics";
import type { AnalyticsEvent } from "./analytics";

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
    expect(screen.queryByRole("button", { name: "New Image" })).not.toBeInTheDocument();
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

    expect(await screen.findByTestId("static-board")).toBeInTheDocument();
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
      "This shared board could not be opened.",
    );
    expect(
      screen.getByRole("heading", { name: "Shared position unavailable" }),
    ).toBeInTheDocument();
    expect(
      screen.getByText(/Start a new upload to rebuild the position/),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Start from upload" })).toHaveAttribute(
      "href",
      "/",
    );
  });

  it("renders the static analysis shell areas with a static board", () => {
    render(<AnalysisShell />);

    expect(screen.queryByText("Analysis board")).not.toBeInTheDocument();
    expect(screen.queryByText("Position workspace")).not.toBeInTheDocument();
    expect(screen.getByLabelText("Analysis board")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-shell")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-board-card")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-primary-controls")).toBeInTheDocument();
    expect(screen.getByTestId("board-mode-toggle")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-board-frame")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-actions")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-feedback")).toBeInTheDocument();
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
      "data-delete-tool-active",
      "false",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
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
    expect(screen.getByRole("button", { name: "Play" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByRole("button", { name: "Edit Board" })).toHaveTextContent(
      "Edit Board",
    );
    expect(screen.getByRole("button", { name: "Edit Board" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
    expect(screen.getByTestId("play-controls-row")).toContainElement(
      screen.getByTestId("position-metadata-controls"),
    );
    expect(screen.getByTestId("play-controls-row")).toContainElement(
      screen.getByTestId("primary-board-actions"),
    );
    expect(screen.getByTestId("position-metadata-controls")).toHaveClass(
      "border-neutral-700",
    );
    expect(screen.getByTestId("primary-board-actions")).toHaveTextContent("Flip");
    expect(screen.getByTestId("primary-board-actions")).toHaveTextContent("Reset");
    expect(screen.getByTestId("secondary-share-actions")).toHaveTextContent("Share");
    expect(screen.queryByRole("button", { name: "Copy FEN" })).not.toBeInTheDocument();
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
    expect(screen.getByRole("button", { name: "White" })).toHaveClass("bg-white");
    expect(screen.getByRole("button", { name: "Black" })).toHaveClass("bg-neutral-950");
    expect(screen.getByRole("button", { name: "Black" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
    expect(
      screen.queryByRole("button", { name: "Delete pieces" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "Place pieces" }),
    ).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Undo" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Redo" })).not.toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: "White queen" }),
    ).not.toBeInTheDocument();
  });

  it("toggles edit mode visual state without mutating the board", () => {
    const analytics = captureAnalytics();

    render(<AnalysisShell />);

    const editModeToggle = screen.getByRole("button", { name: "Edit Board" });

    expect(editModeToggle).toHaveAttribute("aria-pressed", "false");
    expect(screen.getByRole("button", { name: "Play" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(
      screen.queryByRole("button", { name: "Delete pieces" }),
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
    expect(screen.getByRole("button", { name: "Play" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
    expect(screen.getByRole("button", { name: "Delete pieces" })).toBeEnabled();
    expect(screen.getByRole("button", { name: "Place pieces" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByLabelText("Edit tools")).toContainElement(
      screen.getByRole("button", { name: "Delete pieces" }),
    );
    expect(screen.getByTestId("edit-tools-panel")).toBeInTheDocument();
    expect(screen.getByTestId("analysis-actions")).toContainElement(
      screen.getByTestId("edit-tools-panel"),
    );
    expect(screen.getByTestId("edit-tool-mode-controls")).toBeInTheDocument();
    expect(screen.getByTestId("piece-palette")).toBeInTheDocument();
    expect(screen.getByTestId("piece-palette-grid")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "White queen" })).toBeEnabled();
    expect(screen.queryByTestId("position-metadata-controls")).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Black" })).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Redo" })).toBeDisabled();
    expect(screen.getByTestId("edit-history-actions")).toHaveTextContent("Undo");
    expect(screen.getByTestId("edit-history-actions")).toHaveTextContent("Redo");
    expect(screen.getByTestId("edit-utility-actions")).toHaveTextContent("Flip");
    expect(screen.getByTestId("edit-utility-actions")).toHaveTextContent("Reset");
    expect(screen.queryByRole("button", { name: "Share" })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: "Copy FEN" })).not.toBeInTheDocument();
    expect(screen.queryByText("Edit Board active.")).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-edit-mode",
      "true",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-board-visual-state",
      "edit",
    );
    expect(screen.getByTestId("static-board")).toHaveClass("edit-mode-board");
    expect(screen.getByLabelText("Edit tools")).toHaveTextContent("Place");
    expect(screen.getByLabelText("Edit tools")).toHaveTextContent("Delete");
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
      "",
    );
    expect(analytics.events).toContainEqual({
      name: "edit_mode_opened",
      payload: { fen_length: STATIC_ANALYSIS_FEN.length },
    });
    expectAnalyticsEventsAreSafe(analytics.events, STATIC_ANALYSIS_FEN);
    analytics.unsubscribe();
  });

  it("creates a share link for the current fallback FEN outside edit mode", async () => {
    const analytics = captureAnalytics();
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

    expect(
      await screen.findByRole("dialog", { name: "Share position" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Share link ready.")).toBeInTheDocument();
    expect(screen.getByRole("textbox", { name: "Share link" })).toHaveValue(shareUrl);
    expect(screen.getByRole("textbox", { name: "Share link" })).toHaveAttribute(
      "readonly",
    );
    expect(screen.getByRole("textbox", { name: "Current FEN" })).toHaveValue(
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByRole("textbox", { name: "Current FEN" })).toHaveAttribute(
      "readonly",
    );
    expect(writeText).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole("button", { name: "Copy share link" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenLastCalledWith(shareUrl);
    });
    expect(screen.getByText("Share link copied.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Copy current FEN" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenLastCalledWith(STATIC_ANALYSIS_FEN);
    });
    expect(screen.getByText("Current FEN copied.")).toBeInTheDocument();
    expect(analytics.events).toContainEqual({
      name: "fen_copied",
      payload: { fen_length: STATIC_ANALYSIS_FEN.length },
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/share",
      expect.objectContaining({
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fen: STATIC_ANALYSIS_FEN }),
      }),
    );
    expect(analytics.events).toContainEqual({
      name: "share_created",
      payload: {
        fen_length: STATIC_ANALYSIS_FEN.length,
        share_path_length: "/share/generated-123".length,
      },
    });
    expectAnalyticsEventsAreSafe(analytics.events, STATIC_ANALYSIS_FEN);
    analytics.unsubscribe();
  });

  it("shows an error state when share creation fails", async () => {
    const analytics = captureAnalytics();
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
      "Could not create a share link. Try again in a moment.",
    );
    expect(screen.getByRole("button", { name: "Share" })).toBeEnabled();
    expect(screen.queryByText("Share link copied.")).not.toBeInTheDocument();
    expect(analytics.events).toContainEqual({
      name: "share_failed",
      payload: {
        reason: "api_error",
        fen_length: STATIC_ANALYSIS_FEN.length,
      },
    });
    expectAnalyticsEventsAreSafe(analytics.events, STATIC_ANALYSIS_FEN);
    analytics.unsubscribe();
  });

  it("shows a modal FEN copy failure state when clipboard writing fails", async () => {
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
    mockClipboard(vi.fn().mockRejectedValue(new Error("Permission denied")));

    render(<AnalysisShell />);

    fireEvent.click(screen.getByRole("button", { name: "Share" }));
    expect(
      await screen.findByRole("dialog", { name: "Share position" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Copy current FEN" }));

    expect(await screen.findByText("Could not copy current FEN.")).toBeInTheDocument();
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

    expect(screen.queryByTestId("edit-tools-panel")).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
      "",
    );
  });

  it("keeps board piece clicks non-selecting in edit place mode", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
    fireEvent.click(screen.getByTestId("mock-piece"));

    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
      "",
    );
    expect(
      screen.getByTestId("mock-chessboard").getAttribute("data-square-styles"),
    ).toBe("{}");
  });

  it("places the active palette piece while edit mode is active", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
    expect(screen.getByLabelText("Active piece palette")).toHaveTextContent(
      "Active piece",
    );
    const whiteQueen = screen.getByRole("button", { name: "White queen" });
    fireEvent.click(whiteQueen);
    fireEvent.click(screen.getByTestId("mock-empty-square"));

    expect(whiteQueen).toHaveClass("ring-2");
    expect(whiteQueen).toHaveClass("bg-white");
    expect(whiteQueen).toHaveClass("text-neutral-950");
    expect(whiteQueen).toHaveAttribute("data-piece-color", "white");
    expect(screen.getByText("Last interaction: Place Q on d4.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      ADDED_STATIC_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
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
      "data-last-edited-square",
      "",
    );
    expect(screen.getByRole("button", { name: "Undo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "Redo" })).toBeDisabled();
    expect(screen.getByRole("button", { name: "White queen" })).toHaveAttribute(
      "aria-pressed",
      "false",
    );
  });

  it("undoes and redoes add-piece edits", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
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

  it("places white and black active palette pieces with the correct FEN color", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
    fireEvent.click(screen.getByRole("button", { name: "White queen" }));
    fireEvent.click(screen.getByTestId("mock-empty-square"));

    expect(screen.getByText("Last interaction: Place Q on d4.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      ADDED_STATIC_FEN,
    );

    fireEvent.click(screen.getByRole("button", { name: "Undo" }));
    fireEvent.click(screen.getByRole("button", { name: "Black queen" }));
    expect(screen.getByRole("button", { name: "Black queen" })).toHaveClass("bg-white");
    expect(screen.getByRole("button", { name: "Black queen" })).toHaveClass(
      "text-neutral-950",
    );
    expect(screen.getByRole("button", { name: "Black queen" })).toHaveAttribute(
      "data-piece-color",
      "black",
    );
    fireEvent.click(screen.getByTestId("mock-occupied-square"));

    expect(screen.getByText("Last interaction: Place q on c4.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      REPLACED_STATIC_FEN,
    );
  });

  it("keeps delete attempts non-mutating outside edit mode", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByTestId("mock-piece"));

    expect(
      screen.queryByText("Last interaction: Deleted wP from c4."),
    ).not.toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      STATIC_ANALYSIS_FEN,
    );
  });

  it("deletes pieces while delete tool is active", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
    expect(screen.getByRole("button", { name: "Place pieces" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    fireEvent.click(screen.getByRole("button", { name: "Delete pieces" }));
    fireEvent.click(screen.getByTestId("mock-occupied-square"));

    expect(
      screen.getByText("Last interaction: Deleted wP from c4."),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Delete pieces" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-delete-tool-active",
      "true",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
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
      "data-delete-tool-active",
      "false",
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
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
    expect(screen.queryByText(/legal moves/i)).not.toBeInTheDocument();
  });

  it("moves pieces freely while edit mode is active", () => {
    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
    fireEvent.click(screen.getByTestId("mock-chessboard"));

    expect(screen.getByText("Last interaction: wP c4 to e5.")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-fen",
      MOVED_STATIC_FEN,
    );
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-last-edited-square",
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

  it("copies edited FEN and then reset FEN from the share modal", async () => {
    const writeText = mockClipboard();
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            id: "moved-position",
            path: "/share/moved-position",
            fen: MOVED_STATIC_FEN,
            source: "share",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      )
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            id: "reset-position",
            path: "/share/reset-position",
            fen: STATIC_ANALYSIS_FEN,
            source: "share",
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<AnalysisShell />);
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
    fireEvent.click(screen.getByTestId("mock-chessboard"));
    fireEvent.click(screen.getByRole("button", { name: "Play" }));

    fireEvent.click(screen.getByRole("button", { name: "Share" }));
    expect(
      await screen.findByRole("dialog", { name: "Share position" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Copy current FEN" }));

    await waitFor(() => {
      expect(writeText).toHaveBeenLastCalledWith(MOVED_STATIC_FEN);
    });

    fireEvent.click(screen.getByRole("button", { name: "Close share dialog" }));
    fireEvent.click(screen.getByRole("button", { name: "Reset" }));
    fireEvent.click(screen.getByRole("button", { name: "Share" }));
    expect(
      await screen.findByRole("dialog", { name: "Share position" }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Copy current FEN" }));

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
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
    fireEvent.click(screen.getByTestId("mock-chessboard"));
    fireEvent.click(screen.getByRole("button", { name: "Play" }));
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
    fireEvent.click(screen.getByRole("button", { name: "Edit Board" }));
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
    expect(screen.getByRole("button", { name: "Flip" })).not.toHaveAttribute(
      "aria-pressed",
    );
    expect(screen.getByRole("button", { name: "Reset" })).not.toHaveAttribute(
      "aria-pressed",
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
      "data-last-edited-square",
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
    const analytics = captureAnalytics();
    try {
      const uploadedFen = "8/8/8/8/8/8/8/8 w - - 0 1";
      const replacementFen = "8/8/8/8/8/8/8/8 b - - 0 1";
      const fetchMock = vi
        .fn()
        .mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              fen: uploadedFen,
              source: "placeholder",
              confidence: null,
              message: "Received position.png; detection is not implemented yet.",
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          ),
        )
        .mockResolvedValueOnce(
          new Response(
            JSON.stringify({
              fen: replacementFen,
              source: "placeholder",
              confidence: null,
              message:
                "Received replacement-position.png; detection is not implemented yet.",
            }),
            { status: 200, headers: { "Content-Type": "application/json" } },
          ),
        );
      vi.stubGlobal("fetch", fetchMock);

      render(<App />);

      const input = screen.getByLabelText("Choose chess screenshot");
      const file = new File(["fake image"], "position.png", { type: "image/png" });

      fireEvent.change(input, { target: { files: [file] } });

      expect(screen.getByTestId("upload-dropzone")).toHaveAttribute(
        "aria-busy",
        "true",
      );
      expect(screen.getByRole("dialog")).toBeInTheDocument();
      expect(screen.getByText("Uploading image")).toBeInTheDocument();
      expect(screen.getByText("Uploading screenshot")).toBeInTheDocument();

      await flushPromises();

      expect(screen.getByText("Analyzing position")).toBeInTheDocument();

      await advanceNextUploadStage();

      expect(screen.getByText("Opening board")).toBeInTheDocument();

      await advanceNextUploadStage();

      expect(screen.getByTestId("static-board")).toBeInTheDocument();
      expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-fen",
        uploadedFen,
      );
      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-edit-mode",
        "true",
      );
      expect(screen.getByRole("button", { name: "Edit Board" })).toHaveAttribute(
        "aria-pressed",
        "true",
      );
      expect(screen.getByText(/Position needs review/)).toBeInTheDocument();
      expect(screen.getByText(/Correct the pieces in Edit Board/)).toBeInTheDocument();
      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-orientation",
        "white",
      );

      expect(fetchMock).toHaveBeenCalledWith(
        "http://127.0.0.1:8000/upload",
        expect.objectContaining({ method: "POST", body: expect.any(FormData) }),
      );
      expect(analytics.events).toEqual(
        expect.arrayContaining([
          {
            name: "upload_started",
            payload: {
              file_type: "image/png",
              file_size_bucket: "under_100kb",
            },
          },
          {
            name: "upload_success",
            payload: {
              source: "placeholder",
              fen_length: uploadedFen.length,
              confidence_available: false,
            },
          },
          {
            name: "analysis_opened",
            payload: {
              source: "placeholder",
              fen_length: uploadedFen.length,
            },
          },
        ]),
      );
      expectAnalyticsEventsAreSafe(analytics.events, uploadedFen);
      expect(screen.getByTestId("app-header")).toContainElement(
        screen.getByRole("button", { name: "New Image" }),
      );

      const inputClickSpy = vi
        .spyOn(HTMLInputElement.prototype, "click")
        .mockImplementation(() => undefined);

      fireEvent.click(screen.getByRole("button", { name: "New Image" }));

      expect(inputClickSpy).toHaveBeenCalled();
      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-fen",
        uploadedFen,
      );

      inputClickSpy.mockRestore();

      fireEvent.change(screen.getByLabelText("Choose another chess screenshot"), {
        target: {
          files: [
            new File(["replacement image"], "replacement-position.png", {
              type: "image/png",
            }),
          ],
        },
      });

      expect(screen.getByText("Uploading image")).toBeInTheDocument();

      await flushPromises();

      expect(screen.getByText("Analyzing position")).toBeInTheDocument();

      await advanceNextUploadStage();

      expect(screen.getByText("Opening board")).toBeInTheDocument();

      await advanceNextUploadStage();

      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-fen",
        replacementFen,
      );
      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-edit-mode",
        "true",
      );
    } finally {
      vi.useRealTimers();
      analytics.unsubscribe();
    }
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

    await advanceNextUploadStage();

    expect(screen.getByText("Opening board")).toBeInTheDocument();

    await advanceNextUploadStage();

    expect(screen.getByTestId("static-board")).toBeInTheDocument();
    expect(screen.getByTestId("static-board")).toHaveAttribute("data-fen", uploadedFen);
    expect(screen.getByTestId("static-board")).toHaveAttribute(
      "data-edit-mode",
      "true",
    );
    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/upload",
      expect.objectContaining({ method: "POST", body: expect.any(FormData) }),
    );
  });

  it.each([
    ["placeholder", "placeholder"],
    ["partial", "gated_detection_orchestrator"],
    ["failed", "gated_detection_orchestrator"],
  ])(
    "opens %s upload detection results in Edit Board fallback mode",
    async (status, source) => {
      vi.useFakeTimers();
      const topLevelFen = "8/8/8/8/8/8/8/8 w - - 0 1";
      const metadataFen = "4k3/8/8/8/8/8/8/4K3 b - - 0 1";
      const fetchMock = vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            fen: topLevelFen,
            source,
            confidence: null,
            message:
              "Detection needs review. Open the editable board and correct the position manually.",
            detection: {
              status,
              source: "gated_detection_orchestrator",
              confidence: null,
              fen: metadataFen,
              orientation: "unknown",
              stages: [],
              failure:
                status === "placeholder"
                  ? null
                  : {
                      code: "low_confidence",
                      message: "Detection result confidence is below threshold.",
                      stage: "fen",
                      retryable: true,
                      suggestion: "Review and correct the board manually.",
                    },
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      );
      vi.stubGlobal("fetch", fetchMock);

      try {
        render(<App />);

        await uploadSelectedFile();

        expect(screen.getByTestId("static-board")).toHaveAttribute(
          "data-fen",
          topLevelFen,
        );
        expect(screen.getByTestId("static-board")).not.toHaveAttribute(
          "data-fen",
          metadataFen,
        );
        expect(screen.getByTestId("static-board")).toHaveAttribute(
          "data-edit-mode",
          "true",
        );
        expect(screen.getByRole("button", { name: "Edit Board" })).toHaveAttribute(
          "aria-pressed",
          "true",
        );
        expect(screen.getByText(/Position needs review/)).toBeInTheDocument();
        expect(screen.getByText(/We opened a safe fallback board/)).toBeInTheDocument();
        expect(screen.queryByText(/recognized/i)).not.toBeInTheDocument();
        expect(screen.queryByText(/detected successfully/i)).not.toBeInTheDocument();
      } finally {
        vi.useRealTimers();
      }
    },
  );

  it("accepts gated detection metadata and opens the returned FEN", async () => {
    vi.useFakeTimers();
    const analytics = captureAnalytics();
    try {
      const uploadedFen = "4k3/8/8/8/8/8/8/4K3 b - - 0 1";
      const fetchMock = vi.fn().mockResolvedValue(
        new Response(
          JSON.stringify({
            fen: uploadedFen,
            source: "gated_detection_orchestrator",
            confidence: 0.91,
            message: "Detection completed. Review the board before using it.",
            detection: {
              status: "success",
              source: "gated_detection_orchestrator",
              confidence: 0.91,
              fen: uploadedFen,
              orientation: "black-bottom",
              stages: [
                {
                  stage: "fen",
                  status: "success",
                  source: "test_fen",
                  confidence: 0.91,
                  failure: null,
                },
              ],
              failure: null,
            },
          }),
          { status: 200, headers: { "Content-Type": "application/json" } },
        ),
      );
      vi.stubGlobal("fetch", fetchMock);

      render(<App />);

      const input = screen.getByLabelText("Choose chess screenshot");
      const file = new File(["fake image"], "position.png", { type: "image/png" });

      fireEvent.change(input, { target: { files: [file] } });

      await flushPromises();

      expect(screen.getByText("Analyzing position")).toBeInTheDocument();

      await advanceNextUploadStage();

      expect(screen.getByText("Opening board")).toBeInTheDocument();

      await advanceNextUploadStage();

      expect(screen.getByTestId("static-board")).toBeInTheDocument();
      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-fen",
        uploadedFen,
      );
      expect(screen.getByTestId("static-board")).toHaveAttribute(
        "data-edit-mode",
        "false",
      );
      expect(screen.getByRole("button", { name: "Play" })).toHaveAttribute(
        "aria-pressed",
        "true",
      );
      expect(screen.queryByText(/Position needs review/)).not.toBeInTheDocument();
      expect(analytics.events).toEqual(
        expect.arrayContaining([
          {
            name: "upload_success",
            payload: {
              source: "gated_detection_orchestrator",
              fen_length: uploadedFen.length,
              confidence_available: true,
            },
          },
          {
            name: "analysis_opened",
            payload: {
              source: "gated_detection_orchestrator",
              fen_length: uploadedFen.length,
            },
          },
        ]),
      );
      expectAnalyticsEventsAreSafe(analytics.events, uploadedFen);
    } finally {
      vi.useRealTimers();
      analytics.unsubscribe();
    }
  });

  it("displays structured API errors", async () => {
    const analytics = captureAnalytics();
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
      "This upload is not a supported image type.",
    );
    expect(
      screen.getByText(
        "Choose a PNG or JPG screenshot of the board and upload it again.",
      ),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Try another image" }),
    ).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
    expect(analytics.events).toContainEqual({
      name: "upload_failed",
      payload: {
        reason: "unsupported_file_type",
        file_type: "text/plain",
        file_size_bucket: "under_100kb",
      },
    });
    expectAnalyticsEventsAreSafe(analytics.events);
    analytics.unsubscribe();
  });

  it("displays network failures", async () => {
    const analytics = captureAnalytics();
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Failed to fetch")));

    render(<App />);

    const input = screen.getByLabelText("Choose chess screenshot");
    const file = new File(["fake image"], "position.png", { type: "image/png" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByText("Uploading image")).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "We could not reach the upload service.",
      );
    });
    expect(
      screen.getByText(
        "Check your connection, make sure the backend is running, then try again.",
      ),
    ).toBeInTheDocument();
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Try another image" }));

    expect(screen.getByText("Ready to retry")).toBeInTheDocument();
    expect(screen.getByTestId("upload-dropzone")).toHaveAttribute("aria-busy", "false");
    expect(analytics.events).toContainEqual({
      name: "upload_failed",
      payload: {
        reason: "network",
        file_type: "image/png",
        file_size_bucket: "under_100kb",
      },
    });
    expectAnalyticsEventsAreSafe(analytics.events);
    analytics.unsubscribe();
  });
});

async function flushPromises() {
  await act(async () => {
    await Promise.resolve();
    await Promise.resolve();
  });
}

async function advanceNextUploadStage() {
  await act(async () => {
    await vi.advanceTimersToNextTimerAsync();
  });
  await flushPromises();
}

async function uploadSelectedFile() {
  const input = screen.getByLabelText("Choose chess screenshot");
  const file = new File(["fake image"], "position.png", { type: "image/png" });

  fireEvent.change(input, { target: { files: [file] } });

  await flushPromises();

  expect(screen.getByText("Analyzing position")).toBeInTheDocument();

  await advanceNextUploadStage();

  expect(screen.getByText("Opening board")).toBeInTheDocument();

  await advanceNextUploadStage();
}

function captureAnalytics() {
  const events: AnalyticsEvent[] = [];
  const unsubscribe = subscribeToAnalytics((event) => events.push(event));

  return { events, unsubscribe };
}

function expectAnalyticsEventsAreSafe(events: AnalyticsEvent[], forbiddenFen = "") {
  events.forEach((event) => {
    expect(event.payload).not.toHaveProperty("file");
    expect(event.payload).not.toHaveProperty("image");
    expect(event.payload).not.toHaveProperty("fen");
    expect(Object.values(event.payload)).not.toContain(forbiddenFen);
  });
}
