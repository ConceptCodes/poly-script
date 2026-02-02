import { useState, useEffect } from "react";
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@poly/ui";
import { Alert, AlertDescription } from "@poly/ui";
import { Badge } from "@poly/ui";
import { useAppStore } from "../../lib/store";
import { apiFetch } from "../../lib/api";
import { Trash2 } from "lucide-react";

function Dialog({
  open,
  onOpenChange,
  children,
}: {
  open: boolean;
  onOpenChange: (v: boolean) => void;
  children: React.ReactNode;
}) {
  if (!open) return null;
  return (
    <div
      className="fixed inset-0 z-50"
      role="dialog"
      aria-label="Dialog"
      onClick={() => onOpenChange(false)}
    >
      <div
        className="fixed inset-0 bg-black/50"
        onClick={(e) => e.stopPropagation()}
      />
      <div className="flex items-center justify-center h-full">
        <div
          className="relative bg-white rounded-lg shadow-lg p-6 w-full max-w-md"
          onClick={(e) => e.stopPropagation()}
        >
          {children}
        </div>
      </div>
    </div>
  );
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

type Invitation = {
  id: string;
  email: string;
  role: string;
  created_at: string;
};

export function TeamSettingsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);
  const [inviteEmail, setInviteEmail] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [inviteModalOpen, setInviteModalOpen] = useState(false);
  const [inviteRole, setInviteRole] = useState("MEMBER");
  const [pendingInvitations, setPendingInvitations] = useState<Invitation[]>(
    [],
  );

  const { auth } = useAppStore();
  const { user, team } = auth;

  const form = useForm({
    defaultValues: {
      teamName: team?.name ?? "",
      defaultLanguage: team?.defaultLanguage ?? "en",
    },
  });

  const currentMembership = team?.members?.find((m) => m.id === user?.id);
  const isAdmin = currentMembership?.role === "ADMIN";

  useEffect(() => {
    if (isAdmin && team?.id) {
      loadPendingInvitations();
    }
  }, [isAdmin, team?.id]);

  const loadPendingInvitations = async () => {
    try {
      const data = (await apiFetch(`/v1/teams/${team!.id}/invitations`)) as {
        invitations: Invitation[];
      };
      setPendingInvitations(data.invitations || []);
    } catch (error) {
      console.error("Failed to load invitations:", error);
    }
  };

  const handleUpdateTeam = async () => {
    if (!isAdmin) return;
    setIsLoading(true);
    setSuccessMessage("");
    const value = form.state.values as {
      teamName: string;
      defaultLanguage: string;
    };
    try {
      await apiFetch(`/v1/teams/${team!.id}`, {
        method: "PATCH",
        body: { name: value.teamName, default_language: value.defaultLanguage },
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
      await apiFetch(`/v1/teams/${team!.id}/invitations`, {
        method: "POST",
        body: { email: inviteEmail, role: inviteRole },
      });
      setInviteEmail("");
      setInviteRole("MEMBER");
      setInviteModalOpen(false);
      setSuccessMessage(t("teamSettings.inviteSuccess"));
      await loadPendingInvitations();
    } catch (error: any) {
      console.error("Failed to invite member:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangeMemberRole = async (memberId: string, newRole: string) => {
    if (!isAdmin) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team!.id}/members/${memberId}`, {
        method: "PATCH",
        body: { role: newRole },
      });
      setSuccessMessage(t("teamSettings.success"));
    } catch (error: any) {
      console.error("Failed to update member role:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!isAdmin) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team!.id}/members/${memberId}`, {
        method: "DELETE",
      });
      setSuccessMessage(t("teamSettings.removeSuccess"));
    } catch (error: any) {
      console.error("Failed to remove member:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelInvitation = async (invitationId: string) => {
    if (!isAdmin) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team!.id}/invitations/${invitationId}`, {
        method: "DELETE",
      });
      setSuccessMessage(t("teamSettings.inviteSuccess"));
      await loadPendingInvitations();
    } catch (error: any) {
      console.error("Failed to cancel invitation:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTeam = async () => {
    if (!isAdmin) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team!.id}`, {
        method: "DELETE",
      });
      navigate("/dashboard");
    } catch (error: any) {
      console.error("Failed to delete team:", error);
    } finally {
      setIsLoading(false);
      setDeleteDialogOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">{t("teamSettings.title")}</h1>

        {successMessage && (
          <Alert variant="default" className="mb-6">
            <AlertDescription>{successMessage}</AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle>{t("teamSettings.teamInfo")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <form.Field name="teamName">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>
                    {t("teamSettings.teamNameLabel")}
                  </Label>
                  <Input
                    id={field.name}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                    disabled={!isAdmin || isLoading}
                  />
                </div>
              )}
            </form.Field>

            <form.Field name="defaultLanguage">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>
                    {t("teamSettings.defaultLanguageLabel")}
                  </Label>
                  <Select
                    value={field.state.value}
                    onValueChange={field.handleChange}
                    disabled={!isAdmin || isLoading}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue
                        placeholder={t(
                          "teamSettings.defaultLanguagePlaceholder",
                        )}
                      />
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
            <CardTitle>{t("teamSettings.members")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">
                {t("teamSettings.members.title")}
              </h3>
              {isAdmin && (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => setInviteModalOpen(true)}
                >
                  {t("teamSettings.members.invite")}
                </Button>
              )}
            </div>

            <div className="space-y-4">
              {team.members?.map((member) => (
                <div
                  key={member.id}
                  className="flex items-center justify-between py-3 border-b"
                >
                  <div className="flex items-center space-x-3">
                    <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
                      {member.email[0].toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium">{member.email}</p>
                      <Badge
                        variant={
                          member.role === "ADMIN" ? "default" : "secondary"
                        }
                      >
                        {member.role}
                      </Badge>
                    </div>
                  </div>
                  {isAdmin && (
                    <div className="flex items-center space-x-2">
                      <Select
                        defaultValue={member.role}
                        onValueChange={(value) =>
                          handleChangeMemberRole(member.id, value)
                        }
                        disabled={isLoading}
                      >
                        <SelectTrigger className="w-[120px]">
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="ADMIN">
                            {t("teamSettings.roles.admin")}
                          </SelectItem>
                          <SelectItem value="MEMBER">
                            {t("teamSettings.roles.member")}
                          </SelectItem>
                          <SelectItem value="VIEWER">
                            {t("teamSettings.roles.viewer")}
                          </SelectItem>
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

        {isAdmin && pendingInvitations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{t("teamSettings.invitations")}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {pendingInvitations.map((invitation) => (
                <div
                  key={invitation.id}
                  className="flex items-center justify-between py-3 border-b"
                >
                  <div>
                    <p className="font-medium">{invitation.email}</p>
                    <Badge variant="outline">{invitation.role}</Badge>
                    <p className="text-xs text-muted-foreground">
                      {new Date(invitation.created_at).toLocaleDateString()}
                    </p>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    onClick={() => handleCancelInvitation(invitation.id)}
                    disabled={isLoading}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {isAdmin && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">
                {t("teamSettings.dangerZone.title")}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Button
                variant="destructive"
                onClick={() => setDeleteDialogOpen(true)}
              >
                {t("teamSettings.dangerZone.deleteTeam")}
              </Button>
              <p className="text-sm text-muted-foreground">
                {t("teamSettings.dangerZone.warning")}
              </p>
            </CardContent>
          </Card>
        )}

        <Dialog open={inviteModalOpen} onOpenChange={setInviteModalOpen}>
          <div className="space-y-4">
            <div>
              <DialogTitle>{t("teamSettings.members.invite")}</DialogTitle>
              <DialogDescription>
                {t("teamSettings.inviteModal.description")}
              </DialogDescription>
            </div>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="email">
                  {t("teamSettings.inviteModal.emailLabel")}
                </Label>
                <Input
                  id="email"
                  placeholder={t("teamSettings.inviteModal.emailPlaceholder")}
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">
                  {t("teamSettings.inviteModal.roleLabel")}
                </Label>
                <Select value={inviteRole} onValueChange={setInviteRole}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ADMIN">
                      {t("teamSettings.roles.admin")}
                    </SelectItem>
                    <SelectItem value="MEMBER">
                      {t("teamSettings.roles.member")}
                    </SelectItem>
                    <SelectItem value="VIEWER">
                      {t("teamSettings.roles.viewer")}
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setInviteModalOpen(false)}
              >
                {t("common.cancel")}
              </Button>
              <Button
                onClick={handleInviteMember}
                disabled={isLoading || !inviteEmail}
              >
                {isLoading ? t("common.sending") : t("common.send")}
              </Button>
            </DialogFooter>
          </div>
        </Dialog>

        <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <div className="space-y-4">
            <div>
              <h3 className="text-lg font-semibold">
                {t("teamSettings.dangerZone.confirmDelete")}
              </h3>
              <p className="text-sm text-muted-foreground">
                {t("teamSettings.dangerZone.confirmMessage")}
              </p>
            </div>
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                onClick={() => setDeleteDialogOpen(false)}
              >
                {t("common.cancel")}
              </Button>
              <Button
                variant="destructive"
                onClick={handleDeleteTeam}
                disabled={isLoading}
              >
                {isLoading ? t("common.deleting") : t("common.delete")}
              </Button>
            </div>
          </div>
        </Dialog>
      </div>
    </div>
  );
}
