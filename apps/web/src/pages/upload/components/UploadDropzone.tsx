import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { AudioWaveform, CheckCircle2, FileCode, FileMusic, Upload } from "lucide-react";
import { useCallback, useState } from "react";

interface UploadDropzoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function UploadDropzone({ onFileSelected, disabled = false }: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadProgress, setUploadProgress] = useState(0);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const simulateUpload = useCallback(
    (file: File) => {
      setSelectedFile(file);
      setUploadProgress(0);

      const interval = setInterval(() => {
        setUploadProgress((prev) => {
          if (prev >= 100) {
            clearInterval(interval);
            onFileSelected(file);
            return 100;
          }
          return prev + 10;
        });
      }, 50);
    },
    [onFileSelected],
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files);
      const audioFile = files.find((file) => file.type.startsWith("audio/"));

      if (audioFile) {
        simulateUpload(audioFile);
      }
    },
    [disabled, simulateUpload],
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (disabled) return;

      const file = e.target.files?.[0];
      if (file?.type.startsWith("audio/")) {
        simulateUpload(file);
      }
    },
    [disabled, simulateUpload],
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const index = Math.min(sizes.length - 1, i);
    const formattedSize = parseFloat((bytes / k ** i).toFixed(2));
    return `${formattedSize} ${sizes[index]}`;
  };

  return (
    <Card className="precision-card overflow-hidden smooth-transition">
      <CardContent className="p-0">
        <button
          type="button"
          className={`relative min-h-[320px] border-2 rounded-xl smooth-transition overflow-hidden touch-manipulation ${
            isDragging
              ? "border-primary bg-primary/5 shadow-[0_0_0_4px_rgba(79,70,229,0.1)]"
              : "border-dashed border-muted-foreground/25 hover:border-primary/60"
          } ${disabled ? "opacity-50 pointer-events-none" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => document.getElementById("file-input")?.click()}
          disabled={disabled}
        >
          <input
            id="file-input"
            type="file"
            accept="audio/*"
            className="hidden"
            disabled={disabled}
            onChange={handleFileSelect}
            aria-label="Upload audio file"
          />

          <div className="relative z-10 flex flex-col items-center justify-center h-full p-8">
            {selectedFile ? (
              <div className="w-full max-w-md space-y-6 text-center">
                {uploadProgress < 100 ? (
                  <div className="space-y-4 animate-fade-in-up">
                    <div className="flex items-center justify-center">
                      <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center animate-gentle-pulse">
                        <Upload className="h-10 w-10 text-primary" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-sm font-medium text-muted-foreground">Uploading...</p>
                      <div className="h-2 bg-muted rounded-full overflow-hidden">
                        <div
                          className="h-full precision-gradient smooth-transition"
                          style={{ width: `${uploadProgress}%` }}
                        />
                      </div>
                      <p className="text-xs text-muted-foreground">{uploadProgress}%</p>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4 animate-fade-in-up">
                    <div className="flex items-center justify-center">
                      <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-emerald-500/10 to-emerald-600/10 flex items-center justify-center">
                        <CheckCircle2 className="h-10 w-10 text-emerald-600 dark:text-emerald-400" />
                      </div>
                    </div>
                    <div className="space-y-2">
                      <p className="text-base font-semibold text-foreground">{selectedFile.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {formatFileSize(selectedFile.size)}
                      </p>
                      <div className="flex items-center justify-center gap-1 text-xs text-emerald-600 dark:text-emerald-400">
                        <CheckCircle2 className="h-3.5 w-3.5" />
                        <span>Ready for transcription</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="space-y-6 text-center animate-fade-in-up">
                <div className="flex items-center justify-center">
                  <div className="h-20 w-20 rounded-2xl bg-gradient-to-br from-primary/10 to-accent/10 flex items-center justify-center smooth-transition hover:from-primary/20 hover:to-accent/20">
                    <Upload className="h-10 w-10 text-primary" />
                  </div>
                </div>
                <div className="space-y-3">
                  <p className="text-base font-medium text-foreground">
                    Drop audio file here or click to browse
                  </p>
                  <p className="text-sm text-muted-foreground">Supports MP3, WAV, M4A, OGG, WEBM</p>
                  <p className="text-xs text-muted-foreground/70">Maximum file size: 100MB</p>
                </div>
                <Button
                  variant="default"
                  className="precision-gradient shadow-lg shadow-primary/20 hover:shadow-xl hover:shadow-primary/30 smooth-transition"
                  disabled={disabled}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Choose File
                </Button>
              </div>
            )}
          </div>

          <div className="absolute inset-0 overflow-hidden pointer-events-none">
            <FileMusic className="file-icon-1 h-12 w-12 text-primary/5 animate-float" />
            <AudioWaveform className="file-icon-2 h-10 w-10 text-accent/5 animate-float" />
            <FileCode className="file-icon-3 h-8 w-8 text-primary/5 animate-float" />
            <FileMusic className="file-icon-4 h-10 w-10 text-accent/5 animate-float" />
          </div>
        </button>
      </CardContent>
    </Card>
  );
}
