import { Zap } from "lucide-react";

interface UploadHeroProps {
  uploadMode: "file" | "url";
}

export function UploadHero({ uploadMode }: UploadHeroProps) {
  return (
    <div className="space-y-4 mb-8 animate-fade-in-up">
      <div className="flex items-start gap-4">
        <div className="flex items-center justify-center h-12 w-12 rounded-xl bg-gradient-to-br from-primary/10 to-accent/10 smooth-transition">
          <Zap className="h-6 w-6 precision-gradient-text" />
        </div>
        <div className="flex-1">
          <h1 className="text-3xl font-bold tracking-tight text-foreground mb-2">
            {uploadMode === "file" ? "Upload Audio" : "Transcribe from URL"}
          </h1>
          <p className="text-base text-muted-foreground">
            {uploadMode === "file"
              ? "Transform your audio files into accurate transcripts. Drag, drop, or browse to get started."
              : "Paste a YouTube or S3 URL to transcribe. Works with direct audio links too."}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2 text-sm text-muted-foreground/80">
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-primary/60" />
          MP3
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-primary/60" />
          WAV
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-primary/60" />
          M4A
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-primary/60" />
          OGG
        </span>
        <span className="flex items-center gap-1.5">
          <div className="h-1.5 w-1.5 rounded-full bg-primary/60" />
          WEBM
        </span>
        <span className="text-muted-foreground/40 mx-2">•</span>
        <span className="text-xs">Up to 100MB</span>
      </div>

      <div className="flex items-end gap-1 h-8">
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-1" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-2" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-3" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-4" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-5" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-4" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-3" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-2" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-1" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-3" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-5" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-2" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-4" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-1" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-3" />
        <div className="w-1 bg-gradient-to-t from-primary/80 to-primary/20 rounded-full animate-audio-wave-5" />
      </div>
    </div>
  );
}
