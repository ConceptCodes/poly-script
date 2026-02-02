import React, { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Button } from "@poly/ui";
import { Input } from "@poly/ui";
import { Label } from "@poly/ui";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@poly/ui";
import { Trash2 } from "lucide-react";

type Member = { email: string; role: string };

export function InviteMembersStep({ data, updateData }: { data: { members: string[] }; updateData: (key: string, value: any) => void }) {
  const { t } = useTranslation();
  const [members, setMembers] = useState<Member[]>(
    data.members.length ? data.members.map((email) => ({ email, role: "MEMBER" })) : [{ email: "", role: "MEMBER" }]
  );

  useEffect(() => {
    updateData("members", members.filter((m) => m.email.length > 0).map((m) => m.email));
  }, [members]);

  const addMember = () => setMembers((m) => [...m, { email: "", role: "MEMBER" }]);
  const updateMember = (idx: number, field: "email" | "role", value: string) =>
    setMembers((m) => m.map((v, i) => (i === idx ? { ...v, [field]: value } : v)));
  const removeMember = (idx: number) => setMembers((m) => m.filter((_, i) => i !== idx));

  const emailsValid = members.every((member) => member.email.length === 0 || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(member.email));

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl">{t("onboarding.inviteMembers.title")}</CardTitle>
          <CardDescription>{t("onboarding.inviteMembers.subtitle")}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <Label htmlFor="members-list">{t("onboarding.inviteMembers.memberEmail")}</Label>
            <div className="space-y-2 mt-2" id="members-list">
              {members.map((member, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    value={member.email}
                    onChange={(e) => updateMember(index, "email", e.target.value)}
                    placeholder={t("onboarding.inviteMembers.placeholder")}
                    className="flex-1"
                  />
                  <Select
                    value={member.role}
                    onValueChange={(value) => updateMember(index, "role", value)}
                    className="w-[120px]"
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="ADMIN">{t("onboarding.inviteMembers.memberRoleAdmin")}</SelectItem>
                      <SelectItem value="MEMBER">{t("onboarding.inviteMembers.memberRoleMember")}</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button type="button" variant="ghost" size="icon" onClick={() => removeMember(index)}>
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
            {!emailsValid && (
              <p className="text-sm text-red-500">{t("onboarding.error.invalidEmail")}</p>
            )}
          </div>
          <Button type="button" onClick={addMember}>
            {t("onboarding.inviteMembers.addMember")}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
