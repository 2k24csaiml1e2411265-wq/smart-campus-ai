import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import StatCard from "./components/StatCard.jsx";

describe("StatCard", () => {
  it("renders label and value", () => {
    render(<StatCard label="Total Energy" value="12.4" unit="kWh" />);
    expect(screen.getByText("Total Energy")).toBeTruthy();
    expect(screen.getByText("12.4")).toBeTruthy();
    expect(screen.getByText("kWh")).toBeTruthy();
  });
});
