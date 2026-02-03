import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import type { LucideIcon } from "lucide-react";
import {
  ArrowLeft,
  Building2,
  Calendar,
  Clock,
  CreditCard,
  Crown,
  Eye,
  Shield,
  Users,
} from "lucide-react";
import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { apiFetch } from "../lib/api";

type TeamDetail = {
  id: string;
  name: string;
  plan: "FREE" | "STANDARD" | "PRO";
  owner_id: string;
  owner_email?: string;
  created_at: string;
  members?: Array<{ id: string; email: string; role: string; full_name?: string }>;
  usage?: {
    jobs_used: number;
    jobs_limit: number;
    members_used: number;
    members_limit: number;
    reset_date: string;
  };
};

type BadgeVariant = "default" | "secondary" | "destructive" | "outline";

export function TeamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [team, setTeam] = useState<TeamDetail | null>(null);

  useEffect(() => {
    if (id) {
      apiFetch<TeamDetail>(`/admin/teams/${id}`).then(setTeam);
    }
  }, [id]);

  if (!team) {
    return <div className="p-8">Loading…</div>;
  }

  const getPlanBadge = (plan: string) => {
    const colors: Record<string, { variant: BadgeVariant; label: string }> = {
      FREE: { variant: "secondary", label: "Free" },
      STANDARD: { variant: "default", label: "Standard" },
      PRO: { variant: "default", label: "Pro" },
    };
    const config = colors[plan] || { variant: "outline", label: plan };
    return <Badge variant={config.variant}>{config.label}</Badge>;
  };

  const getRoleBadge = (role: string) => {
    const icons: Record<string, LucideIcon> = {
      ADMIN: Crown,
      MEMBER: Shield,
      VIEWER: Eye,
    };
    const Icon = icons[role] || Users;
    return (
      <Badge variant="outline" className="flex items-center gap-1">
        <Icon className="h-3 w-3" aria-hidden="true" />
        {role}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate("/teams")}
          aria-label="Back to teams"
        >
          <ArrowLeft className="h-5 w-5" aria-hidden="true" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">Team Details</h1>
          <p className="text-muted-foreground">Manage team and team members.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Team Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Building2 className="h-5 w-5 text-muted-foreground mt-0.5" aria-hidden="true" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Team Name</div>
                <div className="font-medium">{team.name}</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <CreditCard className="h-5 w-5 text-muted-foreground mt-0.5" aria-hidden="true" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Plan</div>
                {getPlanBadge(team.plan)}
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Users className="h-5 w-5 text-muted-foreground mt-0.5" aria-hidden="true" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Owner Email</div>
                <div className="font-medium">{team.owner_email || "-"}</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" aria-hidden="true" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Created At</div>
                <div className="font-medium">{new Date(team.created_at).toLocaleString()}</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {team.usage && (
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" aria-hidden="true" />
                Usage & Limits
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Jobs Used</span>
                  <span className="text-sm font-medium">
                    {team.usage.jobs_used} / {team.usage.jobs_limit}
                  </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{
                      width: `${Math.min((team.usage.jobs_used / team.usage.jobs_limit) * 100, 100)}%`,
                    }}
                  />
                </div>
              </div>
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm text-muted-foreground">Members Used</span>
                  <span className="text-sm font-medium">
                    {team.usage.members_used} / {team.usage.members_limit}
                  </span>
                </div>
                <div className="h-2 bg-muted rounded-full overflow-hidden">
                  <div
                    className="h-full bg-primary rounded-full"
                    style={{
                      width: `${Math.min((team.usage.members_used / team.usage.members_limit) * 100, 100)}%`,
                    }}
                  />
                </div>
              </div>
              <div className="pt-2 border-t border-border">
                <span className="text-sm text-muted-foreground">Reset Date: </span>
                <span className="text-sm font-medium">
                  {new Date(team.usage.reset_date).toLocaleDateString()}
                </span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {team.members && team.members.length > 0 && (
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="h-5 w-5" />
              Team Members
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {team.members.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border"
                >
                  <div className="flex-1">
                    <div className="font-medium">{member.full_name || member.email}</div>
                    <div className="text-sm text-muted-foreground">{member.email}</div>
                  </div>
                  {getRoleBadge(member.role)}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
