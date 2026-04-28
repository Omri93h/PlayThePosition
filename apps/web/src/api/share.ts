export type SharedPositionResponse = {
  id: string;
  fen: string;
  source: "share";
};

type ApiErrorResponse = {
  error?: {
    message?: string;
  };
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

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
    throw new Error(await getErrorMessage(response));
  }

  return response.json() as Promise<SharedPositionResponse>;
}

async function getErrorMessage(response: Response) {
  try {
    const payload = (await response.json()) as ApiErrorResponse;
    return payload.error?.message ?? "Shared position could not be loaded.";
  } catch {
    return "Shared position could not be loaded.";
  }
}
