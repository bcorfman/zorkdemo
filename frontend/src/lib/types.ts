import { z } from "zod";

export const SessionCreateResponseSchema = z.object({
  session_id: z.string(),
  created: z.boolean(),
  intro_html: z.string().default("")
});

export const CommandResponseSchema = z.object({
  session_id: z.string(),
  input: z.string(),
  output_html: z.string(),
  updated_at: z.string()
});

export const SessionResetResponseSchema = z.object({
  session_id: z.string(),
  reset: z.boolean()
});

export type SessionCreateResponse = z.infer<typeof SessionCreateResponseSchema>;
export type CommandResponse = z.infer<typeof CommandResponseSchema>;
export type SessionResetResponse = z.infer<typeof SessionResetResponseSchema>;

export type TranscriptEntry = {
  id: string;
  kind: "input" | "output" | "system";
  text: string;
  isHtml?: boolean;
};
