import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button } from "@poly-ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly-ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@poly-ui/tabs";
import { 
  ArrowLeft, 
  Download, 
  History, 
  RotateCcw, 
  Save, 
  FileText,
  List,
  Loader2
} from "lucide-react";

import { api } from "../../lib/api";
import { TranscriptHeaderCard } from "./components/cards/TranscriptHeaderCard";
import { AudioPlayerCard } from "./components/cards/AudioPlayerCard";
import { FullTextEditor } from "./components/forms/FullTextEditor";
import { SegmentList } from "./components/SegmentList";
import { ExportModal } from "./components/modals/ExportModal";
import { RevertModal } from "./components/modals/RevertModal";
import { EditHistoryModal } from "./components/modals/EditHistoryModal";

interface Segment {
  id: number;
  start_ms: number;
  end_ms: number;
  text: string;
  speaker: string | null;
}

export function TranscriptEditorPage() {
  const { id: transcriptId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [activeTab, setActiveTab] = useState("full-text");
  const [showExportModal, setShowExportModal] = useState(false);
  const [showRevertModal, setShowRevertModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);

  const { data: transcript, isLoading, error } = useQuery({
    queryKey: ["transcript", transcriptId],
    queryFn: () => api.getTranscript(transcriptId!),
    enabled: !!transcriptId,
  });

  const updateTextMutation = useMutation({
    mutationFn: (text: string) => api.updateTranscriptFullText(transcriptId!, text),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transcript", transcriptId] });
      setLastSaved(new Date());
    },
  });

  const revertMutation = useMutation({
    mutationFn: () => api.revertTranscript(transcriptId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["transcript", transcriptId] });
      setShowRevertModal(false);
    },
  });

  const handleSaveFullText = async (text: string) => {
    setIsSaving(true);
    try {
      await updateTextMutation.mutateAsync(text);
    } finally {
      setIsSaving(false);
    }
  };

  const handleRevert = async () => {
    await revertMutation.mutateAsync();
  };

  const handleExport = async (format: "txt" | "json" | "srt" | "vtt") => {
    try {
      const blob = await api.exportTranscript(transcriptId!, format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `transcript_${transcriptId?.slice(0, 8)}_${Date.now()}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      console.error("Export failed:", err);
    }
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center justify-center h-64">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      </div>
    );
  }

  if (error || !transcript) {
    return (
      <div className="container mx-auto py-8 px-4">
        <div className="flex items-center gap-3 text-destructive">
          <FileText className="w-6 h-6" />
          <div>
            <h3 className="font-semibold text-lg mb-1">Transcript Not Found</h3>
            <p className="text-sm text-muted-foreground">
              The requested transcript could not be loaded.
            </p>
          </div>
        </div>
        <Button
          variant="outline"
          className="mt-4"
          onClick={() => navigate("/library")}
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Library
        </Button>
      </div>
    );
  }

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => navigate("/library")}
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <div>
            <h1 className="text-2xl font-bold">Transcript Editor</h1>
            {lastSaved && (
              <p className="text-sm text-muted-foreground">
                Last saved: {lastSaved.toLocaleTimeString()}
              </p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowHistoryModal(true)}
          >
            <History className="w-4 h-4 mr-2" />
            History
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowRevertModal(true)}
          >
            <RotateCcw className="w-4 h-4 mr-2" />
            Revert
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowExportModal(true)}
          >
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Header & Audio */}
        <div className="lg:col-span-1 space-y-6">
          <TranscriptHeaderCard
            language={transcript.language}
            engineVersion={transcript.engine_version}
            createdAt={transcript.created_at}
            updatedAt={transcript.updated_at}
          />
          <AudioPlayerCard
            jobId={transcript.job_id}
            audioDuration={null} // Would need to fetch from job
          />
        </div>

        {/* Right Column - Editor */}
        <div className="lg:col-span-2">
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
            <TabsList>
              <TabsTrigger value="full-text" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Full Text
              </TabsTrigger>
              <TabsTrigger value="segments" className="flex items-center gap-2">
                <List className="w-4 h-4" />
                Segments
              </TabsTrigger>
            </TabsList>

            <TabsContent value="full-text">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Full Text Editor</CardTitle>
                </CardHeader>
                <CardContent>
                  <FullTextEditor
                    initialText={transcript.text}
                    onSave={handleSaveFullText}
                    isSaving={isSaving}
                  />
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="segments">
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Segment Editor</CardTitle>
                </CardHeader>
                <CardContent>
                  <SegmentList
                    transcriptId={transcriptId!}
                    segments={transcript.segments}
                    onUpdate={() => {
                      queryClient.invalidateQueries({ queryKey: ["transcript", transcriptId] });
                    }}
                  />
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </div>
      </div>

      {/* Modals */}
      {showExportModal && (
        <ExportModal
          onClose={() => setShowExportModal(false)}
          onExport={handleExport}
        />
      )}
      {showRevertModal && (
        <RevertModal
          onClose={() => setShowRevertModal(false)}
          onConfirm={handleRevert}
          isLoading={revertMutation.isPending}
        />
      )}
      {showHistoryModal && (
        <EditHistoryModal
          transcriptId={transcriptId!}
          onClose={() => setShowHistoryModal(false)}
        />
      )}
    </div>
  );
}
