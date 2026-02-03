import * as React from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "../ui/alert-dialog";
import { AlertCircle, AlertTriangle, CheckCircle, Info } from "lucide-react";

export interface SimpleAlertDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  title: string;
  description?: string | React.ReactNode;
  confirmText?: string;
  onConfirm?: () => void;
  variant?: "default" | "destructive" | "success" | "warning";
}

export function SimpleAlertDialog({
  open,
  onOpenChange,
  title,
  description,
  confirmText = "OK",
  onConfirm,
  variant = "default",
}: SimpleAlertDialogProps) {
  const Icon =
    variant === "destructive"
      ? AlertCircle
      : variant === "warning"
        ? AlertTriangle
        : variant === "success"
          ? CheckCircle
          : Info;

  const handleConfirm = () => {
    onConfirm?.();
    onOpenChange(false);
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle
            className={`flex items-center gap-2 ${
              variant === "destructive"
                ? "text-destructive"
                : variant === "warning"
                  ? "text-yellow-600"
                  : variant === "success"
                    ? "text-green-600"
                    : ""
            }`}
          >
            <Icon className="w-5 h-5" aria-hidden="true" />
            {title}
          </AlertDialogTitle>
          {description && (
            <AlertDialogDescription>{description}</AlertDialogDescription>
          )}
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogAction onClick={handleConfirm}>
            {confirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
