import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { mockFetchSequence, renderWithProviders } from "@/test/utils";
import { WorkshopsPage } from "./workshops-page";
import type { Workshop } from "./types";

const workshop: Workshop = {
  id: "workshop-1", title: "AI Essentials", description: "Practical generative AI skills.", topic: "Artificial intelligence",
  facilitator_name: "Priya Menon", facilitator_email: "priya@schoolnet.in", location: "Innovation Lab",
  starts_on: "2026-10-09", ends_on: "2026-10-30", status: "active", student_count: 1, session_count: 1,
  students: [{ id: "student-1", student_id: "SN-2401", name: "Ananya Sharma", institution: "City Public School", status: "present" }],
  sessions: [{ id: "session-1", title: "Prompting foundations", starts_at: "2026-10-09T10:00:00Z", ends_at: "2026-10-09T12:00:00Z", location: "Innovation Lab" }],
};

describe("WorkshopsPage", () => {
  it("loads the list and selected workshop detail", async () => {
    mockFetchSequence([{ body: [workshop] }, { body: workshop }]);
    renderWithProviders(<WorkshopsPage/>);
    expect(await screen.findByText("Ananya Sharma")).toBeInTheDocument();
    expect(screen.getAllByText("AI Essentials")).toHaveLength(2);
  });

  it("filters workshops by their title", async () => {
    mockFetchSequence([{ body: [workshop] }, { body: workshop }]);
    const user = userEvent.setup(); renderWithProviders(<WorkshopsPage/>);
    await screen.findAllByText("AI Essentials");
    await user.type(screen.getByRole("searchbox", { name: /find a workshop/i }), "design");
    expect(screen.getByText("No workshops found.")).toBeInTheDocument();
  });

  it("opens the accessible add student dialog", async () => {
    mockFetchSequence([{ body: [workshop] }, { body: workshop }]);
    const user = userEvent.setup(); renderWithProviders(<WorkshopsPage/>);
    await screen.findAllByText("AI Essentials");
    await user.click(screen.getByRole("button", { name: /add student/i }));
    expect(screen.getByRole("dialog", { name: /add a student/i })).toBeInTheDocument();
    expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
  });
});
