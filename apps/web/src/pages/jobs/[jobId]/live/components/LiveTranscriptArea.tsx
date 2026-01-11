import { Card, CardContent } from "@poly-ui/card";
import { CheckCircle2 } from "lucide-react";
import { useEffect, useRef } from "react";

interface Segment {
  id: number;
  start_ms: number;
  end_ms: number;
  text: string;
  speaker: string | null;
}

interface LiveTranscriptAreaProps {
  segments: Segment[];
  isComplete: boolean;
}

export function LiveTranscriptArea({ segments, isComplete }: LiveTranscriptAreaProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const latestSegmentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (latestSegmentRef.current) {
      latestSegmentRef.current.scrollIntoView({ behavior: "smooth", block: "end" });
    }
  }, [segments.length]);

  const formatTimestamp = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const mins = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${mins}:${remainingSeconds.toString().padStart(2, "0")}`;
  };

  if (segments.length === 0 && !isComplete) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <p className="text-muted-foreground">
            Waiting for transcript segments...
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="h-[600px]">
      <CardContent className="p-0 h-full">
        <div
          ref={scrollRef}
          className="h-full overflow-y-auto p-6"
        >
          <div className="space-y-3">
            {segments.map((segment, index) => (
              <div
                key={segment.id}
                ref={index === segments.length - 1 ? latestSegmentRef : null}
                className={`flex items-start gap-3 p-3 rounded-lg transition-colors ${
                  index === segments.length - 1 && !isComplete
                    ? "bg-primary/10 border border-primary/20"
                    : ""
                }`}
              >
                <span className="text-sm font-mono text-muted-foreground whitespace-nowrap">
                  [{formatTimestamp(segment.start_ms)}]
                </span>
                <p className="flex-1 text-foreground leading-relaxed">
                  {segment.text}
                </p>
                {segment.speaker && (
                  <span className="text-xs font-semibold text-primary bg-primary/10 px-2 py-1 rounded">
                    {segment.speaker}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
