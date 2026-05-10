import { Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Label } from "@poly/ui";
import { useTranslation } from "react-i18next";
import type { OnboardingStepProps } from "./types";

export function TeamNameStep({ data, updateData }: OnboardingStepProps) {
  const { t } = useTranslation();
  const isValid = data.teamName.length >= 2 || data.teamName.length === 0;

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{t("onboarding.teamName.title")}</CardTitle>
          <CardDescription>{t("onboarding.teamName.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="team-name">{t("onboarding.teamName.label")}</Label>
            <Input
              id="team-name"
              value={data.teamName}
              onChange={(e) => updateData("teamName", e.target.value)}
              placeholder={t("onboarding.teamName.placeholder")}
            />
            {!isValid && (
              <p className="text-sm text-destructive">{t("onboarding.teamName.minLength")}</p>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
