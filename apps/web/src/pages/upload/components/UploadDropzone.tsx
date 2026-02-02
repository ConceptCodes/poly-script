import { useCallback, useState } from "react";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { Upload, FileAudio } from "lucide-react";

interface UploadDropzoneProps {
  onFileSelected: (file: File) => void;
  disabled?: boolean;
}

export function UploadDropzone({ onFileSelected, disabled = false }: UploadDropzoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);

      if (disabled) return;

      const files = Array.from(e.dataTransfer.files);
      const audioFile = files.find((file) =>
        file.type.startsWith("audio/")
      );

      if (audioFile) {
        setSelectedFile(audioFile);
        onFileSelected(audioFile);
      }
    },
    [disabled, onFileSelected]
  );

  const handleFileSelect = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      if (disabled) return;

      const file = e.target.files?.[0];
      if (file && file.type.startsWith("audio/")) {
        setSelectedFile(file);
        onFileSelected(file);
      }
    },
    [disabled, onFileSelected]
  );

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    const index = Math.min(sizes.length - 1, i);
    const formattedSize = parseFloat((bytes / Math.pow(k, i)).toFixed(2));
    return `${formattedSize} ${sizes[index]}`;
  };

  return (
    <Card className={isDragging ? "ring-2 ring-primary" : ""}>
      <CardContent>
        <div
          className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors cursor-pointer ${
            isDragging
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/25 hover:border-primary/50"
          } ${disabled ? "opacity-50 pointer-events-none" : ""}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <input
            type="file"
            accept="audio/*"
            className="hidden"
            disabled={disabled}
            onChange={handleFileSelect}
          />
          {selectedFile ? (
            <div className="space-y-4">
              <div className="flex items-center justify-center">
                <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center">
                  <FileAudio className="h-8 w-8 text-primary" />
                </div>
              </div>
              <p className="text-sm font-medium text-muted-foreground">
                {selectedFile.name}
              </p>
              <p className="text-xs text-muted-foreground">
                {formatFileSize(selectedFile.size)}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="h-16 w-16 bg-muted rounded-full flex items-center justify-center mx-auto">
                <Upload className="h-8 w-8 text-muted-foreground" />
              </div>
              <p className="text-sm font-medium text-muted-foreground">
                Drag and drop audio file here, or click to select
              </p>
              <p className="text-xs text-muted-foreground">
                MP3, WAV, M4A, OGG, WEBM
              </p>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
}
