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

export function TeamNameStep() {
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
                  <p className="text-sm text-red-500">{field.state.meta.errors[0]}</p>
                )}
              </div>
            )}
          </form.Field>
        </CardContent>
      </Card>
    </div>
  );
}
