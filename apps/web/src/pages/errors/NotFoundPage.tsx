import { Button, Card, CardContent, CardDescription, CardHeader, CardTitle } from "@poly/ui";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";

export function NotFoundPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center py-8">
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">{t("errors.notFound.title")}</CardTitle>
          <CardDescription>{t("errors.notFound.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-muted-foreground mb-4">{t("errors.notFound.message")}</p>
          <div className="flex justify-center space-x-4">
            <Button onClick={() => navigate(-1)}>{t("common.back")}</Button>
            <Button onClick={() => navigate("/dashboard")}>{t("common.goToDashboard")}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
