import { Card, CardContent, CardDescription, CardHeader, CardTitle, Input, Label } from "@poly/ui";
import { useForm } from "@tanstack/react-form";
import { useTranslation } from "react-i18next";

// Adapt to flexible props to support OnboardingPage wiring
export function TeamNameStep(_props: {
  data?: { teamName?: string };
  updateData?: (key: string, value: string) => void;
  onNext?: () => void;
}) {
  const { t } = useTranslation();
  const form = useForm({
    defaultValues: {
      teamName: "",
    },
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{t("onboarding.teamName.title")}</CardTitle>
          <CardDescription>{t("onboarding.teamName.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form.Field
            name="teamName"
            validators={{
              onChange: ({ value }) => value.length >= 2 || t("onboarding.teamName.minLength"),
            }}
          >
            {(field) => (
              <div>
                <Label htmlFor={field.name}>{t("onboarding.teamName.label")}</Label>
                <Input
                  id={field.name}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  placeholder={t("onboarding.teamName.placeholder")}
                />
                {field.state.meta.errors && (
                  <p className="text-sm text-destructive">{field.state.meta.errors[0]}</p>
                )}
              </div>
            )}
          </form.Field>
        </CardContent>
      </Card>
    </div>
  );
}
