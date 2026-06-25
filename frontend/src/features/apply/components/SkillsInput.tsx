import { useState } from "react";
import { Check, Pencil, Plus, X } from "lucide-react";
import { Badge } from "../../../components/ui/badge";
import { Button } from "../../../components/ui/button";
import { Input } from "../../../components/ui/input";

interface SkillsInputProps {
  label: string;
  values: string[];
  onChange: (nextValues: string[]) => void;
}

export function SkillsInput({ label, values, onChange }: Readonly<SkillsInputProps>) {
  const [draft, setDraft] = useState("");
  const [editingIndex, setEditingIndex] = useState<number | null>(null);
  const isEditing = editingIndex !== null;

  const addOrUpdateSkill = () => {
    const next = draft.trim();
    if (!next) {
      return;
    }

    if (editingIndex !== null) {
      const updated = [...values];
      updated[editingIndex] = next;
      onChange(updated);
      setEditingIndex(null);
      setDraft("");
      return;
    }

    if (!values.some((value) => value.toLowerCase() === next.toLowerCase())) {
      onChange([...values, next]);
    }
    setDraft("");
  };

  return (
    <div className="space-y-3">
      <p className="text-sm font-medium text-slate-700">{label}</p>
      <div className="flex gap-2">
        <Input
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              addOrUpdateSkill();
            }
          }}
          placeholder={isEditing ? `Edit ${label.toLowerCase()}` : `Add ${label.toLowerCase()}`}
        />
        <Button type="button" variant="secondary" onClick={addOrUpdateSkill}>
          {isEditing ? (
            <>
              <Check className="mr-1 h-4 w-4" /> Update
            </>
          ) : (
            <>
              <Plus className="mr-1 h-4 w-4" /> Add
            </>
          )}
        </Button>
      </div>
      <div className="flex flex-wrap gap-2">
        {values.map((value, index) => (
          <Badge key={value} className="gap-2 rounded-lg bg-brand-50 text-brand-700">
            {value}
            <button
              type="button"
              onClick={() => {
                setEditingIndex(index);
                setDraft(value);
              }}
            >
              <Pencil className="h-3.5 w-3.5" />
            </button>
            <button
              type="button"
              onClick={() => onChange(values.filter((_, itemIndex) => itemIndex !== index))}
            >
              <X className="h-3.5 w-3.5" />
            </button>
          </Badge>
        ))}
      </div>
    </div>
  );
}
