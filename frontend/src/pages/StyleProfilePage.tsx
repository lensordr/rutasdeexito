import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api, type StyleProfile } from "../api";
import { Button, Card, Field, PageHeader, inputClass } from "../ui";

export default function StyleProfilePage() {
  const { projectId } = useParams();
  const [profile, setProfile] = useState<StyleProfile | null>(null);
  const [status, setStatus] = useState<string>("");

  const load = useCallback(async () => {
    if (!projectId) return;
    const project = await api.getProject(projectId);
    if (!project.style_profile_id) {
      setStatus("Run the pipeline first to generate a style profile.");
      return;
    }
    setProfile(await api.getStyleProfile(project.style_profile_id));
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  async function save() {
    if (!profile) return;
    setStatus("Saving…");
    try {
      const updated = await api.updateStyleProfile(profile.id, profile);
      setProfile(updated);
      setStatus("Saved.");
    } catch (e) {
      setStatus(String(e));
    }
  }

  if (!profile) {
    return (
      <div>
        <PageHeader title="Style Profile" />
        <div className="text-sm text-slate-400">{status || "Loading…"}</div>
      </div>
    );
  }

  const up = (patch: Partial<StyleProfile>) =>
    setProfile({ ...profile, ...patch });

  return (
    <div>
      <PageHeader
        title="Style Profile"
        subtitle="The reel creation guide derived from your page. Fully editable."
        actions={<Button onClick={save}>Save changes</Button>}
      />
      {status && (
        <div className="mb-4 text-sm text-slate-500">{status}</div>
      )}

      <Card className="mb-6">
        <div className="mb-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Clip preferences
        </div>
        <div className="grid grid-cols-3 gap-4">
          <Field label="Profile name">
            <input
              className={inputClass}
              value={profile.name}
              onChange={(e) => up({ name: e.target.value })}
            />
          </Field>
          <Field label="Target duration (s)">
            <input
              type="number"
              className={inputClass}
              value={profile.target_duration_sec}
              onChange={(e) =>
                up({ target_duration_sec: Number(e.target.value) })
              }
            />
          </Field>
          <Field label="Hook style">
            <select
              className={inputClass}
              value={profile.hook_style}
              onChange={(e) => up({ hook_style: e.target.value })}
            >
              <option value="question">Question</option>
              <option value="bold_claim">Bold claim</option>
              <option value="story">Story</option>
              <option value="stat">Stat</option>
            </select>
          </Field>
        </div>
      </Card>

      <Card className="mb-6">
        <div className="mb-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Subtitle style
        </div>
        <div className="grid grid-cols-3 gap-4">
          <Field label="Font family">
            <input
              className={inputClass}
              value={profile.subtitle.font_family}
              onChange={(e) =>
                up({
                  subtitle: { ...profile.subtitle, font_family: e.target.value },
                })
              }
            />
          </Field>
          <Field label="Font color">
            <input
              type="color"
              className={inputClass + " h-10 p-1"}
              value={profile.subtitle.font_color}
              onChange={(e) =>
                up({
                  subtitle: { ...profile.subtitle, font_color: e.target.value },
                })
              }
            />
          </Field>
          <Field label="Highlight color">
            <input
              type="color"
              className={inputClass + " h-10 p-1"}
              value={profile.subtitle.highlight_color}
              onChange={(e) =>
                up({
                  subtitle: {
                    ...profile.subtitle,
                    highlight_color: e.target.value,
                  },
                })
              }
            />
          </Field>
        </div>
      </Card>

      <Card>
        <div className="mb-4 text-xs font-semibold uppercase tracking-wide text-slate-400">
          Behaviour
        </div>
        <div className="flex gap-6">
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              className="accent-brand-600"
              checked={profile.auto_zoom}
              onChange={(e) => up({ auto_zoom: e.target.checked })}
            />
            Auto zoom
          </label>
          <label className="flex items-center gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              className="accent-brand-600"
              checked={profile.use_broll}
              onChange={(e) => up({ use_broll: e.target.checked })}
            />
            Use b-roll
          </label>
        </div>
      </Card>
    </div>
  );
}
