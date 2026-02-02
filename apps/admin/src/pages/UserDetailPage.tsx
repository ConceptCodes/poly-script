import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { apiFetch } from "../lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Button } from "@poly/ui/button";
import { Badge } from "@poly/ui/badge";
import { ArrowLeft, Mail, User, Calendar, Shield, CheckCircle, XCircle, AlertCircle, Building2 } from "lucide-react";

type UserDetail = {
  id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_suspended: boolean;
  created_at: string;
  last_login_at?: string | null;
  teams?: Array<{ id: string; name: string; role: string }>;
};

export function UserDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [user, setUser] = useState<UserDetail | null>(null);

  useEffect(() => {
    if (id) {
      apiFetch<UserDetail>(`/admin/users/${id}`).then(setUser);
    }
  }, [id]);

  if (!user) {
    return <div className="p-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate("/users")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">User Details</h1>
          <p className="text-muted-foreground">Manage user account and permissions.</p>
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="h-5 w-5" />
              Account Information
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-start gap-3">
              <Mail className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Email</div>
                <div className="font-medium">{user.email}</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <User className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Full Name</div>
                <div className="font-medium">{user.full_name || "-"}</div>
              </div>
            </div>
            <div className="flex items-start gap-3">
              <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div className="flex-1">
                <div className="text-sm text-muted-foreground">Created At</div>
                <div className="font-medium">{new Date(user.created_at).toLocaleString()}</div>
              </div>
            </div>
            {user.last_login_at && (
              <div className="flex items-start gap-3">
                <Calendar className="h-5 w-5 text-muted-foreground mt-0.5" />
                <div className="flex-1">
                  <div className="text-sm text-muted-foreground">Last Login</div>
                  <div className="font-medium">{new Date(user.last_login_at).toLocaleString()}</div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Status & Security
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">Account Status</div>
              <Badge variant={user.is_active ? "default" : "secondary"}>
                {user.is_active ? "Active" : "Inactive"}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">Email Verified</div>
              <Badge variant={user.is_verified ? "default" : "outline"}>
                {user.is_verified ? (
                  <>
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Verified
                  </>
                ) : (
                  <>
                    <XCircle className="h-3 w-3 mr-1" />
                    Not Verified
                  </>
                )}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div className="text-sm text-muted-foreground">Suspended</div>
              <Badge variant={user.is_suspended ? "destructive" : "outline"}>
                {user.is_suspended ? (
                  <>
                    <AlertCircle className="h-3 w-3 mr-1" />
                    Suspended
                  </>
                ) : (
                  "No"
                )}
              </Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {user.teams && user.teams.length > 0 && (
        <Card className="border-border">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Building2 className="h-5 w-5" />
              Team Memberships
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {user.teams.map((team) => (
                <div
                  key={team.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border"
                >
                  <div>
                    <div className="font-medium">{team.name}</div>
                    <div className="text-sm text-muted-foreground">ID: {team.id}</div>
                  </div>
                  <Badge variant="outline">{team.role}</Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
