import { useState } from "react";
import { Button } from "@poly/ui/button";
import { Play, Pause, Volume2 } from "lucide-react";

interface AudioPreviewProps {
  transcriptId: string;
  audioUrl: string;
  className?: string;
}

export function AudioPreview({ transcriptId, audioUrl, className }: AudioPreviewProps) {
  const [isPlaying, setIsPlaying] = useState(false);
  const audioRef = useState<HTMLAudioElement | null>(() => null)[0];

  const togglePlay = () => {
    if (!audioRef) return;

    if (isPlaying) {
      audioRef.pause();
    } else {
      audioRef.play();
    }
    setIsPlaying(!isPlaying);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };

  return (
    <div className={`flex items-center gap-3 ${className || ""}`}>
      <audio
        ref={(el) => {
          if (el) {
            audioRef = el;
            el.addEventListener("ended", () => setIsPlaying(false));
          }
        }}
        src={audioUrl}
        className="hidden"
      />

      <Button
        variant="outline"
        size="sm"
        onClick={togglePlay}
        className="w-9 h-9 p-0 flex-shrink-0"
      >
        {isPlaying ? (
          <Pause className="w-4 h-4" />
        ) : (
          <Play className="w-4 h-4" />
        )}
      </Button>

      <div className="flex-1">
        <input
          type="range"
          min={0}
          max={100}
          value={audioRef?.currentTime ? (audioRef.currentTime / audioRef.duration) * 100 : 0}
          onChange={(e) => {
            if (audioRef && audioRef.duration) {
              const time = (parseFloat(e.target.value) / 100) * audioRef.duration;
              audioRef.currentTime = time;
            }
          }}
          className="w-full h-1 bg-muted rounded-lg appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary"
        />
        <div className="flex items-center justify-between text-xs text-muted-foreground mt-1">
          <span>
            {audioRef?.currentTime ? formatTime(audioRef.currentTime) : "0:00"}
          </span>
          <span>
            {audioRef?.duration ? formatTime(audioRef.duration) : "0:00"}
          </span>
        </div>
      </div>

      <Volume2 className="w-4 h-4 text-muted-foreground flex-shrink-0" />
    </div>
  );
}
