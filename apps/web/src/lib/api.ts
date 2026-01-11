const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/v1";

interface ApiOptions extends Omit<RequestInit, 'body'> {
  body?: Record<string, unknown> | null;
}

export async function apiFetch<T = unknown>(endpoint: string, options: ApiOptions = {}): Promise<T> {
  const token = localStorage.getItem("access_token");
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };
  if (token && !headers.Authorization) {
    headers.Authorization = `Bearer ${token}`;
  }

  const body = options.body && typeof options.body === 'object'
    ? JSON.stringify(options.body)
    : undefined;

  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers,
    body: body as BodyInit,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "An unknown error occurred" }));
    throw new Error(error.detail || response.statusText);
  }

  const data = await response.json();
  return data as T;
}

export const api = {
  async getJobs(params?: { page?: number; page_size?: number; status?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());
    if (params?.status) queryParams.append("status_filter", params.status);

    return apiFetch<{
      jobs: Array<{
        id: string;
        status: string;
        filename: string;
        language: string | null;
        progress_pct: number;
        progress_stage: string | null;
        created_at: string;
        started_at: string | null;
        finished_at: string | null;
      }>;
      total: number;
      page: number;
      page_size: number;
    }>(`/jobs?${queryParams.toString()}`);
  },

  async getPendingJobs(params?: { page?: number; page_size?: number }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());

    return apiFetch<{
      jobs: Array<{
        id: string;
        status: string;
        filename: string;
        language: string | null;
        progress_pct: number;
        progress_stage: string | null;
        created_at: string;
        started_at: string | null;
        finished_at: string | null;
      }>;
      total: number;
      page: number;
      page_size: number;
    }>(`/jobs/pending?${queryParams.toString()}`);
  },

  async getCompletedJobs(params?: { page?: number; page_size?: number; status?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());
    if (params?.status) queryParams.append("status_filter", params.status);

    return apiFetch<{
      jobs: Array<{
        id: string;
        status: string;
        filename: string;
        language: string | null;
        progress_pct: number;
        progress_stage: string | null;
        created_at: string;
        started_at: string | null;
        finished_at: string | null;
      }>;
      total: number;
      page: number;
      page_size: number;
    }>(`/jobs/completed?${queryParams.toString()}`);
  },

  async getJobDetail(jobId: string) {
    return apiFetch<{
      id: string;
      status: string;
      filename: string;
      requested_language: string | null;
      detected_language: string | null;
      engine: string;
      options: Record<string, unknown>;
      progress_pct: number;
      progress_stage: string | null;
      attempts: number;
      error_code: string | null;
      error_message: string | null;
      created_at: string;
      started_at: string | null;
      finished_at: string | null;
      audio_duration_seconds: number | null;
    }>(`/jobs/${jobId}`);
  },

  async getJobResult(jobId: string) {
    return apiFetch<{
      job_id: string;
      transcript_id: string;
      text: string;
      language: string;
      segments: Array<{
        id: number;
        start_ms: number;
        end_ms: number;
        text: string;
        speaker: string | null;
      }>;
      engine: string;
    }>(`/jobs/${jobId}/result`);
  },

  async cancelJob(jobId: string) {
    return apiFetch<{ message: string }>(`/jobs/${jobId}/cancel`, {
      method: "POST",
    });
  },

  async getJobLiveStream(jobId: string): EventSource {
    const token = localStorage.getItem("access_token");
    const url = `${API_URL}/jobs/${jobId}/live`;
    const eventSource = new EventSource(url);
    return eventSource;
  },

  // Transcripts API
  async getTranscripts(params?: { page?: number; page_size?: number; language?: string; search?: string }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());
    if (params?.language) queryParams.append("language", params.language);
    if (params?.search) queryParams.append("search", params.search);

    return apiFetch<{
      transcripts: Array<{
        id: string;
        job_id: string;
        job_filename: string | null;
        text_preview: string;
        language: string;
        created_at: string;
        updated_at: string | null;
      }>;
      total: number;
      page: number;
      page_size: number;
    }>(`/transcripts?${queryParams.toString()}`);
  },

  async getTranscript(transcriptId: string) {
    return apiFetch<{
      id: string;
      job_id: string;
      text: string;
      language: string;
      segments: Array<{
        id: number;
        start_ms: number;
        end_ms: number;
        text: string;
        speaker: string | null;
      }>;
      engine_version: string;
      created_at: string;
      updated_at: string | null;
    }>(`/transcripts/${transcriptId}`);
  },

  async updateTranscriptFullText(transcriptId: string, text: string) {
    return apiFetch<{
      id: string;
      job_id: string;
      text: string;
      language: string;
      segments: Array<{
        id: number;
        start_ms: number;
        end_ms: number;
        text: string;
        speaker: string | null;
      }>;
      engine_version: string;
      created_at: string;
      updated_at: string | null;
    }>(`/transcripts/${transcriptId}`, {
      method: "PATCH",
      body: { text },
    });
  },

  async getTranscriptSegments(transcriptId: string) {
    return apiFetch<{
      segments: Array<{
        id: number;
        start_ms: number;
        end_ms: number;
        text: string;
        speaker: string | null;
      }>;
    }>(`/transcripts/${transcriptId}/segments`);
  },

  async updateTranscriptSegment(transcriptId: string, segmentId: number, text: string) {
    return apiFetch<{
      id: number;
      start_ms: number;
      end_ms: number;
      text: string;
      speaker: string | null;
    }>(`/transcripts/${transcriptId}/segments/${segmentId}`, {
      method: "PATCH",
      body: { text },
    });
  },

  async getTranscriptHistory(transcriptId: string) {
    return apiFetch<{
      edits: Array<{
        id: string;
        user_id: string | null;
        user_email: string | null;
        field_edited: string;
        segment_id: number | null;
        previous_text: string;
        new_text: string;
        created_at: string;
      }>;
      total: number;
    }>(`/transcripts/${transcriptId}/history`);
  },

  async revertTranscript(transcriptId: string) {
    return apiFetch<{ message: string; transcript_id: string }>(
      `/transcripts/${transcriptId}/revert`,
      {
        method: "POST",
        body: { confirm: true },
      }
    );
  },

  async exportTranscript(transcriptId: string, format: "txt" | "json" | "srt" | "vtt" = "txt"): Promise<Blob> {
    const token = localStorage.getItem("access_token");
    const response = await fetch(`${API_URL}/transcripts/${transcriptId}/export?format=${format}`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "Export failed" }));
      throw new Error(error.detail || "Export failed");
    }

    return response.blob();
  },
};
