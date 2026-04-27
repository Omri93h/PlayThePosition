import { useEffect, useRef, useState } from "react";
import type { DragEvent } from "react";

type UploadUiState = "idle" | "dragging" | "loading" | "error" | "retry";

const demoErrorDelayMs = 700;

const stateStyles: Record<UploadUiState, string> = {
  idle: "border-emerald-300/60 bg-neutral-900 shadow-emerald-950/30",
  dragging: "border-emerald-200 bg-emerald-950/40 shadow-emerald-900/40",
  loading: "border-sky-300/70 bg-sky-950/30 shadow-sky-950/30",
  error: "border-rose-300/70 bg-rose-950/30 shadow-rose-950/30",
  retry: "border-amber-300/70 bg-amber-950/30 shadow-amber-950/30",
};

export function UploadDropzone() {
  const [uploadState, setUploadState] = useState<UploadUiState>("idle");
  const demoTimer = useRef<number | undefined>(undefined);

  useEffect(() => {
    return () => {
      window.clearTimeout(demoTimer.current);
    };
  }, []);

  function clearDemoTimer() {
    window.clearTimeout(demoTimer.current);
    demoTimer.current = undefined;
  }

  function startLocalLoadingDemo() {
    clearDemoTimer();
    setUploadState("loading");
    demoTimer.current = window.setTimeout(() => {
      setUploadState("error");
    }, demoErrorDelayMs);
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

    if (uploadState === "dragging") {
      setUploadState("idle");
    }
  }

  function handleFileSelection() {
    startLocalLoadingDemo();
  }

  function handleRetry() {
    clearDemoTimer();
    setUploadState("retry");
  }

  const isLoading = uploadState === "loading";
  const isError = uploadState === "error";

  return (
    <div
      data-testid="upload-dropzone"
      aria-busy={isLoading}
      onDragEnter={handleDragEnter}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`mt-10 flex w-full max-w-2xl flex-col items-center justify-center border border-dashed px-6 py-12 text-center shadow-2xl outline-none transition focus-within:ring-2 focus-within:ring-emerald-300 sm:px-10 ${stateStyles[uploadState]}`}
    >
      <DropzoneIcon state={uploadState} />
      <DropzoneContent state={uploadState} onRetry={handleRetry} />

      {!isLoading && !isError ? (
        <label
          htmlFor="screenshot-upload"
          className="mt-6 cursor-pointer text-sm font-semibold text-emerald-200 underline decoration-emerald-300/50 underline-offset-4 transition hover:text-emerald-100"
        >
          Click to upload
        </label>
      ) : null}

      <input
        id="screenshot-upload"
        name="screenshot-upload"
        type="file"
        accept="image/png,image/jpeg,image/webp"
        className="sr-only"
        aria-label="Choose chess screenshot"
        onChange={handleFileSelection}
      />
    </div>
  );
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
  onRetry,
}: {
  state: UploadUiState;
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
          Preparing screenshot
        </span>
        <span className="mt-2 text-sm leading-6 text-neutral-300">
          This local UI preview is not connected to the backend yet.
        </span>
      </>
    );
  }

  if (state === "error") {
    return (
      <>
        <span className="mt-6 text-xl font-semibold text-white">
          Upload preview paused
        </span>
        <span role="alert" className="mt-2 text-sm leading-6 text-rose-100">
          No upload service is connected yet.
        </span>
        <button
          type="button"
          onClick={onRetry}
          className="mt-6 border border-rose-200 px-4 py-2 text-sm font-semibold text-rose-50 transition hover:bg-rose-200 hover:text-rose-950 focus:outline-none focus:ring-2 focus:ring-rose-200"
        >
          Retry upload
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
          PNG, JPG, or WebP image
        </span>
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
        PNG, JPG, or WebP image
      </span>
    </>
  );
}
