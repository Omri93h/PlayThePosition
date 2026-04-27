import type { ApiError } from "./errors.js";

export type FenString = string;

export type HealthResponse = {
  status: "ok";
};

export type DetectionResult = {
  fen: FenString;
  confidence: number | null;
  orientation: "white" | "black" | "unknown";
};

export type UploadSuccessResponse = {
  ok: true;
  result: DetectionResult;
};

export type UploadErrorResponse = {
  ok: false;
  error: ApiError;
};
