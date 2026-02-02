import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { Button } from "@poly/ui/button";
import { Input } from "@poly/ui/input";
import { Card, CardContent } from "@poly/ui/card";
import { Search, Filter, Grid, List as ListIcon, Loader2 } from "lucide-react";

import { api } from "../../lib/api";
import { TranscriptCard } from "./components/cards/TranscriptCard";
import { AudioPreview } from "./components/cards/AudioPreview";
import { LanguageFilter } from "./components/filters/LanguageFilter";
import { SortFilter } from "./components/filters/SortFilter";
import { BulkExportModal } from "./components/modals/BulkExportModal";
import { DeleteConfirmModal } from "./components/modals/DeleteConfirmModal";

interface TranscriptListItem {
  id: string;
  job_id: string;
  job_filename: string | null;
  text_preview: string;
  language: string;
  created_at: string;
  updated_at: string | null;
}

export function LibraryPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [language, setLanguage] = useState<string | undefined>();
  const [sort, setSort] = useState("created_at:desc");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [showBulkExport, setShowBulkExport] = useState(false);
  const [deleteId, setDeleteId] = useState<string | null>(null);

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["transcripts", page, search, language],
    queryFn: () =>
      api.getTranscripts({
        page,
        page_size: 20,
        search: search || undefined,
        language: language || undefined,
        sort: sort,
      }),
  });

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedIds);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedIds(newSelected);
  };

  const toggleSelectAll = () => {
    if (data?.transcripts && selectedIds.size === data.transcripts.length) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(data!.transcripts.map((t) => t.id)));
    }
  };

  const handleDelete = async (id: string) => {
    // Would need to implement delete API
    console.log("Delete transcript:", id);
    setDeleteId(null);
    refetch();
  };

  return (
    <div className="container mx-auto py-8 px-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Transcript Library</h1>
          <p className="text-muted-foreground">
            Browse and manage all your transcripts
          </p>
        </div>
        {selectedIds.size > 0 && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-muted-foreground">
              {selectedIds.size} selected
            </span>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setShowBulkExport(true)}
            >
              Export Selected
            </Button>
          </div>
        )}
      </div>

      {/* Filters */}
      <div className="flex flex-wrap items-center gap-4 mb-6">
        <div className="relative flex-1 min-w-[200px] max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            placeholder="Search transcripts..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9"
          />
        </div>

        <LanguageFilter
          value={language}
          onChange={setLanguage}
        />

        <SortFilter value={sort} onChange={setSort} />

        <div className="flex items-center gap-1 border rounded-lg p-1">
          <button
            onClick={() => setViewMode("grid")}
            className={`p-2 rounded ${
              viewMode === "grid" ? "bg-muted" : "hover:bg-muted/50"
            }`}
          >
            <Grid className="w-4 h-4" />
          </button>
          <button
            onClick={() => setViewMode("list")}
            className={`p-2 rounded ${
              viewMode === "list" ? "bg-muted" : "hover:bg-muted/50"
            }`}
          >
            <ListIcon className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Content */}
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="w-8 h-8 animate-spin text-muted-foreground" />
        </div>
      ) : data?.transcripts.length === 0 ? (
        <Card>
          <CardContent className="py-16 text-center">
            <Filter className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No transcripts found</h3>
            <p className="text-muted-foreground mb-4">
              {search || language
                ? "Try adjusting your filters"
                : "Upload an audio file to get started"}
            </p>
            {!search && !language && (
              <Button onClick={() => navigate("/upload")}>
                Upload Audio
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <>
          {/* Select All */}
          <div className="flex items-center gap-2 mb-4">
            <input
              type="checkbox"
              checked={
                data?.transcripts.length !== 0 &&
                selectedIds.size === data?.transcripts.length
              }
              onChange={toggleSelectAll}
              className="rounded border-gray-300"
            />
            <span className="text-sm text-muted-foreground">
              Select all ({data?.total} total)
            </span>
          </div>

          {/* Grid/List View */}
          <div
            className={
              viewMode === "grid"
                ? "grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
                : "space-y-4"
            }
          >
            {data?.transcripts.map((transcript) => (
              <TranscriptCard
                key={transcript.id}
                transcript={transcript}
                viewMode={viewMode}
                isSelected={selectedIds.has(transcript.id)}
                onSelect={() => toggleSelect(transcript.id)}
                onView={() => navigate(`/transcripts/${transcript.id}`)}
                onExport={(format) =>
                  api.exportTranscript(transcript.id, format)
                }
                onDelete={() => setDeleteId(transcript.id)}
              />
            ))}
          </div>

          {/* Pagination */}
          {data && data.total > 20 && (
            <div className="flex items-center justify-center gap-2 mt-6">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
              >
                Previous
              </Button>
              <span className="text-sm text-muted-foreground">
                Page {page} of {Math.ceil(data.total / 20)}
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(data.total / 20)}
              >
                Next
              </Button>
            </div>
          )}
        </>
      )}

      {/* Modals */}
      {showBulkExport && (
        <BulkExportModal
          transcriptIds={Array.from(selectedIds)}
          onClose={() => setShowBulkExport(false)}
        />
      )}
      {deleteId && (
        <DeleteConfirmModal
          onClose={() => setDeleteId(null)}
          onConfirm={() => handleDelete(deleteId)}
        />
      )}
    </div>
  );
}
