import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@poly/ui";
import { CheckCircle2 } from "lucide-react";
import { useTranslation } from "react-i18next";

export function CompleteStep(_props: { onNext?: () => void }) {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader className="text-center">
          <div className="flex flex-col items-center gap-4">
            <div className="h-16 w-16 rounded-full bg-green-100 flex items-center justify-center">
              <CheckCircle2 className="h-10 w-10 text-green-600" />
            </div>
            <CardTitle className="text-2xl">{t("onboarding.complete.title")}</CardTitle>
            <CardDescription>{t("onboarding.complete.description")}</CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground">{t("onboarding.complete.nextSteps")}</p>
        </CardContent>
      </Card>
    </div>
  );
}
