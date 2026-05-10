import { Card, CardContent } from "@poly/ui/card";
import { AlertCircle, CheckCircle2, Globe, Link2, Link as LinkIcon, Youtube } from "lucide-react";
import { useState } from "react";

interface UrlInputProps {
  value: string;
  onChange: (value: string) => void;
  error: string;
  disabled?: boolean;
}

type UrlType = "youtube" | "s3" | "direct" | "invalid" | null;

export function UrlInput({ value, onChange, error, disabled }: UrlInputProps) {
  const [focused, setFocused] = useState(false);

  const detectUrlType = (url: string): UrlType => {
    if (!url.trim()) return null;
    if (url.includes("youtube.com") || url.includes("youtu.be")) return "youtube";
    if (url.includes(".s3") && url.includes("amazonaws.com")) return "s3";
    // Direct URL could be any http(s) URL or hosted file
    if (url.startsWith("http://") || url.startsWith("https://")) return "direct";
    // Some providers host direct files on Google Drive; mark as direct for this UI
    if (url.includes("drive.google.com")) return "direct";
    return "invalid";
  };

  const urlType = detectUrlType(value);
  const isValid = !!urlType && urlType !== "invalid" && !error;

  const getUrlIcon = () => {
    switch (urlType) {
      case "youtube":
        return <Youtube className="h-5 w-5" />;
      case "s3":
        return <Globe className="h-5 w-5" />;
      case "direct":
        return <LinkIcon className="h-5 w-5" />;
      case "invalid":
        return <AlertCircle className="h-5 w-5" />;
      default:
        return <Link2 className="h-5 w-5" />;
    }
  };

  const getStatusIcon = () => {
    if (error) return <AlertCircle className="h-4 w-4 text-destructive" />;
    if (isValid) return <CheckCircle2 className="h-4 w-4 text-success dark:text-success/80" />;
    return null;
  };

  const getStatusText = () => {
    if (error) return error;
    if (urlType === "youtube") return "YouTube URL detected";
    if (urlType === "s3") return "S3 URL detected";
    if (urlType === "direct") return "Direct URL detected";
    return null;
  };

  return (
    <Card
      className={`border-2 rounded-xl transition-all ${
        focused ? "ring-2 ring-primary/20 shadow-lg" : error ? "ring-2 ring-destructive/20" : ""
      }`}
    >
      <CardContent className="p-6 space-y-4">
        <div className="space-y-2">
          <label htmlFor="url-input" className="text-sm font-medium text-foreground">
            Audio URL
          </label>

          <div
            className={`relative flex items-center gap-3 px-4 py-3 rounded-xl border-2 transition-all ${
              focused
                ? "border-primary bg-primary/5"
                : error
                  ? "border-destructive bg-destructive/5"
                  : "border-border bg-background hover:border-primary/40"
            }`}
          >
            <div
              className={`flex items-center justify-center h-9 w-9 rounded-lg transition-all ${
                urlType === "youtube"
                  ? "bg-destructive/10 text-destructive dark:text-destructive/80"
                  : urlType === "s3"
                    ? "bg-warning/10 text-warning dark:text-warning/80"
                    : urlType === "direct"
                      ? "bg-primary/10 text-primary"
                      : urlType === "invalid"
                        ? "bg-destructive/10 text-destructive"
                        : "bg-muted/30 text-muted-foreground"
              }`}
            >
              {getUrlIcon()}
            </div>

            <input
              id="url-input"
              type="url"
              placeholder="https://youtube.com/watch?v=... or direct audio URL"
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
              disabled={disabled}
              className="flex-1 bg-transparent border-0 outline-none text-foreground placeholder:text-muted-foreground/60"
              aria-label="Audio URL input"
            />

            {getStatusIcon()}
          </div>

          {getStatusText() && (
            <div
              className={`flex items-center gap-2 text-sm ${
                error ? "text-destructive animate-shake" : "text-muted-foreground"
              }`}
            >
              {getStatusIcon()}
              <span>{getStatusText()}</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 pt-2 border-t border-border/40">
          <div className="flex items-center gap-2 text-xs text-muted-foreground/70">
            <Youtube className="h-3.5 w-3.5" />
            <span>YouTube</span>
          </div>
          <div className="h-1 w-1 rounded-full bg-muted-foreground/30" />
          <div className="flex items-center gap-2 text-xs text-muted-foreground/70">
            <Globe className="h-3.5 w-3.5" />
            <span>S3</span>
          </div>
          <div className="h-1 w-1 rounded-full bg-muted-foreground/30" />
          <div className="flex items-center gap-2 text-xs text-muted-foreground/70">
            <LinkIcon className="h-3.5 w-3.5" />
            <span>Direct</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
