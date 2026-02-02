import { useRef, useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Button } from "@poly/ui/button";
import { Play, Pause, Volume2 } from "lucide-react";

interface AudioPlayerCardProps {
  jobId: string;
  audioDuration: number | null;
}

export function AudioPlayerCard({ jobId, audioDuration }: AudioPlayerCardProps) {
  const audioRef = useRef<HTMLAudioElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
    };

    audio.addEventListener("loadedmetadata", handleLoadedMetadata);
    audio.addEventListener("timeupdate", handleTimeUpdate);
    audio.addEventListener("ended", handleEnded);

    return () => {
      audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
      audio.removeEventListener("timeupdate", handleTimeUpdate);
      audio.removeEventListener("ended", handleEnded);
    };
  }, []);

  const togglePlay = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const audio = audioRef.current;
    if (!audio) return;

    const time = parseFloat(e.target.value);
    audio.currentTime = time;
    setCurrentTime(time);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  // Audio URL would come from the job/audio asset
  const audioUrl = `/api/v1/jobs/${jobId}/audio`;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Audio Player</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <audio ref={audioRef} src={audioUrl} preload="metadata" />

        <div className="flex items-center justify-center">
          <Button
            variant="outline"
            size="icon"
            onClick={togglePlay}
            className="w-12 h-12 rounded-full"
          >
            {isPlaying ? (
              <Pause className="w-5 h-5" />
            ) : (
              <Play className="w-5 h-5" />
            )}
          </Button>
        </div>

        <div className="space-y-2">
          <input
            type="range"
            min={0}
            max={duration || 100}
            value={currentTime}
            onChange={handleSeek}
            className="w-full"
          />
          <div className="flex justify-between text-xs text-muted-foreground">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Volume2 className="w-4 h-4" />
          <span>Use controls above or click on segments to jump to that position</span>
        </div>
      </CardContent>
    </Card>
  );
}
