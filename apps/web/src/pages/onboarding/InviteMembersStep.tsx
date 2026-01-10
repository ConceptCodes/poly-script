import { useTranslation } from "react-i18next";
import { useForm } from "@tanstack/react-form";
import { Button } from "@poly/ui";
import { Input } from "@poly/ui";
import { Label } from "@poly/ui";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@poly/ui";
import { Trash2 } from "lucide-react";

export function InviteMembersStep() {
  const { t } = useTranslation();
  const form = useForm({
    defaultValues: {
      members: [""],
    },
  });

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{t("onboarding.inviteMembers.title")}</CardTitle>
          <CardDescription>{t("onboarding.inviteMembers.description")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form.Field
            name="members"
            validators={{
              onChange: ({ value }) =>
                value.every(
                  (email) => email.length === 0 || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email),
                ) || t("onboarding.inviteMembers.invalidEmail"),
            }}
          >
            {(field) => (
              <div>
                <Label htmlFor={field.name}>{t("onboarding.inviteMembers.label")}</Label>
                <Input
                  id={field.name}
                  value={field.state.value}
                  onChange={(e) => field.handleChange(e.target.value)}
                  placeholder={t("onboarding.inviteMembers.placeholder")}
                />
                {field.state.value.map((email, index) => (
                  <div key={index} className="flex items-center gap-2">
                    <Input value={email} readOnly className="flex-1" />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() =>
                        field.handleChange(field.state.value.filter((_, i) => i !== index))
                      }
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
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
