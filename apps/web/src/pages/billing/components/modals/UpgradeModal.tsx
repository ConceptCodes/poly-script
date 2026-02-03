import {
  Button,
  Dialog,
  DialogClose,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@poly/ui";
import { Loader2 } from "lucide-react";

interface UpgradeModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  planName: string;
  price: number;
  onConfirm: () => void;
  isLoading: boolean;
}

export function UpgradeModal({
  open,
  onOpenChange,
  planName,
  price,
  onConfirm,
  isLoading,
}: UpgradeModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Upgrade to {planName}</DialogTitle>
          <DialogDescription>You are about to upgrade your subscription.</DialogDescription>
        </DialogHeader>
        <div className="py-4">
          <p>
            You will be charged <strong>${price}/month</strong> starting today.
          </p>
          <p className="text-sm text-muted-foreground mt-2">
            The amount will be prorated based on your current cycle.
          </p>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={onConfirm} disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Confirm Upgrade
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
