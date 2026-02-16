import { Button, Textarea } from "@poly/ui";
import { Checkbox } from "@poly/ui/checkbox";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Clock, Edit2, Save, X } from "lucide-react";
import { useState } from "react";
import { api } from "../../../../lib/api";

interface Segment {
  id: number;
  start_ms: number;
  end_ms: number;
  text: string;
  speaker: string | null;
}

interface SegmentListProps {
  transcriptId: string;
  segments: Segment[];
  onUpdate: () => void;
}

export function SegmentList({ transcriptId, segments, onUpdate }: SegmentListProps) {
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editText, setEditText] = useState("");
  const _queryClient = useQueryClient();

  const updateMutation = useMutation({
    mutationFn: ({ segmentId, text }: { segmentId: number; text: string }) =>
      api.updateTranscriptSegment(transcriptId, segmentId, text),
    onSuccess: () => {
      setEditingId(null);
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

  if (segments.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">No segments available</div>;
  }

  return (
    <div className="space-y-4">
      {segments.map((segment) => (
        <div key={segment.id} data-segment-id={segment.id} className="p-4 border rounded-lg hover:bg-muted/50 transition-colors">
          <div className="flex items-center gap-2 mb-2 text-sm text-muted-foreground">
            <Checkbox data-segment-checkbox />
            <Clock className="w-4 h-4" />
            <span className="font-mono">
              {formatTimestamp(segment.start_ms)} - {formatTimestamp(segment.end_ms)}
            </span>
            {segment.speaker && (
              <span className="ml-2 px-2 py-0.5 bg-primary/10 text-primary rounded text-xs">
                {segment.speaker}
              </span>
            )}
          </div>

          {editingId === segment.id ? (
            <div className="space-y-2">
              <Textarea
                value={editText}
                onChange={(e) => setEditText(e.target.value)}
                className="min-h-[80px]"
              />
              <div className="flex justify-end gap-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCancel}
                  disabled={updateMutation.isPending}
                >
                  <X className="w-4 h-4 mr-1" />
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={() => handleSave(segment.id)}
                  disabled={updateMutation.isPending}
                >
                  <Save className="w-4 h-4 mr-1" />
                  {updateMutation.isPending ? "Saving..." : "Save"}
                </Button>
              </div>
            </div>
          ) : (
            <div className="flex items-start justify-between gap-4">
              <p className="flex-1">{segment.text}</p>
              <Button variant="ghost" size="sm" onClick={() => handleEdit(segment)}>
                <Edit2 className="w-4 h-4" />
              </Button>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
