import type { ReactNode } from "react";
import { lazy, Suspense, useEffect, useState } from "react";

import { trackEvent } from "./analytics";
import { loadSharedPosition } from "./api/share";
import type { UploadSuccessResponse } from "./api/upload";
import { LoadingOverlay } from "./components/LoadingOverlay";
import { UploadDropzone } from "./components/UploadDropzone";

const AnalysisShell = lazy(() =>
  import("./components/AnalysisShell").then((module) => ({
    default: module.AnalysisShell,
  })),
);

type UploadLoadingStage = "uploading" | "analyzing" | "opening";

type SharedPositionState =
  | { status: "idle"; fen: null; error: "" }
  | { status: "loading"; fen: null; error: "" }
  | { status: "loaded"; fen: string; error: "" }
  | { status: "error"; fen: null; error: string };

export function App() {
  const [currentPath, setCurrentPath] = useState(window.location.pathname);
  const shareId = getShareId(currentPath);
  const [uploadedFen, setUploadedFen] = useState<string | null>(null);
  const [uploadLoadingStage, setUploadLoadingStage] =
    useState<UploadLoadingStage | null>(null);
  const [sharedPosition, setSharedPosition] = useState<SharedPositionState>({
    status: shareId ? "loading" : "idle",
    fen: null,
    error: "",
  });
  const showHeaderUploadAction = Boolean(
    uploadedFen || (shareId && sharedPosition.status === "loaded"),
  );

  useEffect(() => {
    if (!shareId) {
      return;
    }

    let isActive = true;

    setSharedPosition({ status: "loading", fen: null, error: "" });

    void loadSharedPosition(shareId)
      .then((position) => {
        if (isActive) {
          setSharedPosition({ status: "loaded", fen: position.fen, error: "" });
        }
      })
      .catch((error) => {
        if (isActive) {
          setSharedPosition({
            status: "error",
            fen: null,
            error:
              error instanceof Error
                ? error.message
                : "Shared position could not be loaded.",
          });
        }
      });

    return () => {
      isActive = false;
    };
  }, [shareId]);

  function handleUploadSuccess(result: UploadSuccessResponse) {
    trackEvent("analysis_opened", {
      source: result.source,
      fen_length: result.fen.length,
    });
    setUploadedFen(result.fen);
    setUploadLoadingStage(null);
  }

  function handleUploadFailure() {
    setUploadLoadingStage(null);
  }

  function handleStartNewUpload() {
    window.history.pushState({}, "", "/");
    setCurrentPath("/");
    setUploadedFen(null);
    setUploadLoadingStage(null);
    setSharedPosition({ status: "idle", fen: null, error: "" });
  }

  return (
    <main className="min-h-screen overflow-x-hidden bg-neutral-950 text-neutral-100">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-4 py-4 sm:px-8 sm:py-6">
        <div
          className="flex flex-row items-center justify-between gap-4"
          data-testid="app-header"
        >
          <p className="text-sm font-medium uppercase tracking-wide text-emerald-300">
            Play The Position
          </p>
          {showHeaderUploadAction ? (
            <button
              type="button"
              aria-label="Upload"
              title="Upload another image"
              onClick={handleStartNewUpload}
              className="inline-flex min-h-11 items-center gap-2 rounded-lg border border-emerald-300/60 px-3 py-2 text-sm font-semibold text-emerald-100 transition hover:border-emerald-200 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-300"
            >
              <svg
                aria-hidden="true"
                className="h-5 w-5"
                fill="none"
                stroke="currentColor"
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                viewBox="0 0 24 24"
              >
                <rect height="14" rx="2" width="18" x="3" y="5" />
                <path d="m8 14 2.5-2.5L14 15l1.5-1.5L19 17" />
                <circle cx="8" cy="9" r="1" />
              </svg>
              <span>Upload</span>
            </button>
          ) : null}
        </div>

        {shareId ? (
          <SharedPositionView state={sharedPosition} />
        ) : uploadedFen ? (
          <AnalysisExperienceFallback>
            <AnalysisShell fen={uploadedFen} />
          </AnalysisExperienceFallback>
        ) : (
          <UploadScreen
            onUploadFailure={handleUploadFailure}
            onUploadStageChange={setUploadLoadingStage}
            onUploadSuccess={handleUploadSuccess}
          />
        )}
      </div>
      {uploadLoadingStage ? <LoadingOverlay stage={uploadLoadingStage} /> : null}
    </main>
  );
}

function getShareId(pathname: string) {
  const match = pathname.match(/^\/share\/([^/]+)\/?$/);
  return match?.[1] ? decodeURIComponent(match[1]) : null;
}

function SharedPositionView({ state }: { state: SharedPositionState }) {
  if (state.status === "loaded") {
    return (
      <AnalysisExperienceFallback>
        <AnalysisShell fen={state.fen} />
      </AnalysisExperienceFallback>
    );
  }

  if (state.status === "error") {
    return (
      <section className="flex flex-1 flex-col items-center justify-center px-1 py-10 text-center sm:py-12">
        <h1 className="text-2xl font-semibold tracking-normal text-white sm:text-3xl">
          Shared position unavailable
        </h1>
        <p role="alert" className="mt-4 max-w-xl text-sm leading-6 text-rose-100">
          This shared board could not be opened. The link may be expired, incomplete, or
          unavailable.
        </p>
        <p className="mt-3 max-w-xl text-sm leading-6 text-neutral-300">
          Start a new upload to rebuild the position, or ask for a fresh share link.
        </p>
        <a
          href="/"
          className="mt-6 inline-flex min-h-11 items-center rounded-lg border border-emerald-300/60 px-4 py-2 text-sm font-semibold text-emerald-100 transition hover:border-emerald-200 hover:text-white focus:outline-none focus:ring-2 focus:ring-emerald-300"
        >
          Start from upload
        </a>
        <p className="mt-4 text-xs leading-5 text-neutral-500">{state.error}</p>
      </section>
    );
  }

  return (
    <section className="flex flex-1 flex-col items-center justify-center px-1 py-10 text-center sm:py-12">
      <h1 className="text-2xl font-semibold tracking-normal text-white sm:text-3xl">
        Loading shared position
      </h1>
      <p className="mt-4 text-sm leading-6 text-neutral-300">
        Fetching the saved board state.
      </p>
    </section>
  );
}

function AnalysisExperienceFallback({ children }: { children: ReactNode }) {
  return (
    <Suspense
      fallback={
        <section className="flex flex-1 flex-col items-center justify-center px-1 py-10 text-center sm:py-12">
          <h1 className="text-2xl font-semibold tracking-normal text-white sm:text-3xl">
            Loading analysis board
          </h1>
          <p className="mt-4 text-sm leading-6 text-neutral-300">
            Preparing the editable position workspace.
          </p>
        </section>
      }
    >
      {children}
    </Suspense>
  );
}

function UploadScreen({
  onUploadFailure,
  onUploadStageChange,
  onUploadSuccess,
}: {
  onUploadFailure: () => void;
  onUploadStageChange: (stage: UploadLoadingStage) => void;
  onUploadSuccess: (result: UploadSuccessResponse) => void;
}) {
  return (
    <section className="flex flex-1 flex-col items-center justify-center py-8 sm:py-12">
      <div className="w-full max-w-3xl text-center">
        <h1 className="mt-4 text-3xl font-semibold tracking-normal text-white sm:text-5xl">
          Upload a chess position screenshot
        </h1>
        <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-neutral-300 sm:text-lg">
          Drop in a board image or choose one from your device to start turning a
          screenshot into a live position.
        </p>
      </div>

      <UploadDropzone
        onUploadFailure={onUploadFailure}
        onUploadStageChange={onUploadStageChange}
        onUploadSuccess={onUploadSuccess}
      />
    </section>
  );
}
