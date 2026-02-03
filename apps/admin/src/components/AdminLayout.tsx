import { Button } from "@poly/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@poly/ui/card";
import {
  BarChart3,
  Briefcase,
  Building2,
  FileText,
  LayoutDashboard,
  LogOut,
  Settings,
  Users,
} from "lucide-react";
import { useEffect } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuthStore } from "../store/auth";

const navItems = [
  { label: "Dashboard", to: "/", icon: LayoutDashboard },
  { label: "Users", to: "/users", icon: Users },
  { label: "Teams", to: "/teams", icon: Building2 },
  { label: "Jobs", to: "/jobs", icon: Briefcase },
  { label: "Analytics", to: "/analytics", icon: BarChart3 },
  { label: "Settings", to: "/settings", icon: Settings },
  { label: "Audit Logs", to: "/audit-logs", icon: FileText },
];

export function AdminLayout() {
  const navigate = useNavigate();
  const { hydrate, adminEmail, clear } = useAuthStore();

  useEffect(() => {
    hydrate();
  }, [hydrate]);

  return (
    <div className="admin-shell">
      <aside className="admin-sidebar">
        <div className="mb-6">
          <Card className="border-border bg-card/80 backdrop-blur">
            <CardHeader className="pb-2">
              <CardTitle className="text-lg">PolyScript Admin</CardTitle>
            </CardHeader>
            <CardContent className="text-xs text-muted-foreground">
              Secure control plane
            </CardContent>
          </Card>
        </div>
        <Card className="mb-6 bg-card/80 backdrop-blur">
          <CardContent className="pt-4">
            <div className="text-xs text-muted-foreground mb-1">Signed in as</div>
            <div className="font-semibold text-sm">{adminEmail || "admin@polyscript"}</div>
            <Button
              variant="outline"
              size="sm"
              className="w-full mt-3 focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
              onClick={() => {
                clear();
                navigate("/login");
              }}
            >
              <LogOut className="h-4 w-4 mr-2" />
              Sign out
            </Button>
          </CardContent>
        </Card>
        <nav className="space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary ${
                  isActive
                    ? "bg-primary/10 text-primary border border-primary/20"
                    : "text-muted-foreground hover:bg-accent hover:text-accent-foreground border border-transparent"
                }`
              }
            >
              <item.icon className="h-4 w-4" />
              {item.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
}
