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

        <label
          htmlFor="screenshot-upload"
          className="mt-10 flex w-full max-w-2xl cursor-pointer flex-col items-center justify-center border border-dashed border-emerald-300/60 bg-neutral-900 px-6 py-12 text-center shadow-2xl shadow-emerald-950/30 outline-none transition hover:border-emerald-200 hover:bg-neutral-900/80 focus-within:border-emerald-200 focus-within:ring-2 focus-within:ring-emerald-300 sm:px-10"
        >
          <span className="flex h-14 w-14 items-center justify-center rounded-full bg-emerald-300 text-2xl font-semibold text-neutral-950">
            +
          </span>
          <span className="mt-6 text-xl font-semibold text-white">Click to upload</span>
          <span className="mt-2 text-sm leading-6 text-neutral-300">
            or drag and drop a chess screenshot here
          </span>
          <span className="mt-6 text-xs font-medium uppercase tracking-wide text-neutral-500">
            PNG, JPG, or WebP image
          </span>
          <input
            id="screenshot-upload"
            name="screenshot-upload"
            type="file"
            accept="image/png,image/jpeg,image/webp"
            className="sr-only"
            aria-label="Choose chess screenshot"
          />
        </label>
      </section>
    </main>
  );
}
