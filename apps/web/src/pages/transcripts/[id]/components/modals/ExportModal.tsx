import { Button } from "@poly/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@poly/ui/dialog";
import { FileJson, FileText, Download } from "lucide-react";

interface ExportModalProps {
  onClose: () => void;
  onExport: (format: "txt" | "json" | "srt" | "vtt") => void;
}

export function ExportModal({ onClose, onExport }: ExportModalProps) {
  const formats = [
    { id: "txt", label: "Plain Text", icon: FileText, description: ".txt" },
    { id: "json", label: "JSON", icon: FileJson, description: ".json" },
    { id: "srt", label: "SubRip (SRT)", icon: Download, description: ".srt" },
    { id: "vtt", label: "WebVTT (VTT)", icon: Download, description: ".vtt" },
  ];

  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Export Transcript</DialogTitle>
          <DialogDescription>
            Choose a format to export your transcript.
          </DialogDescription>
        </DialogHeader>

        <div className="grid gap-3 py-4">
          {formats.map((format) => (
            <button
              key={format.id}
              onClick={() => onExport(format.id as "txt" | "json" | "srt" | "vtt")}
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
