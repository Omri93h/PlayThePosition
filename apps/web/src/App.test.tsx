import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { App } from "./App";

describe("App", () => {
  it("renders the foundation app shell", () => {
    render(<App />);

    expect(screen.getByText("Frontend foundation")).toBeInTheDocument();
    expect(
      screen.getByRole("heading", { name: "Play The Position" }),
    ).toBeInTheDocument();
  });
});
