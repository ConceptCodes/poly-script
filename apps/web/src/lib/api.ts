import { API_URL, createApiFetch } from "@poly/ui";

// Create web-specific apiFetch with:
// - access_token (not admin_access_token)
// - error object with status and code
// - FormData support enabled
// - auto-redirect to /session-expired on unrecoverable 401
export const apiFetch = createApiFetch({
  tokenKey: "access_token",
  supportsFormData: true,
  errorTransformer: (error: unknown, status: number) => {
    const errorRecord = (error as Record<string, unknown>) || {};
    const nestedError = errorRecord.error as Record<string, unknown> | undefined;

    if (status === 401 && typeof window !== "undefined") {
      // Only redirect if we're not already on an auth page
      const isAuthPage =
        window.location.pathname.startsWith("/login") ||
        window.location.pathname.startsWith("/signup") ||
        window.location.pathname.startsWith("/session-expired") ||
        window.location.pathname.startsWith("/auth/");
      if (!isAuthPage) {
        window.location.href = "/session-expired";
      }
    }

    const source = nestedError ?? errorRecord;
    return {
      status,
      code: source.code ?? null,
      message: source.message ?? source.detail ?? "An error occurred",
      details: source.details ?? null,
      request_id: source.request_id ?? null,
      documentation_url: source.documentation_url ?? null,
    };
  },
});

// The api object with all endpoint methods remains the same
// ... rest of the api methods
export const api = {
  // Jobs API
  async getJobs(params?: {
    page?: number;
    page_size?: number;
    status?: string;
    search?: string;
    sort_field?: string;
    sort_order?: "asc" | "desc";
  }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());
    if (params?.status) queryParams.append("status_filter", params.status);
    if (params?.search) queryParams.append("search", params.search);
    if (params?.sort_field) queryParams.append("sort_field", params.sort_field);
    if (params?.sort_order) queryParams.append("sort_order", params.sort_order);

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
      translation?: {
        target_language: string;
        text: string;
        segments: Array<{
          start_ms: number;
          end_ms: number;
          text: string;
          speaker?: string | null;
        }> | null;
        engine: string | null;
        engine_version: string | null;
      } | null;
    }>(`/jobs/${jobId}/result`);
  },

  async createJob(formData: FormData) {
    return apiFetch<{ job_id: string; status: string; message: string }>("/jobs", {
      method: "POST",
      body: formData,
    });
  },

  async createJobFromUrl(url: string, options: Record<string, unknown>) {
    return apiFetch<{ job_id: string; status: string; message: string }>("/jobs/url", {
      method: "POST",
      body: { url, options },
    });
  },

  async cancelJob(jobId: string) {
    return apiFetch<{ message: string }>(`/jobs/${jobId}/cancel`, {
      method: "POST",
    });
  },

  async getJobLiveStream(jobId: string): Promise<EventSource> {
    const token = localStorage.getItem("access_token");
    const url = `${API_URL}/jobs/${jobId}/live?access_token=${token}`;
    return new EventSource(url);
  },

  // Transcripts API
  async getTranscripts(params?: {
    page?: number;
    page_size?: number;
    language?: string;
    search?: string;
    sort?: string;
    start_date?: string;
    end_date?: string;
  }) {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.append("page", params.page.toString());
    if (params?.page_size) queryParams.append("page_size", params.page_size.toString());
    if (params?.language) queryParams.append("language", params.language);
    if (params?.search) queryParams.append("search", params.search);
    if (params?.sort) queryParams.append("sort", params.sort);
    if (params?.start_date) queryParams.append("start_date", params.start_date);
    if (params?.end_date) queryParams.append("end_date", params.end_date);

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

  async deleteTranscript(transcriptId: string) {
    return apiFetch<void>(`/transcripts/${transcriptId}`, {
      method: "DELETE",
    });
  },

  async bulkDeleteTranscripts(transcriptIds: string[]) {
    return apiFetch<{ deleted_count: number }>("/transcripts/bulk-delete", {
      method: "POST",
      body: { transcript_ids: transcriptIds },
    });
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
      },
    );
  },

  async exportTranscript(
    transcriptId: string,
    format: "txt" | "json" | "srt" | "vtt" = "txt",
  ): Promise<Blob> {
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

  async splitSegment(transcriptId: string, segmentId: number, splitAtMs: number) {
    return apiFetch<{
      message: string;
      original_segment_id: number;
      new_segment_ids: number[];
    }>(`/transcripts/${transcriptId}/segments/${segmentId}/split`, {
      method: "POST",
      body: { split_at_ms: splitAtMs },
    });
  },

  async mergeSegments(transcriptId: string, segmentIds: number[]) {
    return apiFetch<{
      message: string;
      merged_segment_id: number;
      removed_segment_ids: number[];
    }>(`/transcripts/${transcriptId}/segments/merge`, {
      method: "POST",
      body: { segment_ids: segmentIds },
    });
  },

  async updateSegmentTimestamps(
    transcriptId: string,
    segmentId: number,
    startMs: number,
    endMs: number,
  ) {
    return apiFetch<{
      message: string;
      segment: {
        id: number;
        start_ms: number;
        end_ms: number;
        text: string;
        speaker: string | null;
      };
    }>(`/transcripts/${transcriptId}/segments/${segmentId}/timestamps`, {
      method: "PATCH",
      body: { start_ms: startMs, end_ms: endMs },
    });
  },

  async updateTranscript(transcriptId: string, text: string) {
    return this.updateTranscriptFullText(transcriptId, text);
  },
};
