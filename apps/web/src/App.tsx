import { useState } from "react";

import type { UploadSuccessResponse } from "./api/upload";
import { AnalysisShell } from "./components/AnalysisShell";
import { UploadDropzone } from "./components/UploadDropzone";

export function App() {
  const [uploadedFen, setUploadedFen] = useState<string | null>(null);

  function handleUploadSuccess(result: UploadSuccessResponse) {
    setUploadedFen(result.fen);
  }

  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <div className="mx-auto flex min-h-screen w-full max-w-7xl flex-col px-5 py-6 sm:px-8">
        <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
          <p className="text-sm font-medium uppercase tracking-wide text-emerald-300">
            Play The Position
          </p>
        </div>

        {uploadedFen ? (
          <AnalysisShell fen={uploadedFen} />
        ) : (
          <UploadScreen onUploadSuccess={handleUploadSuccess} />
        )}
      </div>
    </main>
  );
}

function UploadScreen({
  onUploadSuccess,
}: {
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

      <UploadDropzone onUploadSuccess={onUploadSuccess} />
    </section>
  );
}
