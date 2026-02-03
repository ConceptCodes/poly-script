import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { Checkbox } from "@poly/ui/checkbox";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@poly/ui/dropdown-menu";
import { Download, ExternalLink, FileText, Trash2 } from "lucide-react";
import { formatDate } from "../../../../lib/formatters";
import { AudioPreview } from "./AudioPreview";

interface TranscriptListItem {
  id: string;
  job_id: string;
  job_filename: string | null;
  text_preview: string;
  language: string;
  created_at: string;
  updated_at: string | null;
}

interface TranscriptCardProps {
  transcript: TranscriptListItem;
  viewMode: "grid" | "list";
  isSelected: boolean;
  onSelect: () => void;
  onView: () => void;
  onExport: (format: "txt" | "json" | "srt" | "vtt") => void;
  onDelete: () => void;
  audioPreview?: boolean;
  audioUrl?: string;
}

export function TranscriptCard({
  transcript,
  viewMode,
  isSelected,
  onSelect,
  onView,
  onExport,
  onDelete,
  audioPreview,
  audioUrl,
}: TranscriptCardProps) {
  const formatDisplayDate = (dateString: string) => {
    return formatDate(dateString);
  };

  const formatContent = () => {
    return viewMode === "list" ? (
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-4 mb-2">
          <div>
            <h3 className="font-medium truncate">
              {transcript.job_filename || `Transcript ${transcript.id.slice(0, 8)}`}
            </h3>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Badge variant="secondary">{transcript.language.toUpperCase()}</Badge>
              <span>{formatDisplayDate(transcript.created_at)}</span>
            </div>
          </div>
          <Checkbox
            checked={isSelected}
            onCheckedChange={onSelect}
            aria-label={isSelected ? "Deselect transcript" : "Select transcript"}
          />
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">{transcript.text_preview}</p>
        {audioPreview && audioUrl && (
          <AudioPreview transcriptId={transcript.id} audioUrl={audioUrl} className="mb-3" />
        )}
        <div className="flex items-center gap-2 mt-3">
          <Button variant="ghost" size="sm" onClick={onView}>
            <FileText className="w-4 h-4 mr-1" />
            View
          </Button>
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" size="sm">
                <Download className="w-4 h-4 mr-1" />
                Export
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => onExport("txt")}>TXT</DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExport("json")}>JSON</DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExport("srt")}>SRT</DropdownMenuItem>
              <DropdownMenuItem onClick={() => onExport("vtt")}>VTT</DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          <Button variant="ghost" size="sm" onClick={onDelete}>
            <Trash2 className="w-4 h-4 mr-1" />
            Delete
          </Button>
        </div>
      </div>
    ) : (
      <>
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-2">
            <Checkbox
              checked={isSelected}
              onCheckedChange={onSelect}
              aria-label={isSelected ? "Deselect transcript" : "Select transcript"}
            />
            <div>
              <h3 className="font-medium">
                {transcript.job_filename || `Transcript ${transcript.id.slice(0, 8)}`}
              </h3>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Badge variant="secondary" className="text-xs">
                  {transcript.language.toUpperCase()}
                </Badge>
                <span>{formatDisplayDate(transcript.created_at)}</span>
              </div>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onView} aria-label="View transcript details">
            <ExternalLink className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-3 mb-3">{transcript.text_preview}</p>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="flex-1" onClick={onView}>
            <FileText className="w-4 h-4 mr-1" />
            Edit
          </Button>
          <Button variant="outline" size="sm" className="flex-1" onClick={() => onExport("txt")}>
            <Download className="w-4 h-4 mr-1" />
            Export
          </Button>
        </div>
      </>
    );
  };

  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-md ${
        isSelected ? "ring-2 ring-primary" : ""
      }`}
    >
      <CardContent className={viewMode === "list" ? "py-4" : "p-4"}>{formatContent()}</CardContent>
    </Card>
  );
}
