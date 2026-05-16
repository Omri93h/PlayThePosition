import type { ApiError } from "./errors.js";

export type FenString = string;
export type UploadDetectionStatus = "placeholder" | "success" | "partial" | "failed";
export type UploadDetectionOrientation =
  | "white-bottom"
  | "black-bottom"
  | "unknown"
  | (string & {});

export type HealthResponse = {
  status: "ok";
};

export type UploadDetectionFailure = {
  code: string;
  message: string;
  stage: string;
  retryable: boolean;
  suggestion: string;
  failure_reason?: string | null;
};

export type UploadDetectionStage = {
  stage: string;
  status: UploadDetectionStatus;
  source: string;
  confidence: number | null;
  failure: UploadDetectionFailure | null;
};

export type UploadDetectionMetadata = {
  status: UploadDetectionStatus;
  source: string;
  confidence: number | null;
  fen: FenString | null;
  orientation: UploadDetectionOrientation;
  stages: UploadDetectionStage[];
  failure: UploadDetectionFailure | null;
};

export type UploadSuccessResponse = {
  fen: FenString;
  source: string;
  confidence: number | null;
  message: string;
  detection?: UploadDetectionMetadata;
};

export type UploadErrorResponse = {
  ok: false;
  error: ApiError;
};
