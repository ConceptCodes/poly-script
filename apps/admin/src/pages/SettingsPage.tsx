import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import { Input } from "@poly/ui/input";
import { Label } from "@poly/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@poly/ui/select";
import { Switch } from "@poly/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@poly/ui/tabs";
import { Textarea } from "@poly/ui/textarea";
import {
  AlertTriangle,
  Database,
  FileCode,
  Globe,
  Mail,
  RefreshCw,
  Save,
  Shield,
  Webhook,
  Zap,
} from "lucide-react";
import { useEffect, useState } from "react";
import { apiFetch } from "../lib/api";

type SettingsData = {
  administrators: Array<{ id: string; email: string; full_name: string }>;
  system: Record<string, unknown>;
};

type SystemSettings = {
  engines?: {
    whisper?: { enabled: boolean; default: boolean };
    speechmatics?: { enabled: boolean; default: boolean; api_key?: string };
    assemblyai?: { enabled: boolean; default: boolean; api_key?: string };
  };
  rate_limits?: {
    max_jobs_per_minute?: number;
    max_upload_size_mb?: number;
  };
  storage?: {
    provider?: "local" | "s3" | "gcs";
    local_path?: string;
    s3_bucket?: string;
    s3_region?: string;
  };
  email?: {
    smtp_host?: string;
    smtp_port?: number;
    smtp_user?: string;
    from_address?: string;
  };
  auth?: {
    session_timeout_minutes?: number;
    max_login_attempts?: number;
  };
  plans?: {
    free_jobs_limit?: number;
    free_members_limit?: number;
    standard_price_monthly?: number;
    pro_price_monthly?: number;
  };
  localization?: {
    default_language?: string;
    supported_languages?: string[];
  };
  webhooks?: {
    enabled?: boolean;
    signature_header?: string;
  };
  maintenance?: {
    enabled?: boolean;
    message?: string;
  };
};

export function SettingsPage() {
  const [settings, setSettings] = useState<SettingsData | null>(null);
  const [draft, setDraft] = useState<string>("");
  const [activeTab, setActiveTab] = useState("engines");
  const [localSettings, setLocalSettings] = useState<SystemSettings>({});
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    apiFetch<SettingsData>("/admin/system/settings").then((data) => {
      setSettings(data);
      const parsed = data.system as SystemSettings;
      setLocalSettings(parsed);
      setDraft(JSON.stringify(data.system, null, 2));
    });
  }, []);

  const save = async () => {
    setSaving(true);
    try {
      const payload = localSettings as Record<string, unknown>;
      const updated = await apiFetch<SettingsData>("/admin/system/settings", {
        method: "PATCH",
        body: payload,
      });
      setSettings(updated);
      setLocalSettings(updated.system as SystemSettings);
      setDraft(JSON.stringify(updated.system, null, 2));
    } catch (_err) {
      // Error handling - could add error state here
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = <K extends keyof SystemSettings>(key: K, value: SystemSettings[K]) => {
    setLocalSettings((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">System Settings</h1>
          <p className="text-muted-foreground">Configure system-level settings and preferences.</p>
        </div>
        <Button onClick={save} disabled={saving}>
          {saving ? (
            <>
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
              Saving…
            </>
          ) : (
            <>
              <Save className="h-4 w-4 mr-2" />
              Save Settings
            </>
          )}
        </Button>
      </div>

      <Card className="border-border">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Administrators
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            {settings?.administrators?.map((admin) => (
              <div
                key={admin.id}
                className="flex items-center gap-2 p-2 rounded-lg border border-border"
              >
                <Badge variant="outline">{admin.email}</Badge>
                <span className="text-sm text-muted-foreground">{admin.full_name}</span>
              </div>
            )) || <div className="text-sm text-muted-foreground">No administrators listed.</div>}
          </div>
        </CardContent>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-2 lg:grid-cols-5">
          <TabsTrigger value="engines">Engines</TabsTrigger>
          <TabsTrigger value="storage">Storage</TabsTrigger>
          <TabsTrigger value="rate-limits">Rate Limits</TabsTrigger>
          <TabsTrigger value="email">Email</TabsTrigger>
          <TabsTrigger value="advanced">Advanced</TabsTrigger>
        </TabsList>

        <TabsContent value="engines" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                STT Engines
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Whisper</Label>
                    <p className="text-sm text-muted-foreground">Local OpenAI Whisper engine</p>
                  </div>
                  <Switch
                    checked={localSettings.engines?.whisper?.enabled ?? false}
                    onCheckedChange={(checked) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        whisper: {
                          ...localSettings.engines?.whisper,
                          enabled: checked,
                        },
                      } as SystemSettings["engines"])
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Default Engine</Label>
                    <p className="text-sm text-muted-foreground">Use Whisper as default</p>
                  </div>
                  <Switch
                    checked={localSettings.engines?.whisper?.default ?? false}
                    onCheckedChange={(checked) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        whisper: {
                          ...localSettings.engines?.whisper,
                          default: checked,
                        },
                      } as SystemSettings["engines"])
                    }
                  />
                </div>
              </div>

              <div className="border-t border-border pt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Speechmatics</Label>
                    <p className="text-sm text-muted-foreground">Cloud Speechmatics engine</p>
                  </div>
                  <Switch
                    checked={localSettings.engines?.speechmatics?.enabled ?? false}
                    onCheckedChange={(checked) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        speechmatics: {
                          ...localSettings.engines?.speechmatics,
                          enabled: checked,
                        },
                      } as SystemSettings["engines"])
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Default Engine</Label>
                    <p className="text-sm text-muted-foreground">Use Speechmatics as default</p>
                  </div>
                  <Switch
                    checked={localSettings.engines?.speechmatics?.default ?? false}
                    onCheckedChange={(checked) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        speechmatics: {
                          ...localSettings.engines?.speechmatics,
                          default: checked,
                        },
                      } as SystemSettings["engines"])
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="speechmatics-api-key">API Key</Label>
                  <Input
                    id="speechmatics-api-key"
                    type="password"
                    value={localSettings.engines?.speechmatics?.api_key || ""}
                    autoComplete="off"
                    spellCheck={false}
                    onChange={(e) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        speechmatics: {
                          ...localSettings.engines?.speechmatics,
                          api_key: e.target.value,
                        },
                      } as SystemSettings["engines"])
                    }
                    placeholder="Enter API key"
                  />
                </div>
              </div>

              <div className="border-t border-border pt-6 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">AssemblyAI</Label>
                    <p className="text-sm text-muted-foreground">Cloud AssemblyAI engine</p>
                  </div>
                  <Switch
                    checked={localSettings.engines?.assemblyai?.enabled ?? false}
                    onCheckedChange={(checked) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        assemblyai: {
                          ...localSettings.engines?.assemblyai,
                          enabled: checked,
                        },
                      } as SystemSettings["engines"])
                    }
                  />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label className="font-medium">Default Engine</Label>
                    <p className="text-sm text-muted-foreground">Use AssemblyAI as default</p>
                  </div>
                  <Switch
                    checked={localSettings.engines?.assemblyai?.default ?? false}
                    onCheckedChange={(checked) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        assemblyai: {
                          ...localSettings.engines?.assemblyai,
                          default: checked,
                        },
                      } as SystemSettings["engines"])
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="assemblyai-api-key">API Key</Label>
                  <Input
                    id="assemblyai-api-key"
                    type="password"
                    value={localSettings.engines?.assemblyai?.api_key || ""}
                    autoComplete="off"
                    spellCheck={false}
                    onChange={(e) =>
                      updateSetting("engines", {
                        ...localSettings.engines,
                        assemblyai: {
                          ...localSettings.engines?.assemblyai,
                          api_key: e.target.value,
                        },
                      } as SystemSettings["engines"])
                    }
                    placeholder="Enter API key"
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="storage" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Storage Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <Label htmlFor="storage-provider">Storage Provider</Label>
                <Select
                  value={localSettings.storage?.provider || "local"}
                  onValueChange={(value) =>
                    updateSetting("storage", {
                      ...localSettings.storage,
                      provider: value as "local" | "s3" | "gcs",
                    } as SystemSettings["storage"])
                  }
                >
                  <SelectTrigger id="storage-provider">
                    <SelectValue placeholder="Select storage provider" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="local">Local filesystem</SelectItem>
                    <SelectItem value="s3">Amazon S3</SelectItem>
                    <SelectItem value="gcs">Google Cloud Storage</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {localSettings.storage?.provider === "local" && (
                <div className="space-y-2">
                  <Label htmlFor="local-path">Local Path</Label>
                  <Input
                    id="local-path"
                    value={localSettings.storage?.local_path || ""}
                    autoComplete="off"
                    spellCheck={false}
                    onChange={(e) =>
                      updateSetting("storage", {
                        ...localSettings.storage,
                        local_path: e.target.value,
                      } as SystemSettings["storage"])
                    }
                    placeholder="/var/lib/polyscript/uploads"
                  />
                </div>
              )}

              {localSettings.storage?.provider === "s3" && (
                <>
                  <div className="space-y-2">
                    <Label htmlFor="s3-bucket">S3 Bucket</Label>
                    <Input
                      id="s3-bucket"
                      value={localSettings.storage?.s3_bucket || ""}
                      autoComplete="off"
                      spellCheck={false}
                      onChange={(e) =>
                        updateSetting("storage", {
                          ...localSettings.storage,
                          s3_bucket: e.target.value,
                        } as SystemSettings["storage"])
                      }
                      placeholder="my-bucket-name"
                    />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="s3-region">S3 Region</Label>
                    <Input
                      id="s3-region"
                      value={localSettings.storage?.s3_region || ""}
                      autoComplete="off"
                      spellCheck={false}
                      onChange={(e) =>
                        updateSetting("storage", {
                          ...localSettings.storage,
                          s3_region: e.target.value,
                        } as SystemSettings["storage"])
                      }
                      placeholder="us-east-1"
                    />
                  </div>
                </>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="rate-limits" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Zap className="h-5 w-5" />
                Rate Limits
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="max-jobs">Max Jobs Per Minute</Label>
                <Input
                  id="max-jobs"
                  type="number"
                  value={localSettings.rate_limits?.max_jobs_per_minute || ""}
                  inputMode="numeric"
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("rate_limits", {
                      ...localSettings.rate_limits,
                      max_jobs_per_minute: parseInt(e.target.value, 10) || undefined,
                    } as SystemSettings["rate_limits"])
                  }
                  placeholder="10"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max-upload">Max Upload Size (MB)</Label>
                <Input
                  id="max-upload"
                  type="number"
                  value={localSettings.rate_limits?.max_upload_size_mb || ""}
                  inputMode="numeric"
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("rate_limits", {
                      ...localSettings.rate_limits,
                      max_upload_size_mb: parseInt(e.target.value, 10) || undefined,
                    } as SystemSettings["rate_limits"])
                  }
                  placeholder="500"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="email" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Mail className="h-5 w-5" />
                Email Configuration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="smtp-host">SMTP Host</Label>
                <Input
                  id="smtp-host"
                  value={localSettings.email?.smtp_host || ""}
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("email", {
                      ...localSettings.email,
                      smtp_host: e.target.value,
                    } as SystemSettings["email"])
                  }
                  placeholder="smtp.example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp-port">SMTP Port</Label>
                <Input
                  id="smtp-port"
                  type="number"
                  value={localSettings.email?.smtp_port || ""}
                  inputMode="numeric"
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("email", {
                      ...localSettings.email,
                      smtp_port: parseInt(e.target.value, 10) || undefined,
                    } as SystemSettings["email"])
                  }
                  placeholder="587"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="smtp-user">SMTP Username</Label>
                <Input
                  id="smtp-user"
                  value={localSettings.email?.smtp_user || ""}
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("email", {
                      ...localSettings.email,
                      smtp_user: e.target.value,
                    } as SystemSettings["email"])
                  }
                  placeholder="user@example.com"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="from-address">From Address</Label>
                <Input
                  id="from-address"
                  value={localSettings.email?.from_address || ""}
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("email", {
                      ...localSettings.email,
                      from_address: e.target.value,
                    } as SystemSettings["email"])
                  }
                  placeholder="noreply@polyscript.io"
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="advanced" className="space-y-4">
          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                Authentication & Session
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="session-timeout">Session Timeout (minutes)</Label>
                <Input
                  id="session-timeout"
                  type="number"
                  value={localSettings.auth?.session_timeout_minutes || ""}
                  inputMode="numeric"
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("auth", {
                      ...localSettings.auth,
                      session_timeout_minutes: parseInt(e.target.value, 10) || undefined,
                    } as SystemSettings["auth"])
                  }
                  placeholder="1440"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="max-login-attempts">Max Login Attempts</Label>
                <Input
                  id="max-login-attempts"
                  type="number"
                  value={localSettings.auth?.max_login_attempts || ""}
                  inputMode="numeric"
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("auth", {
                      ...localSettings.auth,
                      max_login_attempts: parseInt(e.target.value, 10) || undefined,
                    } as SystemSettings["auth"])
                  }
                  placeholder="5"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                Localization
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="default-language">Default Language</Label>
                <Input
                  id="default-language"
                  value={localSettings.localization?.default_language || ""}
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("localization", {
                      ...localSettings.localization,
                      default_language: e.target.value,
                    } as SystemSettings["localization"])
                  }
                  placeholder="en"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Webhook className="h-5 w-5" />
                Webhooks
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Enable Webhooks</Label>
                  <p className="text-sm text-muted-foreground">Send webhook notifications</p>
                </div>
                <Switch
                  checked={localSettings.webhooks?.enabled ?? false}
                  onCheckedChange={(checked) =>
                    updateSetting("webhooks", {
                      ...localSettings.webhooks,
                      enabled: checked,
                    } as SystemSettings["webhooks"])
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="signature-header">Signature Header</Label>
                <Input
                  id="signature-header"
                  value={localSettings.webhooks?.signature_header || ""}
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("webhooks", {
                      ...localSettings.webhooks,
                      signature_header: e.target.value,
                    } as SystemSettings["webhooks"])
                  }
                  placeholder="X-PolyScript-Signature"
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5" />
                Maintenance Mode
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label className="font-medium">Enable Maintenance Mode</Label>
                  <p className="text-sm text-muted-foreground">
                    Temporarily disable all user access
                  </p>
                </div>
                <Switch
                  checked={localSettings.maintenance?.enabled ?? false}
                  onCheckedChange={(checked) =>
                    updateSetting("maintenance", {
                      ...localSettings.maintenance,
                      enabled: checked,
                    } as SystemSettings["maintenance"])
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="maintenance-message">Maintenance Message</Label>
                <Input
                  id="maintenance-message"
                  value={localSettings.maintenance?.message || ""}
                  autoComplete="off"
                  spellCheck={false}
                  onChange={(e) =>
                    updateSetting("maintenance", {
                      ...localSettings.maintenance,
                      message: e.target.value,
                    } as SystemSettings["maintenance"])
                  }
                  placeholder="System is under maintenance. Please check back later."
                />
              </div>
            </CardContent>
          </Card>

          <Card className="border-destructive/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive">
                <FileCode className="h-5 w-5" />
                Advanced: Direct JSON Editor
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-muted-foreground">
                Edit the raw system configuration JSON directly. Be careful with manual edits.
              </p>
              <Textarea
                className="min-h-[300px] font-mono text-sm"
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
              />
              <Button
                variant="destructive"
                onClick={async () => {
                  try {
                    const payload = JSON.parse(draft || "{}");
                    const updated = await apiFetch<SettingsData>("/admin/system/settings", {
                      method: "PATCH",
                      body: payload,
                    });
                    setSettings(updated);
                    setLocalSettings(updated.system as SystemSettings);
                    setDraft(JSON.stringify(updated.system, null, 2));
                  } catch (_err) {
                    // Error handling - invalid JSON
                  }
                }}
              >
                Save JSON
              </Button>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
