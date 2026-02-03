import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { Input } from "@poly/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@poly/ui/table";
import { Building2, Calendar, Search, Shield, Users } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";

type TeamItem = {
  id: string;
  name: string;
  plan: "FREE" | "STANDARD" | "PRO";
  owner_email?: string;
  member_count?: number;
  created_at: string;
};

type PlanFilter = "all" | "FREE" | "STANDARD" | "PRO";
type BadgeVariant = "default" | "secondary" | "destructive" | "outline";

export function TeamsPage() {
  const navigate = useNavigate();
  const [items, setItems] = useState<TeamItem[]>([]);
  const [query, setQuery] = useState("");
  const [planFilter, setPlanFilter] = useState<PlanFilter>("all");

  const refresh = useCallback(() => {
    const q = query.trim();
    const queryString = q ? `?q=${encodeURIComponent(q)}` : "";
    apiFetch<{ items: TeamItem[] }>(`/admin/teams${queryString}`).then((data) =>
      setItems(data.items),
    );
  }, [query]);

  useEffect(() => {
    const handle = setTimeout(() => {
      refresh();
    }, 300);
    return () => clearTimeout(handle);
  }, [refresh]);

  const filteredItems = items.filter((team) => {
    if (planFilter === "all") return true;
    return team.plan === planFilter;
  });

  const getPlanBadge = (plan: string) => {
    const colors: Record<string, { variant: BadgeVariant; label: string }> = {
      FREE: { variant: "secondary", label: "Free" },
      STANDARD: { variant: "default", label: "Standard" },
      PRO: { variant: "default", label: "Pro" },
    };
    const config = colors[plan] || { variant: "outline", label: plan };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Teams</h1>
        <p className="text-muted-foreground">Manage teams and their subscriptions.</p>
      </div>

      <Card className="border-border">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by team name or owner email"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              {(["all", "FREE", "STANDARD", "PRO"] as const).map((f) => (
                <Button
                  key={f}
                  variant={planFilter === f ? "default" : "outline"}
                  size="sm"
                  className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                  onClick={() => setPlanFilter(f)}
                >
                  {f === "all" ? "All Plans" : f}
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
              <TableHead>Team Name</TableHead>
              <TableHead>Plan</TableHead>
              <TableHead>Owner</TableHead>
              <TableHead>Members</TableHead>
              <TableHead>Created</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((team) => (
              <TableRow key={team.id}>
                <TableCell>
                  <Button
                    variant="link"
                    className="h-auto p-0 text-left"
                    onClick={() => navigate(`/teams/${team.id}`)}
                  >
                    <div className="flex items-center gap-2">
                      <Building2 className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{team.name}</span>
                    </div>
                  </Button>
                </TableCell>
                <TableCell>{getPlanBadge(team.plan)}</TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Users className="h-4 w-4 text-muted-foreground" />
                    <span>{team.owner_email || "-"}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Shield className="h-4 w-4 text-muted-foreground" />
                    <span>{team.member_count ?? "-"}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Calendar className="h-4 w-4 text-muted-foreground" />
                    <span>{new Date(team.created_at).toLocaleDateString()}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                      onClick={() => navigate(`/teams/${team.id}`)}
                    >
                      View
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {!filteredItems.length && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  No teams found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>
    </div>
  );
}
