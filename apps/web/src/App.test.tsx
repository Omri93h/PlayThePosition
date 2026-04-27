import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the upload screen UI", () => {
    render(<App />);

    expect(
      screen.getByRole("heading", { name: "Upload a chess position screenshot" }),
    ).toBeInTheDocument();
    expect(screen.getByText("Click to upload")).toBeInTheDocument();
    expect(
      screen.getByText("or drag and drop a chess screenshot here"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Choose chess screenshot")).toHaveAttribute(
      "type",
      "file",
    );
  });
});
