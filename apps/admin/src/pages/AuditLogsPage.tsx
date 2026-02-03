import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { Input } from "@poly/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@poly/ui/table";
import type { LucideIcon } from "lucide-react";
import { Activity, Clock, Filter, Globe, Search, Shield, User } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

type AuditLogItem = {
  id: string;
  admin_email: string;
  action: string;
  resource_type?: string;
  resource_id?: string;
  details?: string;
  ip_address?: string;
  created_at: string;
};

type ActionFilter =
  | "all"
  | "create"
  | "update"
  | "delete"
  | "suspend"
  | "unsuspend"
  | "retry"
  | "cancel";

type ResourceFilter = "all" | "user" | "team" | "job" | "settings";
type BadgeVariant = "default" | "secondary" | "destructive" | "outline";

export function AuditLogsPage() {
  const [items, setItems] = useState<AuditLogItem[]>([]);
  const [query, setQuery] = useState("");
  const [actionFilter, setActionFilter] = useState<ActionFilter>("all");
  const [resourceFilter, setResourceFilter] = useState<ResourceFilter>("all");

  const refresh = useCallback(() => {
    const q = query.trim();
    const queryString = q ? `?q=${encodeURIComponent(q)}` : "";
    apiFetch<{ items: AuditLogItem[] }>(`/admin/audit-logs${queryString}`).then((data) =>
      setItems(data.items),
    );
  }, [query]);

  useEffect(() => {
    const handle = setTimeout(() => {
      refresh();
    }, 300);
    return () => clearTimeout(handle);
  }, [refresh]);

  const filteredItems = items.filter((item) => {
    const actionMatch = actionFilter === "all" || item.action.toLowerCase().includes(actionFilter);
    const resourceMatch =
      resourceFilter === "all" || item.resource_type?.toLowerCase() === resourceFilter;
    return actionMatch && resourceMatch;
  });

  const getActionBadge = (action: string) => {
    const colors: Record<string, { variant: BadgeVariant; icon: LucideIcon }> = {
      create: { variant: "default", icon: Activity },
      update: { variant: "secondary", icon: Shield },
      delete: { variant: "destructive", icon: Activity },
      suspend: { variant: "destructive", icon: Shield },
      unsuspend: { variant: "default", icon: Shield },
      retry: { variant: "secondary", icon: Activity },
      cancel: { variant: "outline", icon: Activity },
    };
    const actionLower = action.toLowerCase();
    let key: keyof typeof colors = "update";
    for (const [k, _v] of Object.entries(colors)) {
      if (actionLower.includes(k)) {
        key = k as keyof typeof colors;
        break;
      }
    }
    const config = colors[key] || { variant: "outline", icon: Activity };
    const Icon = config.icon;
    return (
      <Badge variant={config.variant} className="flex items-center gap-1">
        <Icon className="h-3 w-3" />
        {action}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Audit Logs</h1>
        <p className="text-muted-foreground">Track all admin actions and system changes.</p>
      </div>

      <Card className="border-border">
        <CardContent className="pt-6">
          <div className="flex flex-col gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by admin email or resource"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Filter className="h-4 w-4 text-muted-foreground mt-2" />
              {["all", "create", "update", "delete", "suspend", "unsuspend", "retry", "cancel"].map(
                (f) => (
                  <Button
                    key={f}
                    variant={actionFilter === f ? "default" : "outline"}
                    size="sm"
                    className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                    onClick={() => setActionFilter(f as ActionFilter)}
                  >
                    {f === "all" ? "All Actions" : f.charAt(0).toUpperCase() + f.slice(1)}
                  </Button>
                ),
              )}
              {(["all", "user", "team", "job", "settings"] as const).map((f) => (
                <Button
                  key={f}
                  variant={resourceFilter === f ? "default" : "outline"}
                  size="sm"
                  className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                  onClick={() => setResourceFilter(f)}
                >
                  {f === "all" ? "All Resources" : f.charAt(0).toUpperCase() + f.slice(1)}
                </Button>
              ))}
              <Button
                variant="outline"
                size="sm"
                className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                onClick={refresh}
              >
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Admin</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Resource Type</TableHead>
              <TableHead>Resource ID</TableHead>
              <TableHead>IP Address</TableHead>
              <TableHead>Details</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((log) => (
              <TableRow key={log.id}>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Clock className="h-4 w-4 text-muted-foreground" />
                    <span>{new Date(log.created_at).toLocaleString()}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span className="font-medium">{log.admin_email}</span>
                  </div>
                </TableCell>
                <TableCell>{getActionBadge(log.action)}</TableCell>
                <TableCell>
                  <Badge variant="outline">{log.resource_type || "-"}</Badge>
                </TableCell>
                <TableCell>
                  <span className="font-mono text-xs">{log.resource_id?.slice(0, 8) || "-"}</span>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    <span className="text-sm">{log.ip_address || "-"}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <span
                    className="text-sm text-muted-foreground max-w-[200px] truncate"
                    title={log.details}
                  >
                    {log.details || "-"}
                  </span>
                </TableCell>
              </TableRow>
            ))}
            {!filteredItems.length && (
              <TableRow>
                <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                  No audit logs found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
