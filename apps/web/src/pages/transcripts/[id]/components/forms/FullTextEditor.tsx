import { useState } from "react";
import { useForm } from "@tanstack/react-form";
import { Button } from "@poly-ui/button";
import { Textarea } from "@poly-ui/textarea";
import { Save, Loader2 } from "lucide-react";

interface FullTextEditorProps {
  initialText: string;
  onSave: (text: string) => Promise<void>;
  isSaving: boolean;
}

export function FullTextEditor({ initialText, onSave, isSaving }: FullTextEditorProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(initialText);

  const form = useForm({
    defaultValues: {
      text: initialText,
    },
    onSubmit: async ({ value }) => {
      await onSave(value.text);
      setIsEditing(false);
    },
  });

  const handleCancel = () => {
    setEditText(initialText);
    setIsEditing(false);
    form.reset();
  };

  if (!isEditing) {
    return (
      <div className="space-y-4">
        <div className="p-4 bg-muted/50 rounded-lg whitespace-pre-wrap min-h-[200px]">
          {initialText}
        </div>
        <div className="flex justify-end">
          <Button onClick={() => setIsEditing(true)}>Edit Text</Button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={form.handleSubmit} className="space-y-4">
      <form.Field
        name="text"
        validators={{
          onChange: (value) => {
            if (!value.value || value.value.trim().length === 0) {
              return "Transcript text cannot be empty";
            }
            return undefined;
          },
        }}
      >
        {(field) => (
          <Textarea
            value={field.state.value}
            onChange={(e) => field.handleChange(e.target.value)}
            onBlur={field.handleBlur}
            className="min-h-[300px] font-mono text-sm"
            placeholder="Enter transcript text..."
          />
        )}
      </form.Field>

      {form.state.errors.text && (
        <p className="text-sm text-destructive">{form.state.errors.text}</p>
      )}

      <div className="flex justify-end gap-2">
        <Button type="button" variant="outline" onClick={handleCancel} disabled={isSaving}>
          Cancel
        </Button>
        <Button type="submit" disabled={isSaving}>
          {isSaving ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4 mr-2" />
              Save
            </>
          )}
        </Button>
      </div>
    </form>
  );
}
