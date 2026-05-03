export type AnalyticsEventName =
  | "upload_started"
  | "upload_success"
  | "upload_failed"
  | "analysis_opened"
  | "edit_mode_opened"
  | "fen_copied"
  | "share_created"
  | "share_failed";

export type AnalyticsPayload = Record<string, boolean | number | string | null>;

export type AnalyticsEvent = {
  name: AnalyticsEventName;
  payload: AnalyticsPayload;
};

type AnalyticsListener = (event: AnalyticsEvent) => void;

const listeners = new Set<AnalyticsListener>();

export function trackEvent(name: AnalyticsEventName, payload: AnalyticsPayload = {}) {
  const event = { name, payload: sanitizePayload(payload) };

  listeners.forEach((listener) => listener(event));
}

export function subscribeToAnalytics(listener: AnalyticsListener) {
  listeners.add(listener);

  return () => {
    listeners.delete(listener);
  };
}

function sanitizePayload(payload: AnalyticsPayload) {
  return Object.fromEntries(
    Object.entries(payload).filter(([key]) => !["fen", "file", "image"].includes(key)),
  );
}
