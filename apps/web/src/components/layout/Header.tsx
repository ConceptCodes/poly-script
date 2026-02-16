import { Badge } from "@poly/ui";
import { Avatar, AvatarFallback } from "@poly/ui/avatar";
import { Button } from "@poly/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@poly/ui/dropdown-menu";
import { Menu, Waveform, X } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { apiFetch } from "../../lib/api";
import { LanguageSwitcher } from "../LanguageSwitcher";

interface SimpleUsage {
  plan: string;
  monthly_upload_count: number;
  monthly_limit: number | "inf";
}

function LogoMark() {
  return (
    <Link to="/" className="flex items-center gap-2.5 group">
      <div className="relative w-9 h-9">
        <svg
          viewBox="0 0 36 36"
          className="w-full h-full transform group-hover:scale-105 transition-transform duration-300"
        >
          <title>PolyScript logo</title>
          <defs>
            <linearGradient id="waveformGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4F46E5" />
              <stop offset="100%" stopColor="#8B5CF6" />
            </linearGradient>
          </defs>
          <rect x="2" y="2" width="32" height="32" rx="8" fill="url(#waveformGradient)" />
          <g fill="white" opacity="0.95">
            <rect x="8" y="14" width="3" height="12" rx="1" />
            <rect x="14" y="10" width="3" height="20" rx="1" />
            <rect x="20" y="8" width="3" height="24" rx="1" />
            <rect x="26" y="12" width="3" height="16" rx="1" />
          </g>
        </svg>
      </div>
      <span className="font-bold text-xl tracking-tight text-foreground">PolyScript</span>
    </Link>
  );
}

function NavLink({
  to,
  children,
  isActive,
  isPrimary = false,
}: {
  to: string;
  children: React.ReactNode;
  isActive: boolean;
  isPrimary?: boolean;
}) {
  if (isPrimary) {
    return (
      <Link
        to={to}
        className={`
          relative px-4 py-2 rounded-full text-sm font-medium
          transition-all duration-300 ease-out
          ${
            isActive
              ? "bg-gradient-to-r from-primary to-accent text-white shadow-lg shadow-primary/20"
              : "text-foreground hover:text-primary hover:bg-primary/10 dark:hover:bg-primary/20"
          }
        `}
      >
        {children}
      </Link>
    );
  }

  return (
    <Link
      to={to}
      className={`
        relative px-4 py-2 rounded-full text-sm font-medium
        transition-all duration-200 ease-out
        text-muted-foreground hover:text-foreground hover:bg-muted/50
      `}
    >
      {children}
      {isActive && (
        <span className="absolute bottom-0 left-4 right-4 h-0.5 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-full" />
      )}
    </Link>
  );
}

function UsageIndicator({ usage }: { usage: SimpleUsage }) {
  const isUnlimited = usage.monthly_limit === "inf";
  const usagePercent = isUnlimited ? 100 : (usage.monthly_upload_count / usage.monthly_limit) * 100;

   const planColors = {
    PRO: "bg-gradient-to-r from-primary to-accent",
    STANDARD: "bg-gradient-to-r from-info to-info/90",
    FREE: "bg-gradient-to-r from-muted to-muted/90",
  };

  const planBadgeColors = {
    PRO: "bg-gradient-to-r from-primary/10 to-accent/10 border-primary/20 text-primary dark:text-primary/80",
    STANDARD: "bg-gradient-to-r from-info/10 to-info/20 border-info/20 text-info dark:text-info/80",
    FREE: "bg-gradient-to-r from-muted/10 to-muted/20 border-muted/20 text-muted-foreground dark:text-muted-foreground/70",
  };

  return (
    <div className="flex items-center gap-3 text-sm">
      {!isUnlimited && (
        <div className="flex flex-col gap-1 min-w-[120px]">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>
              {usage.monthly_upload_count} / {usage.monthly_limit}
            </span>
            <span>{Math.round(usagePercent)}%</span>
          </div>
          <div className="h-1.5 bg-muted rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ease-out ${planColors[usage.plan as keyof typeof planColors] || planColors.FREE}`}
              style={{ width: `${Math.min(usagePercent, 100)}%` }}
            />
          </div>
        </div>
      )}

      <Badge
        variant="outline"
        className={`font-semibold text-xs px-2.5 py-1 rounded-full border ${planBadgeColors[usage.plan as keyof typeof planBadgeColors] || planBadgeColors.FREE}`}
      >
        {usage.plan}
      </Badge>
    </div>
  );
}

function UserAvatar() {
  const initials = "JD";

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="ghost" className="relative h-9 w-9 rounded-full" aria-label="User menu">
          <Avatar className="h-9 w-9">
            <AvatarFallback className="bg-gradient-to-br from-primary to-accent text-white">
              {initials}
            </AvatarFallback>
          </Avatar>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end" className="w-56">
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">john.doe@example.com</p>
          </div>
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem>Profile</DropdownMenuItem>
        <DropdownMenuItem>Settings</DropdownMenuItem>
        <DropdownMenuSeparator />
        <DropdownMenuItem className="text-destructive">Sign out</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

function MobileMenu({
  isOpen,
  onClose,
  usage,
}: {
  isOpen: boolean;
  onClose: () => void;
  usage: SimpleUsage | null;
}) {
  const { pathname } = useLocation();

  if (!isOpen) return null;

  return (
    <>
      <div
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 animate-in fade-in duration-200"
        onClick={onClose}
        aria-hidden="true"
      />

      <div className="fixed top-0 right-0 bottom-0 w-[280px] bg-background border-l border-border z-50 animate-in slide-in-from-right duration-300 ease-out">
        <div className="flex flex-col h-full">
          <div className="flex items-center justify-between p-4 border-b border-border">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8">
                <svg viewBox="0 0 36 36" className="w-full h-full">
                  <title>PolyScript logo</title>
                  <defs>
                    <linearGradient id="waveformGradientMobile" x1="0%" y1="0%" x2="100%" y2="100%">
                      <stop offset="0%" stopColor="#4F46E5" />
                      <stop offset="100%" stopColor="#8B5CF6" />
                    </linearGradient>
                  </defs>
                  <rect
                    x="2"
                    y="2"
                    width="32"
                    height="32"
                    rx="8"
                    fill="url(#waveformGradientMobile)"
                  />
                  <g fill="white" opacity="0.95">
                    <rect x="8" y="14" width="3" height="12" rx="1" />
                    <rect x="14" y="10" width="3" height="20" rx="1" />
                    <rect x="20" y="8" width="3" height="24" rx="1" />
                    <rect x="26" y="12" width="3" height="16" rx="1" />
                  </g>
                </svg>
              </div>
              <span className="font-bold text-lg">PolyScript</span>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={onClose}
              className="p-2 rounded-lg hover:bg-muted transition-colors"
              aria-label="Close menu"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            <Link
              to="/upload"
              onClick={onClose}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all
                ${
                  pathname === "/upload"
                    ? "bg-gradient-to-r from-indigo-500 to-violet-500 text-white"
                    : "text-foreground hover:bg-muted"
                }
              `}
            >
              <Waveform className="h-4 w-4" />
              Upload
            </Link>
            <Link
              to="/jobs/pending"
              onClick={onClose}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all
                ${
                  pathname.startsWith("/jobs")
                    ? "bg-gradient-to-r from-indigo-500 to-violet-500 text-white"
                    : "text-foreground hover:bg-muted"
                }
              `}
            >
              <div className="h-4 w-4 rounded-full bg-foreground/20" />
              Jobs
            </Link>
            <Link
              to="/billing"
              onClick={onClose}
              className={`
                flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all
                ${
                  pathname === "/billing"
                    ? "bg-gradient-to-r from-indigo-500 to-violet-500 text-white"
                    : "text-foreground hover:bg-muted"
                }
              `}
            >
              <div className="h-4 w-4 rounded-full bg-foreground/20" />
              Billing
            </Link>
          </nav>

          <div className="border-t border-border p-4 space-y-4">
            {usage && <UsageIndicator usage={usage} />}
            <LanguageSwitcher className="w-full" showIcon={true} />
          </div>
        </div>
      </div>
    </>
  );
}

export function Header() {
  const [usage, setUsage] = useState<SimpleUsage | null>(null);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const location = useLocation();
  const headerRef = useRef<HTMLElement>(null);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const data = await apiFetch("/billing/usage");
        setUsage(data as SimpleUsage);
      } catch (e) {
        console.error("Failed to fetch header usage", e);
      }
    };
    fetchUsage();
  }, []);

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  useEffect(() => {
    if (location.pathname) {
      setIsMobileMenuOpen(false);
    }
  }, [location.pathname]);

  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = "hidden";
    } else {
      document.body.style.overflow = "";
    }
    return () => {
      document.body.style.overflow = "";
    };
  }, [isMobileMenuOpen]);

  return (
    <>
      <header
        ref={headerRef}
        className={`
          fixed top-4 left-4 right-4 z-50 max-w-7xl mx-auto
          transition-all duration-300 ease-out
          ${isScrolled ? "shadow-xl shadow-indigo-500/10" : "shadow-md"}
        `}
      >
        <div
          className={`
            rounded-2xl border border-border/50 backdrop-blur-xl
            transition-all duration-300 ease-out
            ${isScrolled ? "bg-background/95" : "bg-background/80 hover:bg-background/90"}
          `}
        >
          <div className="hidden md:flex items-center justify-between px-6 py-3">
            <div className="flex items-center">
              <LogoMark />
            </div>

            <nav className="flex items-center gap-1">
              <NavLink to="/upload" isActive={location.pathname === "/upload"} isPrimary={true}>
                Upload
              </NavLink>
              <NavLink to="/jobs/pending" isActive={location.pathname.startsWith("/jobs")}>
                Jobs
              </NavLink>
              <NavLink to="/billing" isActive={location.pathname === "/billing"}>
                Billing
              </NavLink>
            </nav>

            <div className="flex items-center gap-4">
              <LanguageSwitcher className="w-[140px]" showIcon={true} />
              {usage && <UsageIndicator usage={usage} />}
              <UserAvatar />
            </div>
          </div>

          <div className="md:hidden flex items-center justify-between px-4 py-3">
            <LogoMark />

            <div className="flex items-center gap-3">
              {usage && (
                <Badge
                  variant="outline"
                  className={`font-semibold text-xs px-2.5 py-1 rounded-full border ${
                    usage.plan === "PRO"
                      ? "bg-primary/10 border-primary/20 text-primary dark:text-primary/80"
                      : usage.plan === "STANDARD"
                        ? "bg-info/10 border-info/20 text-info dark:text-info/80"
                        : "bg-muted/10 border-muted/20 text-muted-foreground dark:text-muted-foreground/70"
                  }`}
                >
                  {usage.plan}
                </Badge>
              )}
              <Button
                type="button"
                variant="ghost"
                size="icon"
                onClick={() => setIsMobileMenuOpen(true)}
                className="p-2.5 rounded-xl hover:bg-muted transition-colors"
                aria-label="Open menu"
              >
                <Menu className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="h-20" />

      <MobileMenu
        isOpen={isMobileMenuOpen}
        onClose={() => setIsMobileMenuOpen(false)}
        usage={usage}
      />
    </>
  );
}
