import type { UploadSuccessResponse } from "contracts";

export type { UploadSuccessResponse } from "contracts";

type ApiErrorResponse = {
  error?: {
    message?: string;
  };
};

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function uploadScreenshot(file: File): Promise<UploadSuccessResponse> {
  const formData = new FormData();
  formData.append("file", file);

  let response: Response;

  try {
    response = await fetch(`${apiBaseUrl}/upload`, {
      method: "POST",
      body: formData,
    });
  } catch {
    throw new Error("Network error. Check your connection and try again.");
  }

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  return response.json() as Promise<UploadSuccessResponse>;
}

async function getErrorMessage(response: Response) {
  try {
    const payload = (await response.json()) as ApiErrorResponse;
    return payload.error?.message ?? "Upload failed. Try another image.";
  } catch {
    return "Upload failed. Try another image.";
  }
}
