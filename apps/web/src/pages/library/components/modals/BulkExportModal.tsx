import { Button } from "@poly-ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@poly-ui/dialog";
import { FileJson, FileText, Download } from "lucide-react";

interface BulkExportModalProps {
  transcriptIds: string[];
  onClose: () => void;
}

export function BulkExportModal({ transcriptIds, onClose }: BulkExportModalProps) {
  const formats = [
    { id: "txt", label: "Plain Text (TXT)", icon: FileText, description: "All as one file" },
    { id: "json", label: "JSON", icon: FileJson, description: "Structured data" },
    { id: "srt", label: "SubRip (SRT)", icon: Download, description: "For video players" },
    { id: "vtt", label: "WebVTT (VTT)", icon: Download, description: "For web players" },
  ];

  const handleExport = async (format: "txt" | "json" | "srt" | "vtt") => {
    // Download each transcript
    for (const id of transcriptIds) {
      try {
        const blob = await fetch(
          `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/v1/transcripts/${id}/export?format=${format}`,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("access_token")}`,
            },
          }
        ).then((r) => r.blob());

        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `transcript_${id.slice(0, 8)}_${Date.now()}.${format}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
      } catch (err) {
        console.error("Failed to export transcript:", id, err);
      }
    }
    onClose();
  };

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Bulk Export</DialogTitle>
          <DialogDescription>
            Export {transcriptIds.length} transcripts in your chosen format.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-3 py-4">
          {formats.map((format) => (
            <button
              key={format.id}
              onClick={() => handleExport(format.id as "txt" | "json" | "srt" | "vtt")}
              className="flex items-center gap-3 p-3 rounded-lg border hover:bg-muted transition-colors text-left"
            >
              <format.icon className="w-5 h-5 text-muted-foreground" />
              <div className="flex-1">
                <div className="font-medium">{format.label}</div>
                <div className="text-sm text-muted-foreground">
                  {format.description}
                </div>
              </div>
            </button>
          ))}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
