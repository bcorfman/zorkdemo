import { cleanup, render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "../App";

function jsonResponse(payload: unknown): Response {
  return new Response(JSON.stringify(payload), {
    status: 200,
    headers: {
      "Content-Type": "application/json"
    }
  });
}

describe("App", () => {
  beforeEach(() => {
    window.localStorage.clear();
  });

  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("bootstraps a session and stores the session id", async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({ session_id: "session-123", created: true })
    );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    await screen.findByText(/Session: session-123/i);
    expect(window.localStorage.getItem("zorkdemo_session_id")).toBe("session-123");
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/session",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("submits a command and renders html output", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", created: true })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "look",
          output_html: "<p><strong>West of House</strong></p>",
          updated_at: "2026-03-02T00:00:01"
        })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await screen.findByText(/Session: session-123/i);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/Command/i), "look");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await screen.findByText("West of House");
    expect(screen.getByText(/^look$/i)).toBeInTheDocument();
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      "http://localhost:8000/api/v1/command",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("renders first look output even when intro already contains room text", async () => {
    const introHtml = [
      "<p>ZORK I: The Great Underground Empire</p>",
      "<p><span class='location'>West of House</span><br />Room text.</p>"
    ].join("");

    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", created: true, intro_html: introHtml })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "look",
          output_html: "<p><span class='location'>West of House</span><br />Room text.</p>",
          updated_at: "2026-03-02T00:00:01"
        })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await screen.findByText(/Session: session-123/i);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/Command/i), "look");
    await user.click(screen.getByRole("button", { name: /Send/i }));

    await waitFor(() => {
      expect(screen.getAllByText("West of House")).toHaveLength(2);
    });
  });

  it("uses existing local session id and marks session as resumed", async () => {
    window.localStorage.setItem("zorkdemo_session_id", "existing-session");
    const fetchMock = vi
      .fn()
      .mockResolvedValue(
        jsonResponse({ session_id: "existing-session", created: false })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);

    await screen.findByText(/Session: existing-session \(resumed\)/i);
    expect(fetchMock).toHaveBeenCalledWith(
      "http://localhost:8000/api/v1/session",
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({ session_id: "existing-session" })
      })
    );
  });

  it("resets the current session and clears transcript", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", created: true })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "look",
          output_html: "<p>Room text</p>",
          updated_at: "2026-03-02T00:00:01"
        })
      )
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", reset: true, intro_html: "" })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await screen.findByText(/Session: session-123/i);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/Command/i), "look");
    await user.click(screen.getByRole("button", { name: /Send/i }));
    await screen.findByText("Room text");

    await user.click(screen.getByRole("button", { name: /Reset Session/i }));

    await waitFor(() => {
      expect(screen.queryByText("Room text")).not.toBeInTheDocument();
    });
    expect(fetchMock).toHaveBeenNthCalledWith(
      3,
      "http://localhost:8000/api/v1/session/reset",
      expect.objectContaining({ method: "POST" })
    );
  });

  it("shows intro text immediately after reset", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", created: true, intro_html: "<p>Old intro</p>" })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          reset: true,
          intro_html: "<p><span class='location'>West of House</span><br />Room text.</p>"
        })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await screen.findByText(/Session: session-123/i);

    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /Reset Session/i }));

    await screen.findByText("West of House");
    expect(screen.getByText("Room text.")).toBeInTheDocument();
  });

  it("follows restore Y/N confirmation flow", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", created: true, intro_html: "<p>Intro</p>" })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "restore SLOT1",
          output_html: "<p>Do you wish to restore over the game in progress (Y/N)?</p>",
          updated_at: "2026-03-16T00:00:01"
        })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "Y",
          output_html: "<p>SLOT1 restored.</p>",
          updated_at: "2026-03-16T00:00:02"
        })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await screen.findByText(/Session: session-123/i);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/Command/i), "restore SLOT1");
    await user.click(screen.getByRole("button", { name: /Send/i }));
    await screen.findByText("Do you wish to restore over the game in progress (Y/N)?");

    await user.type(screen.getByLabelText(/Command/i), "Y");
    await user.click(screen.getByRole("button", { name: /Send/i }));
    await screen.findByText("SLOT1 restored.");
  });

  it("follows save overwrite Y/N confirmation flow", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", created: true, intro_html: "<p>Intro</p>" })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "save SLOT1",
          output_html: "<p>SLOT1 already exists. Do you wish to overwrite it (Y/N)?</p>",
          updated_at: "2026-03-16T00:00:01"
        })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "N",
          output_html: "<p>Overwrite cancelled.</p>",
          updated_at: "2026-03-16T00:00:02"
        })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await screen.findByText(/Session: session-123/i);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/Command/i), "save SLOT1");
    await user.click(screen.getByRole("button", { name: /Send/i }));
    await screen.findByText("SLOT1 already exists. Do you wish to overwrite it (Y/N)?");

    await user.type(screen.getByLabelText(/Command/i), "N");
    await user.click(screen.getByRole("button", { name: /Send/i }));
    await screen.findByText("Overwrite cancelled.");
  });

  it("follows reset slots Y/N confirmation flow", async () => {
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce(
        jsonResponse({ session_id: "session-123", created: true, intro_html: "<p>Intro</p>" })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "reset slots",
          output_html: "<p>Do you wish to delete all saved slots for this session (Y/N)?</p>",
          updated_at: "2026-03-16T00:00:01"
        })
      )
      .mockResolvedValueOnce(
        jsonResponse({
          session_id: "session-123",
          input: "Y",
          output_html: "<p>All saved slots deleted for this session.</p>",
          updated_at: "2026-03-16T00:00:02"
        })
      );
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    await screen.findByText(/Session: session-123/i);

    const user = userEvent.setup();
    await user.type(screen.getByLabelText(/Command/i), "reset slots");
    await user.click(screen.getByRole("button", { name: /Send/i }));
    await screen.findByText("Do you wish to delete all saved slots for this session (Y/N)?");

    await user.type(screen.getByLabelText(/Command/i), "Y");
    await user.click(screen.getByRole("button", { name: /Send/i }));
    await screen.findByText("All saved slots deleted for this session.");
  });
});
