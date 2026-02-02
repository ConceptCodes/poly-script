import { useState, useCallback, useRef } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '../../../../../lib/api';

export interface EditorState {
  text: string;
  timestamp: number;
}

interface UseTranscriptEditorOptions {
  transcriptId: string;
  initialText?: string;
  onSave?: () => void;
}

export function useTranscriptEditor({
  transcriptId,
  initialText = '',
  onSave,
}: UseTranscriptEditorOptions) {
  const queryClient = useQueryClient();
  const [state, setState] = useState<EditorState>({
    text: initialText,
    timestamp: Date.now(),
  });
  
  // Undo/redo stack
  const [undoStack, setUndoStack] = useState<EditorState[]>([]);
  const [redoStack, setRedoStack] = useState<EditorState[]>([]);
  
  const isSavingRef = useRef(false);
  const saveTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const saveMutation = useMutation({
    mutationFn: (text: string) =>
      api.updateTranscript(transcriptId, text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transcript', transcriptId] });
      onSave?.();
    },
  });

  const pushState = useCallback((newState: EditorState) => {
    setUndoStack((prev) => [...prev, state]);
    setRedoStack([]); // Clear redo stack on new change
    setState(newState);
  }, [state]);

  const undo = useCallback(() => {
    if (undoStack.length === 0) return;
    
    const previousState = undoStack[undoStack.length - 1];
    setUndoStack((prev) => prev.slice(0, -1));
    pushToRedoStack(state);
    setState(previousState);
  }, [undoStack, state]);

  const redo = useCallback(() => {
    if (redoStack.length === 0) return;
    
    const nextState = redoStack[redoStack.length - 1];
    setRedoStack((prev) => prev.slice(0, -1));
    pushToUndoStack(state);
    setState(nextState);
  }, [redoStack, state]);

  const pushToRedoStack = useCallback((editorState: EditorState) => {
    setRedoStack((prev) => [...prev, editorState]);
  }, []);

  const pushToUndoStack = useCallback((editorState: EditorState) => {
    setUndoStack((prev) => [...prev, editorState]);
  }, []);

  const setText = useCallback((text: string, recordState = true) => {
    const newState = { text, timestamp: Date.now() };
    
    if (recordState) {
      pushState(newState);
    } else {
      setState(newState);
    }
  }, [pushState]);

  // Auto-save with debounce
  const autoSave = useCallback(() => {
    if (isSavingRef.current) return;
    
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    
    saveTimeoutRef.current = setTimeout(() => {
      isSavingRef.current = true;
      saveMutation.mutate(state.text, {
        onSuccess: () => {
          isSavingRef.current = false;
        },
        onError: () => {
          isSavingRef.current = false;
        },
      });
    }, 1000); // 1 second debounce
  }, [state.text, saveMutation]);

  const save = useCallback(() => {
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }
    saveMutation.mutate(state.text);
  }, [state.text, saveMutation]);

  const reset = useCallback(() => {
    setState({ text: initialText, timestamp: Date.now() });
    setUndoStack([]);
    setRedoStack([]);
  }, [initialText]);

  return {
    text: state.text,
    setText,
    undo,
    redo,
    canUndo: undoStack.length > 0,
    canRedo: redoStack.length > 0,
    save,
    autoSave,
    isSaving: saveMutation.isPending,
    reset,
  };
}
