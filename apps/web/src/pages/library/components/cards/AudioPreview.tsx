import { Button } from "@poly/ui/button";
import { Pause, Play, Volume2 } from "lucide-react";
import { useRef, useState } from "react";

interface AudioPreviewProps {
  transcriptId: string;
  audioUrl: string;
  className?: string;
}

export function AudioPreview({ transcriptId, audioUrl, className }: AudioPreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const togglePlay = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const handleEnded = () => {
    setIsPlaying(false);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  const captionsSrc = `${import.meta.env.VITE_API_URL || "http://localhost:8000/v1"}/transcripts/${transcriptId}/export?format=vtt`;

  return (
    <div className={`flex items-center gap-3 ${className || ""}`}>
      <audio
        ref={audioRef}
        src={audioUrl}
        className="hidden"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={handleLoadedMetadata}
        onEnded={handleEnded}
      >
        <track kind="captions" srcLang="en" src={captionsSrc} label="English captions" />
      </audio>

      <Button
        variant="outline"
        size="sm"
        onClick={togglePlay}
        className="w-9 h-9 p-0 flex-shrink-0"
        aria-label={isPlaying ? "Pause preview" : "Play preview"}
      >
        {isPlaying ? (
          <Pause className="w-4 h-4" aria-hidden="true" />
        ) : (
          <Play className="w-4 h-4" aria-hidden="true" />
        )}
      </Button>

      <div className="flex-1">
        <input
          type="range"
          min={0}
          max={duration || 100}
          value={currentTime}
          onChange={(e) => {
            if (audioRef.current) {
              const time = parseFloat(e.target.value);
              audioRef.current.currentTime = time;
              setCurrentTime(time);
            }
          }}
          className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
          aria-label="Seek audio"
        />
        <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
          <span>{formatTime(currentTime)}</span>
          <span>{formatTime(duration)}</span>
        </div>
      </div>

      <Volume2 className="w-4 h-4 text-muted-foreground flex-shrink-0" aria-hidden="true" />
    </div>
  );
}
