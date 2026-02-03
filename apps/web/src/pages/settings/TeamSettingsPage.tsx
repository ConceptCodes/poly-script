import {
  Alert,
  AlertDescription,
  Badge,
  Button,
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Input,
  Label,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@poly/ui";
import { useForm } from "@tanstack/react-form";
import { Trash2 } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { apiFetch } from "../../lib/api";
import { useAppStore } from "../../lib/store";

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
  const [pendingInvitations, setPendingInvitations] = useState<Invitation[]>([]);

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

  const loadPendingInvitations = useCallback(async () => {
    if (!team?.id) return;
    try {
      const data = (await apiFetch(`/v1/teams/${team.id}/invitations`)) as {
        invitations: Invitation[];
      };
      setPendingInvitations(data.invitations || []);
    } catch (error) {
      console.error("Failed to load invitations:", error);
    }
  }, [team?.id]);

  useEffect(() => {
    if (isAdmin && team?.id) {
      loadPendingInvitations();
    }
  }, [isAdmin, team?.id, loadPendingInvitations]);

  const handleUpdateTeam = async () => {
    if (!isAdmin || !team?.id) return;
    setIsLoading(true);
    setSuccessMessage("");
    const value = form.state.values as {
      teamName: string;
      defaultLanguage: string;
    };
    try {
      await apiFetch(`/v1/teams/${team.id}`, {
        method: "PATCH",
        body: { name: value.teamName, default_language: value.defaultLanguage },
      });
      setSuccessMessage(t("teamSettings.success"));
    } catch (error: unknown) {
      console.error("Failed to update team:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleInviteMember = async () => {
    if (!isAdmin || !inviteEmail || !team?.id) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team.id}/invitations`, {
        method: "POST",
        body: { email: inviteEmail, role: inviteRole },
      });
      setInviteEmail("");
      setInviteRole("MEMBER");
      setInviteModalOpen(false);
      setSuccessMessage(t("teamSettings.inviteSuccess"));
      await loadPendingInvitations();
    } catch (error: unknown) {
      console.error("Failed to invite member:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChangeMemberRole = async (memberId: string, newRole: string) => {
    if (!isAdmin || !team?.id) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team.id}/members/${memberId}`, {
        method: "PATCH",
        body: { role: newRole },
      });
      setSuccessMessage(t("teamSettings.success"));
    } catch (error: unknown) {
      console.error("Failed to update member role:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRemoveMember = async (memberId: string) => {
    if (!isAdmin || !team?.id) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team.id}/members/${memberId}`, {
        method: "DELETE",
      });
      setSuccessMessage(t("teamSettings.removeSuccess"));
    } catch (error: unknown) {
      console.error("Failed to remove member:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancelInvitation = async (invitationId: string) => {
    if (!isAdmin || !team?.id) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team.id}/invitations/${invitationId}`, {
        method: "DELETE",
      });
      setSuccessMessage(t("teamSettings.inviteSuccess"));
      await loadPendingInvitations();
    } catch (error: unknown) {
      console.error("Failed to cancel invitation:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteTeam = async () => {
    if (!isAdmin || !team?.id) return;
    setIsLoading(true);
    try {
      await apiFetch(`/v1/teams/${team.id}`, {
        method: "DELETE",
      });
      navigate("/dashboard");
    } catch (error: unknown) {
      console.error("Failed to delete team:", error);
    } finally {
      setIsLoading(false);
      setDeleteDialogOpen(false);
    }
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container max-w-4xl mx-auto space-y-8">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold">{t("teamSettings.title")}</h1>
        </div>

        {successMessage && (
          <Alert variant="default">
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
                  <Label htmlFor={field.name}>{t("teamSettings.teamNameLabel")}</Label>
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
                  <Label htmlFor={field.name}>{t("teamSettings.defaultLanguageLabel")}</Label>
                  <Select
                    value={field.state.value}
                    onValueChange={field.handleChange}
                    disabled={!isAdmin || isLoading}
                  >
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={t("teamSettings.defaultLanguagePlaceholder")} />
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

            {isAdmin && (
              <div className="flex justify-end">
                <Button onClick={handleUpdateTeam} disabled={isLoading}>
                  {isLoading ? t("common.saving") : t("teamSettings.save")}
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle>{t("teamSettings.members")}</CardTitle>
            {isAdmin && (
              <Button size="sm" onClick={() => setInviteModalOpen(true)}>
                {t("teamSettings.members.invite")}
              </Button>
            )}
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>User</TableHead>
                  <TableHead>Role</TableHead>
                  {isAdmin && <TableHead className="text-right">Actions</TableHead>}
                </TableRow>
              </TableHeader>
              <TableBody>
                {team?.members?.map((member) => (
                  <TableRow key={member.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-sm font-medium">
                          {member.email[0].toUpperCase()}
                        </div>
                        <span className="font-medium">{member.email}</span>
                      </div>
                    </TableCell>
                    <TableCell>
                      {isAdmin && member.id !== user?.id ? (
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
                      ) : (
                        <Badge variant={member.role === "ADMIN" ? "default" : "secondary"}>
                          {member.role}
                        </Badge>
                      )}
                    </TableCell>
                    {isAdmin && (
                      <TableCell className="text-right">
                        {member.id !== user?.id && (
                          <Button
                            variant="ghost"
                            size="icon"
                            onClick={() => handleRemoveMember(member.id)}
                            disabled={isLoading}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        )}
                      </TableCell>
                    )}
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {isAdmin && pendingInvitations.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>{t("teamSettings.invitations")}</CardTitle>
            </CardHeader>
            <CardContent>
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Email</TableHead>
                    <TableHead>Role</TableHead>
                    <TableHead>Sent</TableHead>
                    <TableHead className="text-right">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {pendingInvitations.map((invitation) => (
                    <TableRow key={invitation.id}>
                      <TableCell className="font-medium">{invitation.email}</TableCell>
                      <TableCell>
                        <Badge variant="outline">{invitation.role}</Badge>
                      </TableCell>
                      <TableCell className="text-muted-foreground text-sm">
                        {new Date(invitation.created_at).toLocaleDateString()}
                      </TableCell>
                      <TableCell className="text-right">
                        <Button
                          variant="ghost"
                          size="icon"
                          onClick={() => handleCancelInvitation(invitation.id)}
                          disabled={isLoading}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </CardContent>
          </Card>
        )}

        {isAdmin && (
          <Card className="border-destructive">
            <CardHeader>
              <CardTitle className="text-destructive">
                {t("teamSettings.dangerZone.title")}
              </CardTitle>
              <CardDescription>{t("teamSettings.dangerZone.warning")}</CardDescription>
            </CardHeader>
            <CardContent>
              <Button variant="destructive" onClick={() => setDeleteDialogOpen(true)}>
                {t("teamSettings.dangerZone.deleteTeam")}
              </Button>
            </CardContent>
          </Card>
        )}

        <Dialog open={inviteModalOpen} onOpenChange={setInviteModalOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("teamSettings.members.invite")}</DialogTitle>
              <DialogDescription>{t("teamSettings.inviteModal.description")}</DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="email">{t("teamSettings.inviteModal.emailLabel")}</Label>
                <Input
                  id="email"
                  placeholder={t("teamSettings.inviteModal.emailPlaceholder")}
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="role">{t("teamSettings.inviteModal.roleLabel")}</Label>
                <Select value={inviteRole} onValueChange={setInviteRole}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="ADMIN">{t("teamSettings.roles.admin")}</SelectItem>
                    <SelectItem value="MEMBER">{t("teamSettings.roles.member")}</SelectItem>
                    <SelectItem value="VIEWER">{t("teamSettings.roles.viewer")}</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setInviteModalOpen(false)}>
                {t("common.cancel")}
              </Button>
              <Button onClick={handleInviteMember} disabled={isLoading || !inviteEmail}>
                {isLoading ? t("common.sending") : t("common.send")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("teamSettings.dangerZone.confirmDelete")}</DialogTitle>
              <DialogDescription>{t("teamSettings.dangerZone.confirmMessage")}</DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                {t("common.cancel")}
              </Button>
              <Button variant="destructive" onClick={handleDeleteTeam} disabled={isLoading}>
                {isLoading ? t("common.deleting") : t("common.delete")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
