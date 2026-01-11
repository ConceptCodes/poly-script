import { AlertTriangle } from "lucide-react";

import { Button } from "@poly-ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@poly-ui/dialog";

interface DeleteConfirmModalProps {
  onClose: () => void;
  onConfirm: () => void;
}

export function DeleteConfirmModal({ onClose, onConfirm }: DeleteConfirmModalProps) {
  return (
    <Dialog open onOpenChange={onClose}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-destructive">
            <AlertTriangle className="w-5 h-5" />
            Delete Transcript
          </DialogTitle>
          <DialogDescription>
            This will permanently delete the transcript and all its data.
            This action cannot be undone.
          </DialogDescription>
        </DialogHeader>

        <div className="py-4">
          <p className="text-sm text-muted-foreground">
            Are you sure you want to delete this transcript? All edits and exports
            will be lost.
          </p>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={onClose}>
            Cancel
          </Button>
          <Button variant="destructive" onClick={onConfirm}>
            Delete Transcript
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
