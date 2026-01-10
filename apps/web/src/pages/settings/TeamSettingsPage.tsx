import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useForm } from "@tanstack/react-form";
import { Button } from "@poly/ui";
import { Input } from "@poly/ui";
import { Label } from "@poly/ui";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@poly/ui";
import { Switch } from "@poly/ui";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui";
import { Alert, AlertDescription } from "@poly/ui";
import { Badge } from "@poly/ui";
import { useAppStore } from "../../lib/store";
import { apiFetch } from "../../lib/api";
import { Trash2 } from "lucide-react";

// Simple Dialog components for now since AlertDialog doesn't exist
function DialogContent({ children }: { children: React.ReactNode }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="fixed inset-0 bg-black/50" />
      <div className="relative z-50 bg-white rounded-lg p-6 max-w-md w-full shadow-lg">
        {children}
      </div>
    </div>
  );
}

function DialogHeader({ children }: { children: React.ReactNode }) {
  return <div className="mb-4">{children}</div>;
}

function DialogTitle({ children }: { children: React.ReactNode }) {
  return <h2 className="text-lg font-semibold">{children}</h2>;
}

function DialogDescription({ children }: { children: React.ReactNode }) {
  return <p className="text-sm text-muted-foreground">{children}</p>;
}

function DialogFooter({ children }: { children: React.ReactNode }) {
  return <div className="flex justify-end gap-2 mt-4">{children}</div>;
}

export function TeamSettingsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { auth } = useAppStore();
  const { user, team } = auth;

  const [form] = useForm({
    defaultValues: {
      teamName: team?.defaultLanguage || "",
      defaultLanguage: team?.defaultLanguage || "en",
    },
  });

  const isAdmin = user?.role === "ADMIN";

  const handleUpdateTeam = async ({ value }) => {
    if (!isAdmin) return;
    setIsLoading(true);
    setSuccessMessage("");

    try {
      await apiFetch(`/v1/teams/${team.id}`, {
        method: "PATCH",
        body: {
          name: value.teamName,
          default_language: value.defaultLanguage,
        },
      });

      setSuccessMessage(t("teamSettings.success"));
    } catch (error: any) {
      console.error("Failed to update team:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInviteMember = async () => {
    if (!isAdmin || !inviteEmail) return;
    setIsLoading(true);

    try {
      await apiFetch(`/v1/teams/${team.id}/invitations`, {
        method: "POST",
        body: {
          email: inviteEmail,
          role: "MEMBER",
        },
      });

      setInviteEmail("");
      setSuccessMessage(t("teamSettings.inviteSuccess"));
    } catch (error: any) {
      console.error("Failed to invite member:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!isAdmin) return;
    setIsLoading(true);

    try {
      await apiFetch(`/v1/teams/${team.id}/members/${memberId}`, {
        method: "DELETE",
      });
      setSuccessMessage(t("teamSettings.removeSuccess"));
    } catch (error: any) {
      console.error("Failed to remove member:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangeMemberRole = async (memberId: string, role: string) => {
    if (!isAdmin) return;
    setIsLoading(true);

    try {
      await apiFetch(`/v1/teams/${team.id}/members/${memberId}`, {
        method: "PATCH",
        body: { role },
      });
      setSuccessMessage(t("teamSettings.roleUpdateSuccess"));
    } catch (error: any) {
      console.error("Failed to update member role:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTeam = async () => {
    setIsLoading(true);

    try {
      await apiFetch(`/v1/teams/${team.id}`, {
        method: "DELETE",
      });
      setDeleteDialogOpen(false);
      navigate("/dashboard");
    } catch (error: any) {
      console.error("Failed to delete team:", error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!team) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center py-8">
        <p>{t("teamSettings.notFound")}</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">{t("teamSettings.title")}</h1>

        {successMessage && (
          <Alert variant="default" className="mb-6">
            {successMessage}
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle>{t("teamSettings.teamInfo")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <form.Field name="teamName">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("teamSettings.teamName.label")}</Label>
                  <Input
                    id={field.name}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    disabled={!isAdmin}
                  />
                  {field.state.meta.errors && (
                    <p className="text-sm text-red-500">{field.state.meta.errors[0]}</p>
                  )}
                </div>
              )}
            </form.Field>

            <form.Field name="defaultLanguage">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("teamSettings.defaultLanguage.label")}</Label>
                  <Select value={field.state.value} onValueChange={field.handleChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={t("teamSettings.defaultLanguage.placeholder")} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="en">English</SelectItem>
                      <SelectItem value="de">Deutsch</SelectItem>
                      <SelectItem value="es">Español</SelectItem>
                      <SelectItem value="fr">Français</SelectItem>
                      <SelectItem value="jp">日本語</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              )}
            </form.Field>

            <Button onClick={handleUpdateTeam} disabled={isLoading || !isAdmin}>
              {isLoading ? t("common.saving") : t("teamSettings.save")}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("teamSettings.members.title")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">{t("teamSettings.members.invite")}</h3>
              {isAdmin && (
                <Button variant="outline" size="sm" onClick={() => setInviteEmail("")}>
                  {t("teamSettings.members.invite")}
                </Button>
              )}
            </div>

            {isAdmin && inviteEmail && (
              <div className="flex gap-2 mb-4">
                <Input
                  placeholder={t("teamSettings.members.emailPlaceholder")}
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleInviteMember()}
                />
                <Button onClick={handleInviteMember} disabled={isLoading}>
                  {t("common.send")}
                </Button>
              </div>
            )}

            <div className="space-y-4">
              {team.members?.map((member) => (
                <div key={member.id} className="flex items-center justify-between py-3 border-b">
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
                      {member.email[0].toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium">{member.email}</p>
                      <Badge variant={member.role === "ADMIN" ? "default" : "secondary"}>
                        {member.role}
                      </Badge>
                    </div>
                  </div>
                  {isAdmin && (
                    <div className="flex items-center space-x-2">
                      <Select
                        defaultValue={member.role}
                        onValueChange={(value) => handleChangeMemberRole(member.id, value)}
                        disabled={isLoading}
                      >
                        <SelectTrigger className="w-[120px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ADMIN">{t("teamSettings.roles.admin")}</SelectItem>
                          <SelectItem value="MEMBER">{t("teamSettings.roles.member")}</SelectItem>
                          <SelectItem value="VIEWER">{t("teamSettings.roles.viewer")}</SelectItem>
                        </SelectContent>
                      </Select>
                      <Button
                        variant="ghost"
                        size="icon"
                        onClick={() => handleRemoveMember(member.id)}
                        disabled={isLoading}
                      >
                        <Trash2 className="h-4 w-4" />
                      </Button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {isAdmin && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">
                {t("teamSettings.dangerZone.title")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button variant="destructive" onClick={() => setDeleteDialogOpen(true)}>
                {t("teamSettings.dangerZone.deleteTeam")}
              </Button>
              <p className="text-sm text-muted-foreground">
                {t("teamSettings.dangerZone.warning")}
              </p>
            </CardContent>
          </Card>
        )}

        <AlertDialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>{t("teamSettings.dangerZone.confirmDelete")}</AlertDialogTitle>
              <AlertDialogDescription>{t("teamSettings.dangerZone.confirmMessage")}</AlertDialogDescription>
            </AlertDialogHeader>
            <AlertDialogFooter>
              <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                {t("common.cancel")}
              </Button>
              <Button variant="destructive" onClick={handleDeleteTeam} disabled={isLoading}>
                {isLoading ? t("common.deleting") : t("common.delete")}
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>
      </div>
    </div>
  );
}
