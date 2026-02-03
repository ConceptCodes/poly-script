import { Badge } from "@poly/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Progress } from "@poly/ui/progress";
import { formatDistanceToNow } from "date-fns";
import { Clock, FileText, Volume2 } from "lucide-react";

interface ProgressCardProps {
  filename: string;
  status: string;
  progressPct: number;
  progressStage: string | null;
  language: string | null;
  createdAt: string;
  audioDuration: number | null;
}

export function ProgressCard({
  filename,
  status,
  progressPct,
  progressStage,
  language,
  createdAt,
  audioDuration,
}: ProgressCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case "QUEUED":
        return "bg-yellow-500";
      case "RUNNING":
        return "bg-blue-500";
      case "SUCCEEDED":
        return "bg-green-500";
      case "FAILED":
        return "bg-red-500";
      case "CANCELED":
        return "bg-gray-500";
      default:
        return "bg-gray-500";
    }
  };

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return "--:--";
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="w-5 h-5 text-muted-foreground" />
            <CardTitle className="text-xl">{filename}</CardTitle>
            <Badge className={getStatusColor(status)}>{status}</Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        <div>
          <div className="flex items-center justify-between text-sm mb-2">
            <span className="text-muted-foreground font-medium">
              {progressStage || "Initializing"}
            </span>
            <span className="font-semibold text-lg">{progressPct}%</span>
          </div>
          <Progress value={progressPct} className="w-full h-2" />
        </div>

        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-muted-foreground" />
            <span className="text-muted-foreground">
              {formatDistanceToNow(new Date(createdAt), { addSuffix: true })}
            </span>
          </div>
          {language && (
            <div className="flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">{language.toUpperCase()}</span>
            </div>
          )}
          {audioDuration && (
            <div className="flex items-center gap-2">
              <Volume2 className="w-4 h-4 text-muted-foreground" />
              <span className="text-muted-foreground">{formatDuration(audioDuration)}</span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
