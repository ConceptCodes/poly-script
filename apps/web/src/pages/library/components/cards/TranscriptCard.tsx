import { Card, CardContent } from "@poly-ui/card";
import { Badge } from "@poly-ui/badge";
import { Button } from "@poly-ui/button";
import {
  CheckSquare,
  Square,
  FileText,
  Download,
  Trash2,
  ExternalLink,
} from "lucide-react";

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
}

export function TranscriptCard({
  transcript,
  viewMode,
  isSelected,
  onSelect,
  onView,
  onExport,
  onDelete,
}: TranscriptCardProps) {
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
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
              <span>{formatDate(transcript.created_at)}</span>
            </div>
          </div>
          <button
            onClick={onSelect}
            className="flex-shrink-0 mt-1"
          >
            {isSelected ? (
              <CheckSquare className="w-5 h-5 text-primary" />
            ) : (
              <Square className="w-5 h-5 text-muted-foreground" />
            )}
          </button>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {transcript.text_preview}
        </p>
        <div className="flex items-center gap-2 mt-3">
          <Button variant="ghost" size="sm" onClick={onView}>
            <FileText className="w-4 h-4 mr-1" />
            View
          </Button>
          <div className="relative group">
            <Button variant="ghost" size="sm">
              <Download className="w-4 h-4 mr-1" />
              Export
            </Button>
            <div className="absolute left-0 top-full mt-1 hidden group-hover:block z-10">
              <div className="bg-popover border rounded-lg shadow-lg p-1">
                <button
                  onClick={() => onExport("txt")}
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded"
                >
                  TXT
                </button>
                <button
                  onClick={() => onExport("json")}
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded"
                >
                  JSON
                </button>
                <button
                  onClick={() => onExport("srt")}
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded"
                >
                  SRT
                </button>
                <button
                  onClick={() => onExport("vtt")}
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-muted rounded"
                >
                  VTT
                </button>
              </div>
            </div>
          </div>
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
            <button
              onClick={onSelect}
              className="flex-shrink-0"
            >
              {isSelected ? (
                <CheckSquare className="w-5 h-5 text-primary" />
              ) : (
                <Square className="w-5 h-5 text-muted-foreground" />
              )}
            </button>
            <div>
              <h3 className="font-medium">
                {transcript.job_filename || `Transcript ${transcript.id.slice(0, 8)}`}
              </h3>
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <Badge variant="secondary" className="text-xs">
                  {transcript.language.toUpperCase()}
                </Badge>
                <span>{formatDate(transcript.created_at)}</span>
              </div>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={onView}>
            <ExternalLink className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-3 mb-3">
          {transcript.text_preview}
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={onView}
          >
            <FileText className="w-4 h-4 mr-1" />
            Edit
          </Button>
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => onExport("txt")}
          >
            <Download className="w-4 h-4 mr-1" />
            Export
          </Button>
        </div>
      </>
    );

  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-md ${
        isSelected ? "ring-2 ring-primary" : ""
      }`}
    >
      <CardContent className={viewMode === "list" ? "py-4" : "p-4"}>
        {formatContent()}
      </CardContent>
    </Card>
  );
}
