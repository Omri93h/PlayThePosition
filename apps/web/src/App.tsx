import { useEffect, useState } from "react";

import { loadSharedPosition } from "./api/share";
import type { UploadSuccessResponse } from "./api/upload";
import { AnalysisShell } from "./components/AnalysisShell";
import { LoadingOverlay } from "./components/LoadingOverlay";
import { UploadDropzone } from "./components/UploadDropzone";

type UploadLoadingStage = "uploading" | "analyzing" | "opening";

type SharedPositionState =
  | { status: "idle"; fen: null; error: "" }
  | { status: "loading"; fen: null; error: "" }
  | { status: "loaded"; fen: string; error: "" }
  | { status: "error"; fen: null; error: string };

export function App() {
  const shareId = getShareId(window.location.pathname);
  const [uploadedFen, setUploadedFen] = useState<string | null>(null);
  const [uploadLoadingStage, setUploadLoadingStage] =
    useState<UploadLoadingStage | null>(null);
  const [sharedPosition, setSharedPosition] = useState<SharedPositionState>({
    status: shareId ? "loading" : "idle",
    fen: null,
    error: "",
  });

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
    setUploadedFen(result.fen);
    setUploadLoadingStage(null);
  }

  function handleUploadFailure() {
    setUploadLoadingStage(null);
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-6 sm:px-8">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <p className="text-sm font-medium uppercase tracking-wide text-emerald-300">
            Play The Position
          </p>
        </div>

        {shareId ? (
          <SharedPositionView state={sharedPosition} />
        ) : uploadedFen ? (
          <AnalysisShell fen={uploadedFen} />
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
    return <AnalysisShell fen={state.fen} />;
  }

  if (state.status === "error") {
    return (
      <section className="flex flex-1 flex-col items-center justify-center py-12 text-center">
        <h1 className="text-3xl font-semibold tracking-normal text-white">
          Shared position unavailable
        </h1>
        <p role="alert" className="mt-4 max-w-xl text-sm leading-6 text-rose-100">
          {state.error}
        </p>
      </section>
    );
  }

  return (
    <section className="flex flex-1 flex-col items-center justify-center py-12 text-center">
      <h1 className="text-3xl font-semibold tracking-normal text-white">
        Loading shared position
      </h1>
      <p className="mt-4 text-sm leading-6 text-neutral-300">
        Fetching the saved board state.
      </p>
    </section>
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
    <section className="flex flex-1 flex-col items-center justify-center py-12">
      <div className="w-full max-w-3xl text-center">
        <h1 className="mt-4 text-4xl font-semibold tracking-normal text-white sm:text-5xl">
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
