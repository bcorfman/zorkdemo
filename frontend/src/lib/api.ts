import {
  CommandResponse,
  CommandResponseSchema,
  SessionCreateResponse,
  SessionCreateResponseSchema,
  SessionResetResponse,
  SessionResetResponseSchema
} from "./types";

type ApiErrorPayload = {
  detail?: string;
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function requestJson<T>(
  path: string,
  payload: object,
  validator: { parse: (value: unknown) => T }
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });

  let parsedJson: unknown = {};
  try {
    parsedJson = await response.json();
  } catch {
    parsedJson = {};
  }

  if (!response.ok) {
    const errorPayload = parsedJson as ApiErrorPayload;
    const message = errorPayload.detail ?? "Request failed";
    throw new Error(message);
  }

  return validator.parse(parsedJson);
}

export async function createSession(
  sessionId: string | null
): Promise<SessionCreateResponse> {
  return requestJson(
    "/api/v1/session",
    { session_id: sessionId ?? undefined },
    SessionCreateResponseSchema
  );
}

export async function runCommand(
  sessionId: string,
  command: string
): Promise<CommandResponse> {
  return requestJson(
    "/api/v1/command",
    { session_id: sessionId, command },
    CommandResponseSchema
  );
}

export async function resetSession(
  sessionId: string
): Promise<SessionResetResponse> {
  return requestJson(
    "/api/v1/session/reset",
    { session_id: sessionId },
    SessionResetResponseSchema
  );
}
