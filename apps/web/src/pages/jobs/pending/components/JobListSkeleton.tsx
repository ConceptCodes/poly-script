import { Card, CardContent } from "@poly/ui/card";
import { Skeleton } from "@poly/ui/skeleton";

export function JobListSkeleton() {
  return (
    <div className="space-y-4">
      {[...Array(5)].map((_, i) => (
        <Card key={i}>
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Skeleton className="w-5 h-5" />
                  <Skeleton className="w-48 h-6" />
                  <Skeleton className="w-20 h-6" />
                </div>
              </div>
              <div className="space-y-2">
                <Skeleton className="w-full h-4" />
                <Skeleton className="w-3/4 h-4" />
              </div>
              <div className="flex items-center gap-3">
                <Skeleton className="w-24 h-9" />
                <Skeleton className="w-20 h-9" />
              </div>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
