import { act, cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

describe("App", () => {
  afterEach(() => {
    cleanup();
    vi.useRealTimers();
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

  it("shows local loading, error, and retry states for file selection", () => {
    vi.useFakeTimers();
    render(<App />);

    const input = screen.getByLabelText("Choose chess screenshot");
    const file = new File(["fake image"], "position.png", { type: "image/png" });

    fireEvent.change(input, { target: { files: [file] } });

    expect(screen.getByTestId("upload-dropzone")).toHaveAttribute("aria-busy", "true");
    expect(screen.getByText("Preparing screenshot")).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(700);
    });

    expect(screen.getByRole("alert")).toHaveTextContent(
      "No upload service is connected yet.",
    );

    fireEvent.click(screen.getByRole("button", { name: "Retry upload" }));

    expect(screen.getByText("Ready to retry")).toBeInTheDocument();
    expect(screen.getByTestId("upload-dropzone")).toHaveAttribute("aria-busy", "false");
  });
});
