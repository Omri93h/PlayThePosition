type LoadingOverlayProps = {
  stage: "uploading" | "analyzing" | "opening";
};

const stageContent: Record<
  LoadingOverlayProps["stage"],
  { title: string; detail: string }
> = {
  uploading: {
    title: "Uploading image",
    detail: "Sending your screenshot to the app.",
  },
  analyzing: {
    title: "Analyzing position",
    detail: "Preparing the board result from the current MVP pipeline.",
  },
  opening: {
    title: "Opening board",
    detail: "Loading the editable position workspace.",
  },
};

export function LoadingOverlay({ stage }: LoadingOverlayProps) {
  const content = stageContent[stage];

  return (
    <div
      aria-labelledby="upload-loading-title"
      aria-modal="true"
      className="fixed inset-0 z-50 flex items-center justify-center bg-neutral-950/80 px-4 backdrop-blur-sm"
      role="dialog"
    >
      <div className="w-full max-w-sm rounded-lg border border-emerald-300/30 bg-neutral-900 p-5 text-center shadow-2xl shadow-emerald-950/40 sm:p-6">
        <div
          aria-hidden="true"
          className="mx-auto h-12 w-12 animate-spin rounded-full border-2 border-emerald-300/20 border-t-emerald-200"
        />
        <h2 className="mt-5 text-xl font-semibold tracking-normal text-white">
          <span id="upload-loading-title">{content.title}</span>
        </h2>
        <p className="mt-2 text-sm leading-6 text-neutral-300">{content.detail}</p>
        <div className="mt-5 grid grid-cols-3 gap-2" aria-hidden="true">
          {(["uploading", "analyzing", "opening"] as const).map((step) => (
            <span
              key={step}
              className={`h-1 rounded-full ${
                step === stage ? "bg-emerald-200" : "bg-neutral-700"
              }`}
            />
          ))}
        </div>
        <p className="mt-4 text-xs font-medium uppercase tracking-wide text-neutral-500">
          Detection is still in scaffolded MVP mode
        </p>
      </div>
    </div>
  );
}
