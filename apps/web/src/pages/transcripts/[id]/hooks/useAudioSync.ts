import { useState, useEffect, useRef, useCallback } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../../../lib/api";

interface AudioSyncOptions {
  transcriptId: string;
  segments: Array<{ id: number; start_ms: number; end_ms: number; text: string }>;
  onActiveSegmentChange?: (segmentId: number) => void;
}

export function useAudioSync({
  transcriptId,
  segments,
  onActiveSegmentChange,
}: AudioSyncOptions) {
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSegmentId, setActiveSegmentId] = useState<number | null>(null);
  
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const containerRef = useRef<HTMLDivElement | null>(null);
  const scrollToRef = useRef<NodeJS.Timeout | null>(null);

  // Get audio URL
  const { data: audioData } = useQuery({
    queryKey: ['audio', transcriptId],
    queryFn: () => fetch(
      `${import.meta.env.VITE_API_URL || "http://localhost:8000"}/v1/jobs/${transcriptId}/audio`,
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      }
    ).then(r => r.json()),
    enabled: !!transcriptId,
  });

  // Find active segment based on current time
  const findActiveSegment = useCallback((timeMs: number): number | null => {
    for (let i = 0; i < segments.length; i++) {
      const seg = segments[i];
      if (timeMs >= seg.start_ms && timeMs < seg.end_ms) {
        return seg.id;
      }
    }
    return null;
  }, [segments]);

  // Scroll active segment into view
  const scrollToSegment = useCallback((segmentId: number) => {
    if (!containerRef.current) return;

    const segmentEl = containerRef.current.querySelector(`[data-segment-id="${segmentId}"]`);
    if (!segmentEl) return;

    // Smooth scroll with offset to center segment
    const containerRect = containerRef.current.getBoundingClientRect();
    const segmentRect = segmentEl.getBoundingClientRect();
    const scrollTop = containerRef.current.scrollTop +
      segmentRect.top -
      containerRect.top -
      (containerRect.height / 2) +
      (segmentRect.height / 2);

    containerRef.current.scrollTo({
      top: scrollTop,
      behavior: 'smooth',
    });
  }, []);

  // Handle audio time updates
  const handleTimeUpdate = useCallback(() => {
    if (!audioRef.current) return;

    const newCurrentTime = audioRef.current.currentTime;
    const timeMs = newCurrentTime * 1000; // Convert to milliseconds
    
    setCurrentTime(newCurrentTime);

    // Find active segment
    const segmentId = findActiveSegment(timeMs);
    if (segmentId !== null && segmentId !== activeSegmentId) {
      setActiveSegmentId(segmentId);
      onActiveSegmentChange?.(segmentId);
      
      // Auto-scroll to active segment
      if (scrollToRef.current) {
        clearTimeout(scrollToRef.current);
      }
      scrollToRef.current = setTimeout(() => {
        scrollToSegment(segmentId);
      }, 500); // Debounce scroll
    }
  }, [audioRef, findActiveSegment, activeSegmentId, onActiveSegmentChange, scrollToSegment]);

  // Handle play/pause
  const togglePlay = useCallback(() => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  }, [isPlaying]);

  // Handle seeking to segment
  const seekToSegment = useCallback((segmentId: number) => {
    const segment = segments.find(s => s.id === segmentId);
    if (!segment || !audioRef.current) return;

    // Seek to middle of segment
    const seekTime = (segment.start_ms + segment.end_ms) / 2 / 1000; // Convert to seconds
    audioRef.current.currentTime = seekTime;
    setCurrentTime(seekTime);
  }, [segments]);

  // Handle manual seek
  const handleSeek = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (!audioRef.current) return;

    const time = parseFloat(e.target.value);
    audioRef.current.currentTime = time;
    setCurrentTime(time);
  }, []);

  // Format time for display
  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  }, []);

  // Cleanup
  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
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
      if (scrollToRef.current) {
        clearTimeout(scrollToRef.current);
      }
    };
  }, [audioRef, handleTimeUpdate]);

  return {
    audioRef,
    containerRef,
    audioUrl: audioData?.presigned_url || audioData?.storage_uri,
    isPlaying,
    currentTime,
    duration,
    activeSegmentId,
    togglePlay,
    seekToSegment,
    handleSeek,
    formatTime,
  };
}
