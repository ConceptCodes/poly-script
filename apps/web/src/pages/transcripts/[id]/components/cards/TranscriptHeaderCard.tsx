import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Badge } from "@poly/ui/badge";

interface TranscriptHeaderCardProps {
  language: string;
  engineVersion: string;
  createdAt: string;
  updatedAt: string | null;
}

export function TranscriptHeaderCard({
  language,
  engineVersion,
  createdAt,
  updatedAt,
}: TranscriptHeaderCardProps) {
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
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Transcript Info</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Status</span>
          <Badge variant="default">Completed</Badge>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Language</span>
          <span className="font-medium">{language.toUpperCase()}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Engine</span>
          <span className="font-medium text-xs">{engineVersion}</span>
        </div>

        <div className="flex items-center justify-between">
          <span className="text-sm text-muted-foreground">Created</span>
          <span className="text-sm">{formatDate(createdAt)}</span>
        </div>

        {updatedAt && (
          <div className="flex items-center justify-between">
            <span className="text-sm text-muted-foreground">Last Modified</span>
            <span className="text-sm">{formatDate(updatedAt)}</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
