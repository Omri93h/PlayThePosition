import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

describe("App", () => {
  afterEach(() => {
    cleanup();
    vi.useRealTimers();
    vi.unstubAllGlobals();
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

  it("uploads a selected file and displays the placeholder FEN", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          fen: "8/8/8/8/8/8/8/8 w - - 0 1",
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
    expect(screen.getByText("Uploading screenshot")).toBeInTheDocument();

    expect(await screen.findByText("Placeholder FEN ready")).toBeInTheDocument();
    expect(screen.getByText("8/8/8/8/8/8/8/8 w - - 0 1")).toBeInTheDocument();
    expect(screen.getByTestId("upload-dropzone")).toHaveAttribute("aria-busy", "false");

    expect(fetchMock).toHaveBeenCalledWith(
      "http://127.0.0.1:8000/upload",
      expect.objectContaining({ method: "POST", body: expect.any(FormData) }),
    );
  });

  it("uploads a dropped file and displays the placeholder FEN", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      new Response(
        JSON.stringify({
          fen: "8/8/8/8/8/8/8/8 w - - 0 1",
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

    expect(await screen.findByText("Placeholder FEN ready")).toBeInTheDocument();
    expect(screen.getByText("8/8/8/8/8/8/8/8 w - - 0 1")).toBeInTheDocument();
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

    expect(await screen.findByRole("alert")).toHaveTextContent(
      "Only PNG and JPEG images are supported.",
    );
  });

  it("displays network failures", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Failed to fetch")));

    render(<App />);

    const input = screen.getByLabelText("Choose chess screenshot");
    const file = new File(["fake image"], "position.png", { type: "image/png" });

    fireEvent.change(input, { target: { files: [file] } });

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent(
        "Network error. Check your connection and try again.",
      );
    });

    fireEvent.click(screen.getByRole("button", { name: "Retry upload" }));

    expect(screen.getByText("Ready to retry")).toBeInTheDocument();
    expect(screen.getByTestId("upload-dropzone")).toHaveAttribute("aria-busy", "false");
  });
});
