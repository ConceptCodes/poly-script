import { useTranslation } from "react-i18next";
import { Button } from "@poly/ui";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@poly/ui";
import { useNavigate } from "react-router-dom";

export function ForbiddenPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center py-8">
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">{t("errors.forbidden.title")}</CardTitle>
          <CardDescription>{t("errors.forbidden.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-muted-foreground mb-4">{t("errors.forbidden.message")}</p>
          <div className="flex justify-center">
            <Button onClick={() => navigate("/dashboard")}>{t("common.goToDashboard")}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
