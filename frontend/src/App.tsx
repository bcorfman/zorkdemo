import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { createSession, resetSession, runCommand } from "./lib/api";
import { TranscriptEntry } from "./lib/types";
import "./App.css";

const SESSION_STORAGE_KEY = "zorkdemo_session_id";

function generateEntryId(): string {
  return `${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function htmlToNormalizedText(html: string): string {
  const container = document.createElement("div");
  container.innerHTML = html;
  return (container.textContent ?? "")
    .replace(/\s+/g, " ")
    .trim()
    .toLowerCase();
}

function isRedundantInitialLook(
  cleanedCommand: string,
  previousEntries: TranscriptEntry[],
  outputHtml: string
): boolean {
  if (cleanedCommand.toLowerCase() !== "look") {
    return false;
  }
  if (previousEntries.length !== 2) {
    return false;
  }
  const [introEntry, inputEntry] = previousEntries;
  if (
    introEntry.kind !== "output" ||
    !introEntry.isHtml ||
    inputEntry.kind !== "input" ||
    inputEntry.text.trim().toLowerCase() !== "look"
  ) {
    return false;
  }

  const introText = htmlToNormalizedText(introEntry.text);
  const outputText = htmlToNormalizedText(outputHtml);
  if (!outputText) {
    return false;
  }
  return introText.endsWith(outputText);
}

export default function App() {
  const [sessionId, setSessionId] = useState<string>("");
  const [command, setCommand] = useState<string>("");
  const [transcript, setTranscript] = useState<TranscriptEntry[]>([]);
  const [status, setStatus] = useState<string>("Connecting...");
  const [error, setError] = useState<string>("");
  const [busy, setBusy] = useState<boolean>(false);
  const transcriptRef = useRef<HTMLElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (transcriptRef.current) {
      transcriptRef.current.scrollTop = transcriptRef.current.scrollHeight;
    }
    if (!busy && inputRef.current) {
      inputRef.current.focus();
    }
  }, [transcript, busy]);

  const canSubmit = useMemo(
    () => command.trim().length > 0 && sessionId.length > 0 && !busy,
    [busy, command, sessionId]
  );

  useEffect(() => {
    let active = true;

    async function bootstrap() {
      setBusy(true);
      setError("");
      try {
        const existingSession = localStorage.getItem(SESSION_STORAGE_KEY);
        const response = await createSession(existingSession);
        if (!active) {
          return;
        }
        setSessionId(response.session_id);
        localStorage.setItem(SESSION_STORAGE_KEY, response.session_id);
        if (response.created && response.intro_html) {
          setTranscript([
            {
              id: generateEntryId(),
              kind: "output",
              text: response.intro_html,
              isHtml: true
            }
          ]);
        }
        setStatus(
          response.created
            ? `Session: ${response.session_id} (new)`
            : `Session: ${response.session_id} (resumed)`
        );
      } catch (err) {
        if (!active) {
          return;
        }
        const message = err instanceof Error ? err.message : "Failed to bootstrap";
        setError(message);
        setStatus("Disconnected");
      } finally {
        if (active) {
          setBusy(false);
        }
      }
    }

    bootstrap();

    return () => {
      active = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const cleanedCommand = command.trim();
    if (!cleanedCommand || !sessionId || busy) {
      return;
    }

    setBusy(true);
    setError("");
    setStatus(`Session: ${sessionId}`);

    setTranscript((prev) => [
      ...prev,
      { id: generateEntryId(), kind: "input", text: cleanedCommand }
    ]);

    setCommand("");

    try {
      const response = await runCommand(sessionId, cleanedCommand);
      setTranscript((prev) => [
        ...(isRedundantInitialLook(cleanedCommand, prev, response.output_html)
          ? prev
          : [
              ...prev,
              {
                id: generateEntryId(),
                kind: "output",
                text: response.output_html,
                isHtml: true
              }
            ])
      ]);
      setStatus(`Session: ${response.session_id}`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to run command";
      setError(message);
      setTranscript((prev) => [
        ...prev,
        { id: generateEntryId(), kind: "system", text: "Command failed." }
      ]);
    } finally {
      setBusy(false);
    }
  }

  async function handleReset() {
    if (!sessionId || busy) {
      return;
    }

    setBusy(true);
    setError("");
    try {
      const response = await resetSession(sessionId);
      setTranscript([]);
      setStatus(`Session: ${response.session_id} (reset)`);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to reset session";
      setError(message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="app">
      <section className="panel">
        <header className="header">
          <h1 className="title">ZorkDemo</h1>
          <p className="status" aria-live="polite">
            {status}
          </p>
        </header>

        {error && <div className="error">{error}</div>}

        <section className="transcript" aria-label="Transcript" ref={transcriptRef}>
          {transcript.length === 0 ? (
            <p className="line line-system">Type a command like "look" to begin.</p>
          ) : (
            transcript.map((entry) => (
              entry.isHtml ? (
                <div
                  className={`line line-${entry.kind}`}
                  key={entry.id}
                  dangerouslySetInnerHTML={{ __html: entry.text }}
                />
              ) : (
                <div className={`line line-${entry.kind}`} key={entry.id}>
                  {entry.text}
                </div>
              )
            ))
          )}
        </section>

        <form className="controls" onSubmit={handleSubmit}>
          <label htmlFor="command-input" className="sr-only">
            Command
          </label>
          <input
            id="command-input"
            name="command"
            ref={inputRef}
            value={command}
            onChange={(event) => setCommand(event.target.value)}
            placeholder="Enter command"
            aria-label="Command"
            disabled={busy}
          />
          <button type="submit" disabled={!canSubmit}>
            Send
          </button>
          <button type="button" onClick={handleReset} disabled={busy || !sessionId}>
            Reset Session
          </button>
        </form>
      </section>
    </main>
  );
}
