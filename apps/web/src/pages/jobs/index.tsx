import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Input } from "@poly/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@poly/ui/table";
import { useQuery } from "@tanstack/react-query";
import { AlertCircle, ArrowUpDown, ChevronLeft, ChevronRight, RefreshCw } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../lib/api";

const STATUS_OPTIONS = [
  { value: "all", label: "All Status" },
  { value: "QUEUED", label: "Queued" },
  { value: "RUNNING", label: "Running" },
  { value: "SUCCEEDED", label: "Succeeded" },
  { value: "FAILED", label: "Failed" },
  { value: "CANCELED", label: "Canceled" },
];

const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

export function JobsPage() {
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [sortField, setSortField] = useState("created_at");
  const [sortOrder, setSortOrder] = useState<"asc" | "desc">("desc");

  const {
    data: jobsData,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ["jobs", page, pageSize, statusFilter, searchQuery, sortField, sortOrder],
    queryFn: () =>
      api.getJobs({
        page,
        page_size: pageSize,
        status: statusFilter === "all" ? undefined : statusFilter,
        search: searchQuery || undefined,
        sort_field: sortField,
        sort_order: sortOrder,
      }),
  });

  const handleSort = (field: string) => {
    if (sortField === field) {
      setSortOrder(sortOrder === "asc" ? "desc" : "asc");
    } else {
      setSortField(field);
      setSortOrder("desc");
    }
  };

  const totalPages = jobsData ? Math.ceil(jobsData.total / pageSize) : 0;

  const getStatusBadge = (status: string) => {
    const colors: Record<string, string> = {
      QUEUED: "bg-yellow-100 text-yellow-800",
      RUNNING: "bg-blue-100 text-blue-800",
      SUCCEEDED: "bg-green-100 text-green-800",
      FAILED: "bg-red-100 text-red-800",
      CANCELED: "bg-gray-100 text-gray-800",
    };
    const color = colors[status] || "bg-gray-100 text-gray-800";
    return <span className={`px-2 py-1 rounded-full text-xs font-medium ${color}`}>{status}</span>;
  };

  if (isLoading) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card>
          <CardHeader>
            <CardTitle>Jobs</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center py-12">Loading jobs...</div>
          </CardContent>
        </Card>
      </div>
    );
  }

  if (error) {
    return (
      <div className="container mx-auto py-8 px-4">
        <Card className="border-destructive">
          <CardContent className="p-6">
            <div className="flex items-center gap-3 text-destructive">
              <AlertCircle className="w-6 h-6" />
              <div>
                <h3 className="font-semibold text-lg mb-1">Error Loading Jobs</h3>
                <p className="text-sm text-muted-foreground">
                  {error instanceof Error ? error.message : "An unknown error occurred"}
                </p>
              </div>
            </div>
            <Button
              variant="outline"
              className="flex items-center gap-2 mt-4"
              onClick={() => refetch()}
            >
              <RefreshCw className="w-4 h-4" />
              Retry
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  const jobs = jobsData?.jobs || [];

  return (
    <div className="container mx-auto py-8 px-4">
      <Card>
        <CardHeader className="flex items-center justify-between">
          <CardTitle>Jobs ({jobsData?.total || 0})</CardTitle>
          <Button
            variant="ghost"
            size="sm"
            className="flex items-center gap-2"
            onClick={() => refetch()}
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </Button>
        </CardHeader>
        <CardContent>
          {/* Filters */}
          <div className="flex flex-col sm:flex-row gap-4 mb-6">
            <div className="flex-1">
              <Input
                placeholder="Search by filename..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {STATUS_OPTIONS.map((option) => (
                  <SelectItem key={option.value} value={option.value}>
                    {option.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={String(pageSize)} onValueChange={(v) => setPageSize(Number(v))}>
              <SelectTrigger className="w-[120px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {PAGE_SIZE_OPTIONS.map((size) => (
                  <SelectItem key={size} value={String(size)}>
                    {size} / page
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          {/* Table */}
          {jobs.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-muted-foreground mb-4">No jobs found</p>
              <Button onClick={() => navigate("/upload")}>Upload Audio</Button>
            </div>
          ) : (
            <>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort("created_at")}
                      >
                        <div className="flex items-center gap-1">
                          Created
                          {sortField === "created_at" && <ArrowUpDown className="w-4 h-4" />}
                        </div>
                      </TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Filename</TableHead>
                      <TableHead>Language</TableHead>
                      <TableHead>Engine</TableHead>
                      <TableHead>Progress</TableHead>
                      <TableHead
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort("started_at")}
                      >
                        <div className="flex items-center gap-1">
                          Started
                          {sortField === "started_at" && <ArrowUpDown className="w-4 h-4" />}
                        </div>
                      </TableHead>
                      <TableHead
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => handleSort("finished_at")}
                      >
                        <div className="flex items-center gap-1">
                          Finished
                          {sortField === "finished_at" && <ArrowUpDown className="w-4 h-4" />}
                        </div>
                      </TableHead>
                      <TableHead>Stage</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {jobs.map((job) => (
                      <TableRow
                        key={job.id}
                        className="cursor-pointer hover:bg-muted"
                        onClick={() => navigate(`/jobs/${job.id}/live`)}
                      >
                        <TableCell className="text-xs">
                          {new Date(job.created_at).toLocaleString()}
                        </TableCell>
                        <TableCell>{getStatusBadge(job.status)}</TableCell>
                        <TableCell className="font-medium">{job.filename}</TableCell>
                        <TableCell className="text-sm">{job.language || "-"}</TableCell>
                        <TableCell className="text-sm">-</TableCell>
                        <TableCell className="text-sm">
                          {job.status === "RUNNING" || job.status === "QUEUED" ? (
                            <div className="flex items-center gap-2">
                              <div className="w-16 h-2 bg-gray-200 rounded-full overflow-hidden">
                                <div
                                  className="h-full bg-blue-500 transition-all"
                                  style={{ width: `${job.progress_pct}%` }}
                                />
                              </div>
                              <span className="text-xs">{job.progress_pct}%</span>
                            </div>
                          ) : (
                            <span className="text-muted-foreground">
                              {job.status === "SUCCEEDED" ? "100%" : "-"}
                            </span>
                          )}
                        </TableCell>
                        <TableCell className="text-xs">
                          {job.started_at ? new Date(job.started_at).toLocaleString() : "-"}
                        </TableCell>
                        <TableCell className="text-xs">
                          {job.finished_at ? new Date(job.finished_at).toLocaleString() : "-"}
                        </TableCell>
                        <TableCell className="text-xs">{job.progress_stage || "-"}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex items-center justify-between mt-6">
                  <p className="text-sm text-muted-foreground">
                    Showing {(page - 1) * pageSize + 1} to{" "}
                    {Math.min(page * pageSize, jobsData?.total || 0)} of {jobsData?.total || 0} jobs
                  </p>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.max(1, p - 1))}
                      disabled={page === 1}
                    >
                      <ChevronLeft className="w-4 h-4" />
                      Previous
                    </Button>
                    <span className="text-sm px-2">
                      Page {page} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                      disabled={page === totalPages}
                    >
                      Next
                      <ChevronRight className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
