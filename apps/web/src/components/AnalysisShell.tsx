export function AnalysisShell() {
  return (
    <section
      aria-labelledby="analysis-shell-title"
      className="grid flex-1 gap-6 py-8 lg:grid-cols-[minmax(0,1fr)_20rem]"
    >
      <div className="flex min-h-[32rem] flex-col rounded-lg border border-neutral-800 bg-neutral-900/70 shadow-2xl shadow-emerald-950/20">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-neutral-800 px-5 py-4">
          <div>
            <p className="text-xs font-medium uppercase tracking-wide text-emerald-300">
              Analysis board
            </p>
            <h1
              id="analysis-shell-title"
              className="mt-1 text-2xl font-semibold tracking-normal text-white"
            >
              Position workspace
            </h1>
          </div>
          <div
            aria-label="Analysis toolbar"
            className="flex flex-wrap items-center gap-2"
          >
            <span className="rounded-lg bg-neutral-800 px-4 py-2 text-sm font-semibold text-neutral-200">
              Board tools
            </span>
            <span className="rounded-lg bg-neutral-800 px-4 py-2 text-sm font-semibold text-neutral-200">
              Position tools
            </span>
          </div>
        </div>

        <div className="flex flex-1 items-center justify-center p-5">
          <div
            aria-label="Board placeholder"
            className="aspect-square w-full max-w-[34rem] rounded-lg border border-emerald-300/30 bg-neutral-950 shadow-inner shadow-emerald-950"
          >
            <div className="grid h-full w-full grid-cols-8 grid-rows-8 overflow-hidden rounded-lg">
              {Array.from({ length: 64 }, (_, index) => (
                <span
                  key={index}
                  className={
                    index % 2 === Math.floor(index / 8) % 2
                      ? "bg-neutral-800"
                      : "bg-neutral-700"
                  }
                />
              ))}
            </div>
          </div>
        </div>

        <div
          aria-label="Analysis actions"
          className="flex flex-wrap items-center justify-between gap-3 border-t border-neutral-800 px-5 py-4"
        >
          <span className="text-sm text-neutral-400">Ready for board loading.</span>
          <div className="flex flex-wrap gap-2">
            <span className="rounded-lg border border-neutral-700 px-4 py-2 text-sm font-semibold text-neutral-200">
              Board action
            </span>
            <span className="rounded-lg border border-emerald-300/60 px-4 py-2 text-sm font-semibold text-emerald-200">
              Position action
            </span>
          </div>
        </div>
      </div>

      <aside className="rounded-lg border border-neutral-800 bg-neutral-900/60 p-5 shadow-xl shadow-neutral-950/40">
        <h2 className="text-lg font-semibold text-white">Position details</h2>
        <p className="mt-3 text-sm leading-6 text-neutral-300">
          Static shell only. FEN loading and board state arrive in the next features.
        </p>
      </aside>
    </section>
  );
}
