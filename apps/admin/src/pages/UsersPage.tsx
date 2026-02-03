import { ConfirmDialog } from "@poly/ui";
import { Badge } from "@poly/ui/badge";
import { Button } from "@poly/ui/button";
import { Card, CardContent } from "@poly/ui/card";
import { Input } from "@poly/ui/input";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@poly/ui/table";
import { AlertCircle, Ban, Mail, RotateCcw, Search, User } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { apiFetch } from "../lib/api";

type UserItem = {
  id: string;
  email: string;
  full_name?: string | null;
  is_active: boolean;
  is_verified: boolean;
  is_suspended: boolean;
  created_at?: string;
};

export function UsersPage() {
  const [items, setItems] = useState<UserItem[]>([]);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<"all" | "active" | "suspended" | "unverified">("all");
  const [userToDelete, setUserToDelete] = useState<{
    id: string;
    email: string;
  } | null>(null);

  const refresh = useCallback(() => {
    const q = query.trim();
    const queryString = q ? `?q=${encodeURIComponent(q)}` : "";
    apiFetch<{ items: UserItem[] }>(`/admin/users${queryString}`).then((data) =>
      setItems(data.items),
    );
  }, [query]);

  useEffect(() => {
    const handle = setTimeout(() => {
      refresh();
    }, 300);
    return () => clearTimeout(handle);
  }, [refresh]);

  const action = async (path: string, reason?: string) => {
    await apiFetch(path, { method: "POST", body: reason ? { reason } : {} });
    refresh();
  };

  const remove = async (id: string) => {
    await apiFetch(`/admin/users/${id}`, { method: "DELETE" });
    setUserToDelete(null);
    refresh();
  };

  const filteredItems = items.filter((user) => {
    if (filter === "all") return true;
    if (filter === "active") return user.is_active && !user.is_suspended;
    if (filter === "suspended") return user.is_suspended;
    if (filter === "unverified") return !user.is_verified;
    return true;
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight mb-2">Users</h1>
        <p className="text-muted-foreground">Manage user accounts and access.</p>
      </div>

      <Card className="border-border">
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by email or name"
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                className="pl-10"
              />
            </div>
            <div className="flex gap-2">
              {(["all", "active", "suspended", "unverified"] as const).map((f) => (
                <Button
                  key={f}
                  variant={filter === f ? "default" : "outline"}
                  size="sm"
                  className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                  onClick={() => setFilter(f)}
                >
                  {f.charAt(0).toUpperCase() + f.slice(1)}
                </Button>
              ))}
              <Button
                variant="outline"
                size="sm"
                className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                onClick={refresh}
              >
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="border-border">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Email</TableHead>
              <TableHead>Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Verified</TableHead>
              <TableHead>Suspended</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredItems.map((user) => (
              <TableRow key={user.id}>
                <TableCell>
                  <Link
                    to={`/users/${user.id}`}
                    className="flex items-center gap-2 text-left focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                  >
                    <Mail className="h-4 w-4 text-muted-foreground" aria-hidden="true" />
                    <span>{user.email}</span>
                  </Link>
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <User className="h-4 w-4 text-muted-foreground" />
                    <span>{user.full_name || "-"}</span>
                  </div>
                </TableCell>
                <TableCell>
                  <Badge variant={user.is_active ? "default" : "secondary"}>
                    {user.is_active ? "Active" : "Inactive"}
                  </Badge>
                </TableCell>
                <TableCell>
                  <Badge variant={user.is_verified ? "default" : "outline"}>
                    {user.is_verified ? "Verified" : "No"}
                  </Badge>
                </TableCell>
                <TableCell>
                  {user.is_suspended ? (
                    <Badge variant="destructive">
                      <AlertCircle className="h-3 w-3 mr-1" />
                      Suspended
                    </Badge>
                  ) : (
                    <span className="text-muted-foreground">No</span>
                  )}
                </TableCell>
                <TableCell>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="outline"
                      size="sm"
                      className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                      onClick={() =>
                        action(
                          `/admin/users/${user.id}/${user.is_suspended ? "unsuspend" : "suspend"}`,
                        )
                      }
                    >
                      {user.is_suspended ? (
                        <>
                          <RotateCcw className="h-3 w-3 mr-1" />
                          Unsuspend
                        </>
                      ) : (
                        <>
                          <Ban className="h-3 w-3 mr-1" />
                          Suspend
                        </>
                      )}
                    </Button>
                    <Button
                      variant="destructive"
                      size="sm"
                      className="focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                      onClick={() => setUserToDelete({ id: user.id, email: user.email })}
                    >
                      Delete
                    </Button>
                  </div>
                </TableCell>
              </TableRow>
            ))}
            {!filteredItems.length && (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                  No users found.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </Card>

      <ConfirmDialog
        open={!!userToDelete}
        onOpenChange={(open) => !open && setUserToDelete(null)}
        title="Delete User"
        description={`Are you sure you want to delete ${userToDelete?.email}? This action cannot be undone.`}
        onConfirm={() => userToDelete && remove(userToDelete.id)}
        confirmText="Delete User"
        variant="destructive"
      />
    </div>
  );
}
