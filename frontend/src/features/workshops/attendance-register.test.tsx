import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it } from "vitest";
import { mockFetchSequence, renderWithProviders } from "@/test/utils";
import { AttendanceRegister } from "./attendance-register";
import type { AttendanceSheet, Workshop } from "./types";

const workshop: Workshop = {
  id: "workshop-1", title: "AI Essentials", description: "Practical AI skills", topic: "AI",
  facilitator_name: "Priya", facilitator_email: "priya@example.com", location: "Lab",
  starts_on: "2026-10-09", ends_on: "2026-10-10", status: "active", student_count: 1, session_count: 1,
  sessions: [{ id: "session-1", title: "Day one", starts_at: "2026-10-09T10:00:00Z", ends_at: "2026-10-09T12:00:00Z", location: "Lab" }],
};
const sheet: AttendanceSheet = {
  workshop_id: "workshop-1", session_id: "session-1",
  records: [{ student_id: "student-1", student_name: "Ada Lovelace", student_email: "ada@example.com", status: "unmarked", minutes_attended: null }],
};

describe("AttendanceRegister", () => {
  it("marks and saves a student's attendance", async () => {
    const mock = mockFetchSequence([{ body: sheet }, { body: { ...sheet, records: [{ ...sheet.records[0], status: "present", minutes_attended: 55 }] } }]);
    const user = userEvent.setup();
    renderWithProviders(<AttendanceRegister workshop={workshop}/>);
    await screen.findByText("Ada Lovelace");
    await user.click(screen.getByRole("button", { name: "present" }));
    await user.clear(screen.getByLabelText("Minutes attended for Ada Lovelace"));
    await user.type(screen.getByLabelText("Minutes attended for Ada Lovelace"), "55");
    await user.click(screen.getByRole("button", { name: /save attendance/i }));
    await waitFor(() => expect(mock.calls.some((call) => call.init?.method === "PUT")).toBe(true));
    const request = mock.calls.find((call) => call.init?.method === "PUT");
    expect(request?.init?.body).toContain('"status":"present"');
    expect(request?.init?.body).toContain('"minutes_attended":55');
  }, 10_000);
});
