import { useTranslation } from "react-i18next";
import { Button } from "@poly/ui/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@poly/ui/components/ui/card";

export function InternalServerErrorPage() {
  const { t } = useTranslation();

  return (
    <div className="min-h-screen bg-background flex items-center justify-center py-8">
      <Card className="max-w-md">
        <CardHeader>
          <CardTitle className="text-2xl">{t("errors.internalError.title")}</CardTitle>
          <CardDescription>{t("errors.internalError.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-muted-foreground mb-4">{t("errors.internalError.message")}</p>
          <div className="flex justify-center">
            <Button onClick={() => (window.location.href = "/")}>{t("common.goToHomepage")}</Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
