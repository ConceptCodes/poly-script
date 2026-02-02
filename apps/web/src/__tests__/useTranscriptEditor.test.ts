import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useTranscriptEditor } from '../pages/transcripts/[id]/hooks/useTranscriptEditor';
import { api } from '../lib/api';

// Mock API
vi.mock('../lib/api', () => ({
  api: {
    updateTranscript: vi.fn(),
  },
}));

describe('useTranscriptEditor', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
        mutations: { retry: false },
      },
    });
    vi.clearAllMocks();
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );

  it('initializes with provided text', () => {
    const { result } = renderHook(
      () => useTranscriptEditor({ transcriptId: 'test-id', initialText: 'Hello world' }),
      { wrapper }
    );

    expect(result.current.text).toBe('Hello world');
  });

  it('can undo text changes', async () => {
    const { result } = renderHook(
      () => useTranscriptEditor({ transcriptId: 'test-id', initialText: 'Original text' }),
      { wrapper }
    );

    // Change text
    act(() => {
      result.current.setText('New text');
    });

    expect(result.current.text).toBe('New text');
    expect(result.current.canUndo).toBe(true);
    expect(result.current.canRedo).toBe(false);

    // Undo
    act(() => {
      result.current.undo();
    });

    expect(result.current.text).toBe('Original text');
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(true);
  });

  it('can redo after undo', async () => {
    const { result } = renderHook(
      () => useTranscriptEditor({ transcriptId: 'test-id', initialText: 'Original' }),
      { wrapper }
    );

    act(() => {
      result.current.setText('Modified');
      result.current.undo();
    });

    expect(result.current.canRedo).toBe(true);

    // Redo
    act(() => {
      result.current.redo();
    });

    expect(result.current.text).toBe('Modified');
    expect(result.current.canRedo).toBe(false);
  });

  it('resets to initial text', () => {
    const { result } = renderHook(
      () => useTranscriptEditor({ transcriptId: 'test-id', initialText: 'Initial' }),
      { wrapper }
    );

    act(() => {
      result.current.setText('Changed');
    });

    expect(result.current.text).toBe('Changed');
    expect(result.current.canUndo).toBe(true);

    // Reset
    act(() => {
      result.current.reset();
    });

    expect(result.current.text).toBe('Initial');
    expect(result.current.canUndo).toBe(false);
    expect(result.current.canRedo).toBe(false);
  });

  it('saves changes via API', async () => {
    vi.mocked(api.updateTranscript).mockResolvedValue({ id: 'test-id', text: 'Saved text' });

    const { result } = renderHook(
      () => useTranscriptEditor({ transcriptId: 'test-id', initialText: 'Initial' }),
      { wrapper }
    );

    act(() => {
      result.current.setText('To save');
    });

    // Trigger save
    await act(async () => {
      await result.current.save();
    });

    expect(api.updateTranscript).toHaveBeenCalledWith('test-id', 'To save');
  });
});
