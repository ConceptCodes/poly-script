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
import { CreditCard, Loader2 } from "lucide-react";

interface ConfirmPurchaseModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  credits: number;
  totalPrice: string;
  onConfirm: () => void;
  isLoading: boolean;
}

export function ConfirmPurchaseModal({
  open,
  onOpenChange,
  credits,
  totalPrice,
  onConfirm,
  isLoading,
}: ConfirmPurchaseModalProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <CreditCard className="h-5 w-5" />
            Confirm Credit Purchase
          </DialogTitle>
          <DialogDescription>Review your purchase before continuing to checkout.</DialogDescription>
        </DialogHeader>
        <div className="py-4 space-y-2">
          <div className="flex justify-between text-sm">
            <span>Credits</span>
            <span className="font-medium">{credits}</span>
          </div>
          <div className="flex justify-between text-sm">
            <span>Total</span>
            <span className="font-medium">${totalPrice}</span>
          </div>
          <p className="text-xs text-muted-foreground">
            You will be redirected to Stripe to complete payment.
          </p>
        </div>
        <DialogFooter>
          <DialogClose asChild>
            <Button variant="outline">Cancel</Button>
          </DialogClose>
          <Button onClick={onConfirm} disabled={isLoading}>
            {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Continue to Checkout
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
