import { API_URL } from "@poly/ui";
import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Pause, Play, Volume2, VolumeX } from "lucide-react";
import { forwardRef, useEffect, useImperativeHandle, useRef, useState } from "react";

interface AudioPlayerCardProps {
  jobId: string;
  transcriptId: string;
  onTimeChange?: (seconds: number) => void;
}

export interface AudioPlayerHandle {
  seekTo: (seconds: number) => void;
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, "0")}`;
}

export const AudioPlayerCard = forwardRef<AudioPlayerHandle, AudioPlayerCardProps>(
  ({ jobId, transcriptId, onTimeChange }, ref) => {
    const audioRef = useRef<HTMLAudioElement>(null);
    const [isPlaying, setIsPlaying] = useState(false);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const [volume, setVolume] = useState(1);
    const [isMuted, setIsMuted] = useState(false);
    const [audioError, setAudioError] = useState(false);

    // Expose seekTo so segments can click-to-jump
    useImperativeHandle(
      ref,
      () => ({
        seekTo: (seconds: number) => {
          const audio = audioRef.current;
          if (!audio) return;
          audio.currentTime = seconds;
          setCurrentTime(seconds);
          onTimeChange?.(seconds);
          if (!isPlaying) {
            audio.play().catch(() => {});
            setIsPlaying(true);
          }
        },
      }),
      [isPlaying, onTimeChange],
    );

    useEffect(() => {
      const audio = audioRef.current;
      if (!audio) return;

      const handleLoadedMetadata = () => setDuration(audio.duration);
      const handleTimeUpdate = () => {
        setCurrentTime(audio.currentTime);
        onTimeChange?.(audio.currentTime);
      };
      const handleEnded = () => setIsPlaying(false);
      const handleError = () => setAudioError(true);

      audio.addEventListener("loadedmetadata", handleLoadedMetadata);
      audio.addEventListener("timeupdate", handleTimeUpdate);
      audio.addEventListener("ended", handleEnded);
      audio.addEventListener("error", handleError);

      return () => {
        audio.removeEventListener("loadedmetadata", handleLoadedMetadata);
        audio.removeEventListener("timeupdate", handleTimeUpdate);
        audio.removeEventListener("ended", handleEnded);
        audio.removeEventListener("error", handleError);
      };
    }, [onTimeChange]);

    const togglePlay = () => {
      const audio = audioRef.current;
      if (!audio) return;
      if (isPlaying) {
        audio.pause();
      } else {
        audio.play().catch(() => setAudioError(true));
      }
      setIsPlaying(!isPlaying);
    };

    const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
      const audio = audioRef.current;
      if (!audio) return;
      const time = parseFloat(e.target.value);
      audio.currentTime = time;
      setCurrentTime(time);
      onTimeChange?.(time);
    };

    const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      const audio = audioRef.current;
      const v = parseFloat(e.target.value);
      setVolume(v);
      if (audio) audio.volume = v;
      setIsMuted(v === 0);
    };

    const toggleMute = () => {
      const audio = audioRef.current;
      if (!audio) return;
      const newMuted = !isMuted;
      audio.muted = newMuted;
      setIsMuted(newMuted);
    };

    // Build URL: authenticated via bearer token passed as query param for <audio> tag
    const token = localStorage.getItem("access_token") ?? "";
    const audioUrl = `${API_URL}/jobs/${jobId}/audio?access_token=${encodeURIComponent(token)}`;
    const captionsSrc = `${API_URL}/transcripts/${transcriptId}/export?format=vtt`;

    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Audio Player</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {audioError ? (
            <div className="text-center py-4 text-sm text-muted-foreground">
              Audio file unavailable for this job.
            </div>
          ) : (
            <>
              <audio ref={audioRef} src={audioUrl} preload="metadata" crossOrigin="use-credentials">
                <track kind="captions" srcLang="en" src={captionsSrc} label="English captions" />
              </audio>

              {/* Play / Pause */}
              <div className="flex items-center justify-center">
                <Button
                  variant="outline"
                  size="icon"
                  onClick={togglePlay}
                  className="w-12 h-12 rounded-full"
                  aria-label={isPlaying ? "Pause audio" : "Play audio"}
                >
                  {isPlaying ? (
                    <Pause className="w-5 h-5" aria-hidden="true" />
                  ) : (
                    <Play className="w-5 h-5" aria-hidden="true" />
                  )}
                </Button>
              </div>

              {/* Seek bar */}
              <div className="space-y-1">
                <input
                  type="range"
                  min={0}
                  max={duration || 100}
                  step={0.1}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full accent-primary"
                  aria-label="Seek audio position"
                />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>{formatTime(currentTime)}</span>
                  <span>{formatTime(duration)}</span>
                </div>
              </div>

              {/* Volume */}
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={toggleMute}
                  className="text-muted-foreground hover:text-foreground transition-colors"
                  aria-label={isMuted ? "Unmute" : "Mute"}
                >
                  {isMuted ? (
                    <VolumeX className="w-4 h-4" aria-hidden="true" />
                  ) : (
                    <Volume2 className="w-4 h-4" aria-hidden="true" />
                  )}
                </button>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.05}
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="w-24 accent-primary"
                  aria-label="Volume"
                />
                <span className="text-xs text-muted-foreground">Click a segment to jump</span>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    );
  },
);

AudioPlayerCard.displayName = "AudioPlayerCard";
