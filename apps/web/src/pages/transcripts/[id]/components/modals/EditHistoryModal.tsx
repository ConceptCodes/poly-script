import { Button } from "@poly/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@poly/ui/dialog";
import { useQuery } from "@tanstack/react-query";
import { History, Loader2, User } from "lucide-react";
import { api } from "../../../../../lib/api";

interface EditHistoryModalProps {
  transcriptId: string;
  onClose: () => void;
}

interface TranscriptEdit {
  id: string;
  user_email?: string | null;
  created_at: string;
  field_edited: string;
  segment_id: number | null;
  previous_text: string | null;
  new_text: string | null;
}

export function EditHistoryModal({ transcriptId, onClose }: EditHistoryModalProps) {
  const { data: history, isLoading } = useQuery({
    queryKey: ["transcript-history", transcriptId],
    queryFn: () => api.getTranscriptHistory(transcriptId),
  });

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="sm:max-w-lg max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <History className="w-5 h-5" />
            Edit History
          </DialogTitle>
          <DialogDescription>View all edits made to this transcript.</DialogDescription>
        </DialogHeader>

        <div className="py-4">
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
            </div>
          ) : !history || history.edits.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              No edits have been made to this transcript.
            </div>
          ) : (
            <div className="space-y-4">
              {history.edits.map((edit: TranscriptEdit) => (
                <div
                  key={edit.id}
                  className="p-4 border rounded-lg space-y-2 hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <User className="w-4 h-4 text-muted-foreground" />
                      <span className="text-sm font-medium">
                        {edit.user_email || "Unknown User"}
                      </span>
                    </div>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(edit.created_at)}
                    </span>
                  </div>

                  <div className="text-xs text-muted-foreground">
                    Changed: {edit.field_edited}
                    {edit.segment_id !== null && ` (Segment ${edit.segment_id})`}
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div className="p-2 bg-destructive/10 dark:bg-destructive/20 rounded border border-destructive/30 dark:border-destructive/40">
                      <div className="text-xs text-destructive dark:text-destructive/80 mb-1">Before</div>
                      <p className="line-clamp-2">{edit.previous_text}</p>
                    </div>
                    <div className="p-2 bg-success/10 dark:bg-success/20 rounded border border-success/30 dark:border-success/40">
                      <div className="text-xs text-success dark:text-success/80 mb-1">After</div>
                      <p className="line-clamp-2">{edit.new_text}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="flex justify-end">
          <Button variant="outline" onClick={onClose}>
            Close
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  );
}
