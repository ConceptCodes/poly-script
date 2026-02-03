import { ConfirmDialog } from "@poly/ui";

interface DeleteConfirmModalProps {
  onClose: () => void;
  onConfirm: () => void;
}

export function DeleteConfirmModal({ onClose, onConfirm }: DeleteConfirmModalProps) {
  return (
    <ConfirmDialog
      open
      onOpenChange={onClose}
      title="Delete Transcript"
      description="This will permanently delete the transcript and all its data. This action cannot be undone."
      content="Are you sure you want to delete this transcript? All edits and exports will be lost."
      confirmText="Delete Transcript"
      onConfirm={onConfirm}
      variant="destructive"
    />
  );
}
