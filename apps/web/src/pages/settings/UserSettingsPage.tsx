import { useState } from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import { useForm } from "@tanstack/react-form";
import { Button } from "@poly/ui";
import { Input } from "@poly/ui";
import { Label } from "@poly/ui";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@poly/ui";
import { Switch } from "@poly/ui";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui";
import { Alert, AlertDescription } from "@poly/ui";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@poly/ui";
import { useAppStore } from "../../lib/store";
import { apiFetch } from "../../lib/api";

export function UserSettingsPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { user } = useAppStore();
  const [isLoading, setIsLoading] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [successMessage, setSuccessMessage] = useState("");
  const [theme, setTheme] = useState<"light" | "dark" | "system">(user?.theme || "system"));

  const form = useForm({
    defaultValues: {
      name: user?.name || "",
      email: user?.email || "",
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
      language: user?.language || "en",
      emailNotifications: user?.email_notifications ?? true,
      jobCompletionNotifications: user?.job_completion_notifications ?? true,
      inAppNotifications: user?.in_app_notifications ?? true,
    },
  });

  const handleUpdateEmail = async () => {
    setIsLoading(true);
    try {
      await apiFetch("/v1/user/email/update", {
        method: "POST",
        body: { email: form.state.values.email },
      });
      setSuccessMessage(t("userSettings.emailUpdateSuccess"));
    } catch (error: any) {
      console.error("Failed to update email:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePassword = async () => {
    setIsLoading(true);
    try {
      await apiFetch("/v1/user/password", {
        method: "POST",
        body: {
          current_password: form.state.values.currentPassword,
          new_password: form.state.values.newPassword,
        },
      });
      setSuccessMessage(t("userSettings.passwordUpdateSuccess"));
    } catch (error: any) {
      console.error("Failed to update password:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePreferences = async () => {
    setIsLoading(true);
    try {
      await apiFetch("/v1/user/preferences", {
        method: "PATCH",
        body: { language: form.state.values.language, theme },
      });
      setSuccessMessage(t("userSettings.preferencesUpdateSuccess"));
    } catch (error: any) {
      console.error("Failed to update preferences:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateNotifications = async () => {
    setIsLoading(true);
    try {
      await apiFetch("/v1/user/notifications", {
        method: "PATCH",
        body: {
          email_notifications: form.state.values.emailNotifications,
          job_completion_notifications: form.state.values.jobCompletionNotifications,
          in_app_notifications: form.state.values.inAppNotifications,
        },
      });
      setSuccessMessage(t("userSettings.notificationsUpdateSuccess"));
    } catch (error: any) {
      console.error("Failed to update notifications:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = async () => {
    setIsLoading(true);
    try {
      await apiFetch("/v1/user", {
        method: "DELETE",
      });
      navigate("/");
    } catch (error: any) {
      console.error("Failed to delete account:", error);
    } finally {
      setIsLoading(false);
      setShowDeleteDialog(false);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString(undefined, {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">{t("userSettings.title")}</h1>

        {successMessage && (
          <Alert variant="default" className="mb-6">
            <AlertDescription>{successMessage}</AlertDescription>
          </Alert>
        )}

        <Card>
          <CardHeader>
            <CardTitle>{t("userSettings.profile.title")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <form.Field name="name">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.name.label")}</Label>
                  <Input
                    id={field.name}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                </div>
              )}
            </form.Field>

            <form.Field name="email">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.email.label")}</Label>
                  <Input id={field.name} value={field.state.value} disabled />
                  <p className="text-xs text-muted-foreground mt-1">
                    {t("userSettings.email.read")}
                  </p>
                </div>
              )}
            </form.Field>

            <Button onClick={handleUpdateEmail} disabled={isLoading}>
              {t("userSettings.email.updateButton")}
            </Button>

            <div className="space-y-2 pt-4">
              <h3 className="font-medium">{t("userSettings.account.title")}</h3>
              {user?.created_at && (
                <p className="text-sm text-muted-foreground">
                  {t("userSettings.account.joined")}: {formatDate(user.created_at)}
                </p>
              )}
              {user?.last_login && (
                <p className="text-sm text-muted-foreground">
                  {t("userSettings.account.lastLogin")}: {formatDate(user.last_login)}
                </p>
              )}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("userSettings.password.title")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <form.Field name="currentPassword">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.currentPassword.label")}</Label>
                  <Input
                    type="password"
                    id={field.name}
                    placeholder={t("userSettings.currentPassword.placeholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                </div>
              )}
            </form.Field>

            <form.Field name="newPassword">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.newPassword.label")}</Label>
                  <Input
                    type="password"
                    id={field.name}
                    placeholder={t("userSettings.newPassword.placeholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                </div>
              )}
            </form.Field>

            <form.Field name="confirmPassword">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.confirmPassword.label")}</Label>
                  <Input
                    type="password"
                    id={field.name}
                    placeholder={t("userSettings.confirmPassword.placeholder")}
                    value={field.state.value}
                    onChange={(e) => field.handleChange(e.target.value)}
                  />
                  {field.state.meta.errors.length > 0 && (
                    <p className="text-sm text-destructive">{field.state.meta.errors[0]}</p>
                  )}
                </div>
              )}
            </form.Field>

            <Button onClick={handleUpdatePassword} disabled={isLoading}>
              {t("userSettings.password.updateButton")}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("userSettings.preferences.title")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <form.Field name="language">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.language.label")}</Label>
                  <Select value={field.state.value} onValueChange={field.handleChange}>
                    <SelectTrigger className="w-full">
                      <SelectValue placeholder={t("userSettings.language.placeholder")} />
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

            <div className="space-y-2">
              <Label htmlFor="theme">{t("userSettings.theme.label")}</Label>
              <Select value={theme} onValueChange={setTheme}>
                <SelectTrigger className="w-full">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="light">{t("userSettings.theme.light")}</SelectItem>
                  <SelectItem value="dark">{t("userSettings.theme.dark")}</SelectItem>
                  <SelectItem value="system">{t("userSettings.theme.system")}</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button onClick={handleUpdatePreferences} disabled={isLoading}>
              {t("userSettings.preferences.updateButton")}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("userSettings.notifications.title")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <Label htmlFor="emailNotifications">{t("userSettings.notifications.email")}</Label>
                <p className="text-xs text-muted-foreground">{t("userSettings.notifications.emailDesc")}</p>
              </div>
              <Switch
                id="emailNotifications"
                checked={form.state.values.emailNotifications}
                onCheckedChange={(checked) => (form as any).setValue("emailNotifications", checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex-1">
                <Label htmlFor="jobCompletionNotifications">{t("userSettings.notifications.jobComplete")}</Label>
                <p className="text-xs text-muted-foreground">{t("userSettings.notifications.jobCompleteDesc")}</p>
              </div>
              <Switch
                id="jobCompletionNotifications"
                checked={form.state.values.jobCompletionNotifications}
                onCheckedChange={(checked) => (form as any).setValue("jobCompletionNotifications", checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="flex-1">
                <Label htmlFor="inAppNotifications">{t("userSettings.notifications.inApp")}</Label>
                <p className="text-xs text-muted-foreground">{t("userSettings.notifications.inAppDesc")}</p>
              </div>
              <Switch
                id="inAppNotifications"
                checked={form.state.values.inAppNotifications}
                onCheckedChange={(checked) => (form as any).setValue("inAppNotifications", checked)}
              />
            </div>

            <Button onClick={handleUpdateNotifications} disabled={isLoading}>
              {t("userSettings.notifications.updateButton")}
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>{t("userSettings.dangerZone.title")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <p className="text-sm text-muted-foreground mb-4">
              {t("userSettings.dangerZone.warning")}
            </p>
            <Button variant="destructive" onClick={() => setShowDeleteDialog(true)}>
              {t("userSettings.dangerZone.deleteAccount")}
            </Button>
          </CardContent>
        </Card>

        <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>{t("userSettings.dangerZone.confirmDelete")}</DialogTitle>
              <DialogDescription>{t("userSettings.dangerZone.confirmMessage")}</DialogDescription>
            </DialogHeader>
            <DialogFooter>
              <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
                {t("common.cancel")}
              </Button>
              <Button variant="destructive" onClick={handleDeleteAccount} disabled={isLoading}>
                {isLoading ? t("common.deleting") : t("common.delete")}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>

        <Button onClick={() => navigate(-1)}>{t("common.back")}</Button>
      </div>
    </div>
  );
}
