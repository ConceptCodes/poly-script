import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@poly/ui/button";
import Input from "@poly/ui/input";
import Textarea from "@poly/uitextarea";
import {
  Edit2,
  Save,
  X,
  Clock,
  Scissors,
  GitMerge,
  ChevronRight,
  ChevronLeft,
} from "lucide-react";
import { api } from "../../../../lib/api";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from "@poly/ui/dialog";

interface Segment {
  id: number;
  start_ms: number;
  end_ms: number;
  text: string;
  speaker: string | null;
}

interface SegmentListWithOpsProps {
  transcriptId: string;
  segments: Segment[];
  onUpdate: () => void;
  onSegmentClick?: (segment: Segment) => void;
  activeSegmentId?: number;
}

export function SegmentListWithOps({
  transcriptId,
  segments,
  onUpdate,
  onSegmentClick,
  activeSegmentId,
}: SegmentListWithOpsProps) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editingTimestamps, setEditingTimestamps] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const [editStartMs, setEditStartMs] = useState(0);
  const [editEndMs, setEditEndMs] = useState(0);
  const [splitDialog, setSplitDialog] = useState<number | null>(null);
  const [splitTime, setSplitTime] = useState(0);
  const [selectedForMerge, setSelectedForMerge] = useState<Set<number>>(new Set());

  const queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: ({ segmentId, text }: { segmentId: number; text: string }) =>
      api.updateTranscriptSegment(transcriptId, segmentId, text),
    onSuccess: () => {
      setEditingId(null);
      onUpdate();
    },
  });

  const splitMutation = useMutation({
    mutationFn: ({ segmentId, splitAtMs }: { segmentId: number; splitAtMs: number }) =>
      api.splitSegment(transcriptId, segmentId, splitAtMs),
    onSuccess: () => {
      setSplitDialog(null);
      onUpdate();
    },
  });

  const mergeMutation = useMutation({
    mutationFn: (segmentIds: number[]) =>
      api.mergeSegments(transcriptId, segmentIds),
    onSuccess: () => {
      setSelectedForMerge(new Set());
      onUpdate();
    },
  });

  const updateTimestampsMutation = useMutation({
    mutationFn: ({
      segmentId,
      startMs,
      endMs,
    }: {
      segmentId: number;
      startMs: number;
      endMs: number;
    }) =>
      api.updateSegmentTimestamps(transcriptId, segmentId, startMs, endMs),
    onSuccess: () => {
      setEditingTimestamps(null);
      onUpdate();
    },
  });

  const formatTimestamp = (ms: number) => {
    const hours = Math.floor(ms / 3600000);
    const minutes = Math.floor((ms % 3600000) / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    const milliseconds = ms % 1000;

    return `${hours.toString().padStart(2, "0")}:${minutes
      .toString()
      .padStart(2, "0")}:${seconds.toString().padStart(2, "0")}.${milliseconds
      .toString()
      .padStart(3, "0")}`;
  };

  const parseTimestamp = (ts: string) => {
    const parts = ts.split(":");
    if (parts.length !== 3) return 0;

    const hours = parseInt(parts[0], 10);
    const timeParts = parts[2].split(".");
    const minutes = parseInt(parts[1], 10);
    const seconds = parseInt(timeParts[0], 10);
    const milliseconds = parseInt(timeParts[1].padEnd(3, "0").slice(0, 3), 10);

    return hours * 3600000 + minutes * 60000 + seconds * 1000 + milliseconds;
  };

  const handleEdit = (segment: Segment) => {
    setEditingId(segment.id);
    setEditText(segment.text);
  };

  const handleSave = (segmentId: number) => {
    updateMutation.mutate({ segmentId, text: editText });
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditText("");
  };

  const handleSplit = (segment: Segment) => {
    setSplitDialog(segment.id);
    setSplitTime(Math.floor((segment.start_ms + segment.end_ms) / 2));
  };

  const confirmSplit = () => {
    if (splitDialog !== null) {
      splitMutation.mutate({ segmentId: splitDialog, splitAtMs: splitTime });
    }
  };

  const toggleMergeSelection = (segmentId: number) => {
    const newSelected = new Set(selectedForMerge);
    if (newSelected.has(segmentId)) {
      newSelected.delete(segmentId);
    } else {
      newSelected.add(segmentId);
    }
    setSelectedForMerge(newSelected);
  };

  const handleMerge = () => {
    const selected = Array.from(selectedForMerge).sort((a, b) => a - b);
    if (selected.length >= 2) {
      mergeMutation.mutate(selected);
    }
  };

  const areConsecutive = (ids: number[]) => {
    const sorted = [...ids].sort((a, b) => a - b);
    for (let i = 1; i < sorted.length; i++) {
      if (sorted[i] !== sorted[i - 1] + 1) return false;
    }
    return true;
  };

  const canMerge = selectedForMerge.size >= 2 && areConsecutive(Array.from(selectedForMerge));

  const handleTimestampEdit = (segment: Segment) => {
    setEditingTimestamps(segment.id);
    setEditStartMs(segment.start_ms);
    setEditEndMs(segment.end_ms);
  };

  const handleSaveTimestamps = () => {
    if (editingTimestamps !== null) {
      updateTimestampsMutation.mutate({
        segmentId: editingTimestamps,
        startMs: editStartMs,
        endMs: editEndMs,
      });
    }
  };

  if (segments.length === 0) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No segments available
      </div>
    );
  }

  return (
    <>
      {/* Merge actions */}
      {selectedForMerge.size > 0 && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 bg-background border rounded-lg shadow-lg p-4 flex items-center gap-3 z-50">
          <span className="text-sm">{selectedForMerge.size} selected</span>
          {canMerge && (
            <Button size="sm" onClick={handleMerge} disabled={mergeMutation.isPending}>
              <GitMerge className="w-4 h-4 mr-1" />
              {mergeMutation.isPending ? "Merging..." : "Merge"}
            </Button>
          )}
          {!canMerge && (
            <span className="text-xs text-muted-foreground">
              Select consecutive segments to merge
            </span>
          )}
          <Button variant="ghost" size="sm" onClick={() => setSelectedForMerge(new Set())}>
            Clear
          </Button>
        </div>
      )}

      <div className="space-y-4">
        {segments.map((segment, idx) => (
          <div
            key={segment.id}
            className={`p-4 border rounded-lg transition-colors ${
              activeSegmentId === segment.id
                ? "bg-primary/10 border-primary"
                : selectedForMerge.has(segment.id)
                ? "bg-primary/5 border-primary"
                : "hover:bg-muted/50"
            }`}
            onClick={() => onSegmentClick?.(segment)}
          >
            <div className="flex items-start justify-between gap-4 mb-2">
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <input
                  type="checkbox"
                  checked={selectedForMerge.has(segment.id)}
                  onChange={() => toggleMergeSelection(segment.id)}
                  onClick={(e) => e.stopPropagation()}
                  className="rounded border-gray-300"
                />
                {editingTimestamps === segment.id ? (
                  <div className="flex items-center gap-2">
                    <Input
                      type="text"
                      value={formatTimestamp(editStartMs)}
                      onChange={(e) => setEditStartMs(parseTimestamp(e.target.value))}
                      className="w-24 h-8 text-xs"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <span>-</span>
                    <Input
                      type="text"
                      value={formatTimestamp(editEndMs)}
                      onChange={(e) => setEditEndMs(parseTimestamp(e.target.value))}
                      className="w-24 h-8 text-xs"
                      onClick={(e) => e.stopPropagation()}
                    />
                    <Button
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSaveTimestamps();
                      }}
                      disabled={updateTimestampsMutation.isPending}
                    >
                      <Save className="w-3 h-3" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        setEditingTimestamps(null);
                      }}
                    >
                      <X className="w-3 h-3" />
                    </Button>
                  </div>
                ) : (
                  <>
                    <Clock className="w-4 h-4" />
                    <span
                      className="font-mono cursor-pointer hover:text-foreground"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleTimestampEdit(segment);
                      }}
                    >
                      {formatTimestamp(segment.start_ms)} - {formatTimestamp(segment.end_ms)}
                    </span>
                  </>
                )}
                {segment.speaker && (
                  <span className="ml-2 px-2 py-0.5 bg-primary/10 text-primary rounded text-xs">
                    {segment.speaker}
                  </span>
                )}
              </div>

              {/* Segment actions */}
              <div className="flex items-center gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleSplit(segment);
                  }}
                  title="Split segment"
                >
                  <Scissors className="w-4 h-4" />
                </Button>
                {editingId === segment.id ? (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSave(segment.id);
                      }}
                      disabled={updateMutation.isPending}
                    >
                      <Save className="w-4 h-4 mr-1" />
                      {updateMutation.isPending ? "Saving..." : "Save"}
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCancel();
                      }}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </>
                ) : (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleEdit(segment);
                    }}
                  >
                    <Edit2 className="w-4 h-4" />
                  </Button>
                )}
              </div>
            </div>

            {/* Segment text */}
            {editingId === segment.id ? (
              <Textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="min-h-[80px]"
                onClick={(e) => e.stopPropagation()}
              />
            ) : (
              <p className="text-sm">{segment.text}</p>
            )}
          </div>
        ))}
      </div>

      {/* Split dialog */}
      {splitDialog !== null && (
        <Dialog open onOpenChange={() => setSplitDialog(null)}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Split Segment</DialogTitle>
            </DialogHeader>
            <div className="py-4">
              <label className="block text-sm font-medium mb-2">
                Split at timestamp (ms): {splitTime}
              </label>
              <input
                type="range"
                min={segments[splitDialog]?.start_ms || 0}
                max={segments[splitDialog]?.end_ms || 0}
                value={splitTime}
                onChange={(e) => setSplitTime(parseInt(e.target.value))}
                className="w-full"
              />
              <div className="flex items-center justify-between text-xs text-muted-foreground mt-2">
                <span>{formatTimestamp(segments[splitDialog]?.start_ms || 0)}</span>
                <span>{formatTimestamp(segments[splitDialog]?.end_ms || 0)}</span>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setSplitDialog(null)}
              >
                Cancel
              </Button>
              <Button
                onClick={confirmSplit}
                disabled={splitMutation.isPending}
              >
                {splitMutation.isPending ? "Splitting..." : "Split"}
              </Button>
            </DialogFooter>
          </DialogContent>
 </Dialog>
      )}
    </>
  );
}
