export type SharedPositionResponse = {
  id: string;
  fen: string;
  source: "share";
};

export type CreateSharedPositionResponse = SharedPositionResponse & {
  path: string;
};

type ApiErrorResponse = {
  error?: {
    message?: string;
  };
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function createSharedPosition(
  fen: string,
): Promise<CreateSharedPositionResponse> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/share`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ fen }),
    });
  } catch {
    throw new Error("Network error. Check your connection and try again.");
  }

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(response, "Share link could not be created."),
    );
  }

  return response.json() as Promise<CreateSharedPositionResponse>;
}

export async function loadSharedPosition(
  shareId: string,
): Promise<SharedPositionResponse> {
  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/share/${encodeURIComponent(shareId)}`);
  } catch {
    throw new Error("Network error. Check your connection and try again.");
  }

  if (!response.ok) {
    throw new Error(
      await getErrorMessage(response, "Shared position could not be loaded."),
    );
  }

  return response.json() as Promise<SharedPositionResponse>;
}

async function getErrorMessage(response: Response, fallbackMessage: string) {
  try {
    const payload = (await response.json()) as ApiErrorResponse;
    return payload.error?.message ?? fallbackMessage;
  } catch {
    return fallbackMessage;
  }
}
