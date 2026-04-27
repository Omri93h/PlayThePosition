import { UploadDropzone } from "./components/UploadDropzone";

export function App() {
  return (
    <main className="min-h-screen bg-neutral-950 text-neutral-100">
      <section className="mx-auto flex min-h-screen w-full max-w-5xl flex-col items-center justify-center px-5 py-12 sm:px-8">
        <div className="w-full max-w-3xl text-center">
          <p className="text-sm font-medium uppercase tracking-wide text-emerald-300">
            Play The Position
          </p>
          <h1 className="mt-4 text-4xl font-semibold tracking-normal text-white sm:text-5xl">
            Upload a chess position screenshot
          </h1>
          <p className="mx-auto mt-5 max-w-2xl text-base leading-7 text-neutral-300 sm:text-lg">
            Drop in a board image or choose one from your device to start turning a
            screenshot into a live position.
          </p>
        </div>

        <UploadDropzone />
      </section>
    </main>
  );
}
