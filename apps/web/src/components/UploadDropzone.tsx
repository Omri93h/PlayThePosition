import type { ChangeEvent, DragEvent, KeyboardEvent, MouseEvent } from "react";
import { useRef, useState } from "react";

import { trackEvent } from "../analytics";
import { uploadScreenshot } from "../api/upload";
import type { UploadSuccessResponse } from "../api/upload";

type UploadUiState = "idle" | "dragging" | "loading" | "error" | "retry" | "success";
type UploadLoadingStage = "uploading" | "analyzing" | "opening";

const stateStyles: Record<UploadUiState, string> = {
  idle: "border-emerald-300/60 bg-neutral-900 shadow-emerald-950/30",
  dragging: "border-emerald-200 bg-emerald-950/40 shadow-emerald-900/40",
  loading: "border-sky-300/70 bg-sky-950/30 shadow-sky-950/30",
  error: "border-rose-300/70 bg-rose-950/30 shadow-rose-950/30",
  retry: "border-amber-300/70 bg-amber-950/30 shadow-amber-950/30",
  success: "border-emerald-300/70 bg-emerald-950/30 shadow-emerald-950/30",
};

export function UploadDropzone({
  onUploadFailure,
  onUploadStageChange,
  onUploadSuccess,
}: {
  onUploadFailure?: () => void;
  onUploadStageChange?: (stage: UploadLoadingStage) => void;
  onUploadSuccess?: (result: UploadSuccessResponse) => void;
}) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [uploadState, setUploadState] = useState<UploadUiState>("idle");
  const [errorMessage, setErrorMessage] = useState("");
  const [uploadResult, setUploadResult] = useState<UploadSuccessResponse | null>(null);

  async function uploadFile(file: File) {
    setUploadState("loading");
    setErrorMessage("");
    setUploadResult(null);
    trackEvent("upload_started", {
      file_type: file.type || "unknown",
      file_size_bucket: getFileSizeBucket(file.size),
    });
    onUploadStageChange?.("uploading");

    try {
      const result = await uploadScreenshot(file);

      trackEvent("upload_success", {
        source: result.source,
        fen_length: result.fen.length,
        confidence_available: result.confidence !== null,
      });

      onUploadStageChange?.("analyzing");
      await waitForLoadingStage();
      onUploadStageChange?.("opening");
      await waitForLoadingStage();

      setUploadResult(result);
      setUploadState("success");
      onUploadSuccess?.(result);
    } catch (error) {
      trackEvent("upload_failed", {
        reason: getUploadFailureReason(error),
        file_type: file.type || "unknown",
        file_size_bucket: getFileSizeBucket(file.size),
      });
      onUploadFailure?.();
      setErrorMessage(
        error instanceof Error
          ? error.message
          : "Upload failed. Check your connection and try again.",
      );
      setUploadState("error");
    }
  }

  function handleDragEnter(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();

    if (uploadState !== "loading") {
      setUploadState("dragging");
    }
  }

  function handleDragOver(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();
  }

  function handleDragLeave(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();

    if (uploadState === "dragging") {
      setUploadState("idle");
    }
  }

  function handleDrop(event: DragEvent<HTMLDivElement>) {
    event.preventDefault();

    const file = getFirstFile(event.dataTransfer.files);

    if (file) {
      void uploadFile(file);
      return;
    }

    setUploadState("idle");
  }

  function handleFileSelection(event: ChangeEvent<HTMLInputElement>) {
    const file = getFirstFile(event.target.files);

    if (file) {
      void uploadFile(file);
    }
  }

  function handleRetry() {
    setUploadState("retry");
    setErrorMessage("");
    setUploadResult(null);
  }

  const isLoading = uploadState === "loading";
  const isError = uploadState === "error";
  const canSelectFile = !isLoading && !isError;

  function openFilePicker() {
    if (canSelectFile) {
      fileInputRef.current?.click();
    }
  }

  function handleDropzoneClick(event: MouseEvent<HTMLDivElement>) {
    if (event.target === fileInputRef.current) {
      return;
    }

    openFilePicker();
  }

  function handleDropzoneKeyDown(event: KeyboardEvent<HTMLDivElement>) {
    if (event.key !== "Enter" && event.key !== " ") {
      return;
    }

    event.preventDefault();
    openFilePicker();
  }

  return (
    <div
      data-testid="upload-dropzone"
      aria-busy={isLoading}
      aria-label={canSelectFile ? "Open image file picker" : undefined}
      role={canSelectFile ? "button" : undefined}
      tabIndex={canSelectFile ? 0 : undefined}
      onClick={handleDropzoneClick}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onKeyDown={handleDropzoneKeyDown}
      className={`mt-8 flex min-h-80 w-full max-w-2xl flex-col items-center justify-center border border-dashed px-5 py-10 text-center shadow-2xl outline-none transition focus:ring-2 focus:ring-emerald-300 focus-within:ring-2 focus-within:ring-emerald-300 sm:mt-10 sm:px-10 sm:py-12 ${canSelectFile ? "cursor-pointer" : ""} ${stateStyles[uploadState]}`}
    >
      <DropzoneIcon state={uploadState} />
      <DropzoneContent
        state={uploadState}
        errorMessage={errorMessage}
        uploadResult={uploadResult}
        onRetry={handleRetry}
      />

      {!isLoading && !isError ? (
        <span className="mt-6 text-sm font-semibold text-emerald-200 underline decoration-emerald-300/50 underline-offset-4 transition">
          Click to upload
        </span>
      ) : null}

      <input
        ref={fileInputRef}
        id="screenshot-upload"
        name="screenshot-upload"
        type="file"
        accept="image/png,image/jpeg"
        className="sr-only"
        tabIndex={-1}
        aria-label="Choose chess screenshot"
        onChange={handleFileSelection}
      />
    </div>
  );
}

function getFirstFile(files: FileList | null): File | undefined {
  return files?.item?.(0) ?? files?.[0];
}

function waitForLoadingStage() {
  return new Promise((resolve) => window.setTimeout(resolve, 120));
}

function getFileSizeBucket(size: number) {
  if (size < 100 * 1024) {
    return "under_100kb";
  }

  if (size < 1024 * 1024) {
    return "under_1mb";
  }

  if (size < 5 * 1024 * 1024) {
    return "under_5mb";
  }

  return "over_5mb";
}

function getUploadFailureReason(error: unknown) {
  if (!(error instanceof Error)) {
    return "unknown";
  }

  const message = error.message.toLowerCase();

  if (message.includes("network")) {
    return "network";
  }

  if (message.includes("png and jpeg")) {
    return "unsupported_file_type";
  }

  if (message.includes("size")) {
    return "file_too_large";
  }

  if (message.includes("valid image")) {
    return "invalid_image_payload";
  }

  return "api_error";
}

function DropzoneIcon({ state }: { state: UploadUiState }) {
  const icon = state === "loading" ? "" : state === "error" ? "!" : "+";

  return (
    <span className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-300 text-2xl font-semibold text-neutral-950">
      {state === "loading" ? (
        <span
          aria-hidden="true"
          className="h-6 w-6 animate-spin rounded-full border-2 border-neutral-950/20 border-t-neutral-950"
        />
      ) : (
        icon
      )}
    </span>
  );
}

function DropzoneContent({
  state,
  errorMessage,
  uploadResult,
  onRetry,
}: {
  state: UploadUiState;
  errorMessage: string;
  uploadResult: UploadSuccessResponse | null;
  onRetry: () => void;
}) {
  if (state === "dragging") {
    return (
      <>
        <span className="mt-6 text-xl font-semibold text-white">
          Drop screenshot here
        </span>
        <span className="mt-2 text-sm leading-6 text-neutral-300">
          Release to return to the upload prompt.
        </span>
      </>
    );
  }

  if (state === "loading") {
    return (
      <>
        <span className="mt-6 text-xl font-semibold text-white">
          Uploading screenshot
        </span>
        <span className="mt-2 text-sm leading-6 text-neutral-300">
          Sending the image to the backend.
        </span>
      </>
    );
  }

  if (state === "error") {
    const errorContent = getUploadErrorContent(errorMessage);

    return (
      <>
        <span className="mt-6 text-xl font-semibold text-white">
          {errorContent.title}
        </span>
        <span role="alert" className="mt-2 text-sm leading-6 text-rose-100">
          {errorContent.message}
        </span>
        <span className="mt-2 max-w-md text-sm leading-6 text-neutral-300">
          {errorContent.guidance}
        </span>
        <button
          type="button"
          onClick={onRetry}
          className="mt-6 inline-flex min-h-11 items-center border border-rose-200 px-4 py-2 text-sm font-semibold text-rose-50 transition hover:bg-rose-200 hover:text-rose-950 focus:outline-none focus:ring-2 focus:ring-rose-200"
        >
          Try another image
        </button>
      </>
    );
  }

  if (state === "retry") {
    return (
      <>
        <span className="mt-6 text-xl font-semibold text-white">Ready to retry</span>
        <span className="mt-2 text-sm leading-6 text-neutral-300">
          Choose a screenshot again or drag one over the dropzone.
        </span>
        <span className="mt-6 text-xs font-medium uppercase tracking-wide text-neutral-500">
          PNG or JPG image
        </span>
      </>
    );
  }

  if (state === "success" && uploadResult) {
    return (
      <>
        <span className="mt-6 text-xl font-semibold text-white">
          Placeholder FEN ready
        </span>
        <span className="mt-2 text-sm leading-6 text-neutral-300">
          {uploadResult.message}
        </span>
        <code className="mt-6 max-w-full overflow-x-auto border border-emerald-300/30 bg-neutral-950 px-3 py-2 text-sm text-emerald-100">
          {uploadResult.fen}
        </code>
      </>
    );
  }

  return (
    <>
      <span className="mt-6 text-xl font-semibold text-white">
        Choose a board image
      </span>
      <span className="mt-2 text-sm leading-6 text-neutral-300">
        or drag and drop a chess screenshot here
      </span>
      <span className="mt-6 text-xs font-medium uppercase tracking-wide text-neutral-500">
        PNG or JPG image
      </span>
    </>
  );
}

function getUploadErrorContent(errorMessage: string) {
  if (errorMessage.toLowerCase().includes("network")) {
    return {
      title: "Connection problem",
      message: "We could not reach the upload service.",
      guidance:
        "Check your connection, make sure the backend is running, then try again.",
    };
  }

  if (errorMessage.toLowerCase().includes("png and jpeg")) {
    return {
      title: "Use a PNG or JPG image",
      message: "This upload is not a supported image type.",
      guidance: "Choose a PNG or JPG screenshot of the board and upload it again.",
    };
  }

  if (errorMessage.toLowerCase().includes("size")) {
    return {
      title: "Image is too large",
      message: "This screenshot is bigger than the upload limit.",
      guidance: "Try a smaller PNG or JPG image of the board.",
    };
  }

  if (errorMessage.toLowerCase().includes("valid image")) {
    return {
      title: "Image could not be read",
      message: "The file does not look like a readable board screenshot.",
      guidance: "Export or capture the board again, then upload a fresh PNG or JPG.",
    };
  }

  return {
    title: "Upload needs another try",
    message: "We could not process this upload.",
    guidance: "Choose a clear PNG or JPG screenshot and try again.",
  };
}
