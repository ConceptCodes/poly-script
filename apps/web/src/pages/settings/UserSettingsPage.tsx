import { useTranslation } from "react-i18next";
import { useForm } from "@tanstack/react-form";
import { Button } from "@poly/ui/components/ui/button";
import { Input } from "@poly/ui/components/ui/input";
import { Label } from "@poly/ui/components/ui/label";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@poly/ui/components/ui/card";
import { Switch } from "@poly/ui/components/ui/switch";
import { useAuthStore } from "../../lib/store";

export function UserSettingsPage() {
  const { t } = useTranslation();
  const { user, setUser } = useAuthStore();
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = React.useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);

  const [form, Field] = useForm({
    defaultValues: {
      name: "",
      email: "",
      currentPassword: "",
      newPassword: "",
      confirmPassword: "",
    },
  });

  const handleUpdateProfile = async ({ value }) => {
    setIsLoading(true);

    try {
      const response = await api.patch("/v1/user/profile", {
        name: value.name,
      });
      setUser({ ...user, ...response.data });
      setSuccessMessage(t("userSettings.success"));
    } catch (error: any) {
      console.error("Failed to update profile:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateEmail = async () => {
    setIsLoading(true);

    try {
      const response = await api.post("/v1/user/email/update", {
        email: form.state.values.email,
      });
      setUser({ ...user, email: response.data.email });
      setSuccessMessage(t("userSettings.emailUpdateSuccess"));
    } catch (error: any) {
      console.error("Failed to update email:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePassword = async () => {
    if (form.state.values.newPassword !== form.state.values.confirmPassword) {
      setIsLoading(true);

      try {
        const response = await api.post("/v1/user/password", {
          current_password: form.state.values.currentPassword,
          new_password: form.state.values.newPassword,
        });
        setSuccessMessage(t("userSettings.passwordUpdateSuccess"));
      } catch (error: any) {
        console.error("Failed to update password:", error);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleUpdatePreferences = async () => {
    setIsLoading(true);

    try {
      const response = await api.patch("/v1/user/preferences", {
        language: form.state.values.language,
      });
      setUser({ ...user, language: response.data.language });
      i18n.changeLanguage(response.data.language);
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
      const response = await api.patch("/v1/user/notifications", {
        email_notifications: form.state.values.emailNotifications,
        in_app_notifications: form.state.values.inAppNotifications,
      });
      setUser({ ...user, ...response.data });
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
      await api.delete("/v1/user");
      navigate("/");
    } catch (error: any) {
      console.error("Failed to delete account:", error);
    } finally {
      setIsLoading(false);
      setShowDeleteDialog(false);
    }
  };

  return (
    <div className="min-h-screen bg-background py-8">
      <div className="container max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-6">{t("userSettings.title")}</h1>

        {successMessage && (
          <Alert variant="default" className="mb-6">
            {successMessage}
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
                  <Input id={field.name} value={user.email} disabled />
                  <p className="text-sm text-muted-foreground">
                    {t("userSettings.email.readOnly")}
                  </p>
                </div>
              )}
            </form.Field>

            <div>
              <Button variant="outline" onClick={handleUpdateEmail} disabled={isLoading}>
                {t("userSettings.email.updateButton")}
              </Button>
            </div>

            <form.Field name="currentPassword">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.currentPassword.label")}</Label>
                  <Input type="password" id={field.name} />
                </div>
              )}
            </form.Field>

            <form.Field name="newPassword">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.newPassword.label")}</Label>
                  <Input type="password" id={field.name} />
                </div>
              )}
            </form.Field>

            <form.Field name="confirmPassword">
              {(field) => (
                <div>
                  <Label htmlFor={field.name}>{t("userSettings.confirmPassword.label")}</Label>
                  <Input type="password" id={field.name} />
                  {field.state.meta.errors && (
                    <p className="text-sm text-red-500">{field.state.meta.errors[0]}</p>
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
                  <select className="w-full">
                    {field.Component}
                    <option value="en">English</option>
                    <option value="de">Deutsch</option>
                    <option value="es">Español</option>
                    <option value="fr">Français</option>
                    <option value="jp">日本語</option>
                  </select>
                </div>
              )}
            </form.Field>

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
            <div className="flex items-center space-x-4">
              <Label htmlFor="emailNotifications">{t("userSettings.notifications.email")}</Label>
              <Switch
                id="emailNotifications"
                checked={form.state.values.emailNotifications}
                onCheckedChange={(checked) => form.setValue("emailNotifications", checked)}
              />
            </div>

            <div className="flex items-center space-x-4">
              <Label htmlFor="inAppNotifications">{t("userSettings.notifications.inApp")}</Label>
              <Switch
                id="inAppNotifications"
                checked={form.state.values.inAppNotifications}
                onCheckedChange={(checked) => form.setValue("inAppNotifications", checked)}
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

        <AlertDialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
          <AlertDialogContent>
            <AlertDialogHeader>
              <AlertDialogTitle>{t("userSettings.dangerZone.confirmDelete")}</AlertDialogTitle>
            </AlertDialogHeader>
            <AlertDialogBody>{t("userSettings.dangerZone.confirmMessage")}</AlertDialogBody>
            <AlertDialogFooter>
              <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
                {t("common.cancel")}
              </Button>
              <Button variant="destructive" onClick={handleDeleteAccount} disabled={isLoading}>
                {isLoading ? t("common.deleting") : t("common.delete")}
              </Button>
            </AlertDialogFooter>
          </AlertDialogContent>
        </AlertDialog>

        <Button onClick={() => navigate(-1)}>{t("common.back")}</Button>
      </div>
    </div>
  );
}
