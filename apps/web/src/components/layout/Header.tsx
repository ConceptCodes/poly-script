import { Link } from "react-router-dom";
import { Badge, Button } from "@poly/ui";
import { useEffect, useState } from "react";
import { apiFetch } from "../../lib/api";

interface SimpleUsage {
  plan: string;
  monthly_upload_count: number;
  monthly_limit: number | "inf";
}

export function Header() {
  const [usage, setUsage] = useState<SimpleUsage | null>(null);

  useEffect(() => {
    // Poll usage every 10 seconds or just fetch once on mount
    // For now, just once on mount
    const fetchUsage = async () => {
      try {
        const data = await apiFetch("/billing/usage");
        setUsage(data);
      } catch (e) {
        console.error("Failed to fetch header usage", e);
      }
    };
    fetchUsage();
  }, []);

  return (
    <nav className="border-b px-6 py-4 flex items-center justify-between bg-card text-card-foreground shadow-sm">
      <div className="flex items-center space-x-6">
        <Link to="/" className="font-bold text-xl flex items-center gap-2">
          <span>PolyScript</span>
        </Link>
        <div className="h-6 w-px bg-border"></div>
        <Link to="/upload" className="text-sm font-medium hover:text-primary transition-colors">Upload</Link>
        <Link to="/billing" className="text-sm font-medium hover:text-primary transition-colors">Billing</Link>
      </div>
      
      <div className="flex items-center space-x-4">
        {usage && (
          <div className="flex items-center gap-2 text-sm text-muted-foreground mr-2">
            <span>
              {usage.monthly_upload_count} / {usage.monthly_limit === "inf" ? "∞" : usage.monthly_limit} uploads
            </span>
            <Badge variant={usage.plan === 'PRO' ? 'default' : usage.plan === 'STANDARD' ? 'secondary' : 'outline'}>
              {usage.plan}
            </Badge>
          </div>
        )}
        
        <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center text-xs font-bold text-primary border border-primary/20">
          JD
        </div>
      </div>
    </nav>
  );
}
