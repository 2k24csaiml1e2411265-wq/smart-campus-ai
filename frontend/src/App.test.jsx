import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";
import App from "./App.jsx";
import { AuthProvider } from "./hooks/useAuth.jsx";

describe("App routing", () => {
  it("renders login route", () => {
    render(
      <MemoryRouter initialEntries={["/login"]}>
        <AuthProvider>
          <App />
        </AuthProvider>
      </MemoryRouter>
    );
    expect(screen.getByText(/Smart Campus AI/)).toBeTruthy();
    expect(screen.getByText(/Sign in/)).toBeTruthy();
  });
});
