import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api, type Clip } from "../api";
import { Button, Card, PageHeader, inputClass } from "../ui";

function fmt(sec: number) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

export default function ClipsPage() {
  const { projectId } = useParams();
  const [clips, setClips] = useState<Clip[]>([]);
  const [suggestions, setSuggestions] = useState<Record<string, string[]>>({});

  const load = useCallback(async () => {
    if (!projectId) return;
    setClips(await api.listClips(projectId));
  }, [projectId]);

  useEffect(() => {
    load();
  }, [load]);

  async function saveTitle(clip: Clip, title: string) {
    const updated = await api.updateClip(clip.id, { title_text: title });
    setClips((cs) => cs.map((c) => (c.id === clip.id ? updated : c)));
  }

  async function toggleSelected(clip: Clip) {
    const updated = await api.updateClip(clip.id, { selected: !clip.selected });
    setClips((cs) => cs.map((c) => (c.id === clip.id ? updated : c)));
  }

  async function suggest(clip: Clip) {
    const res = await api.suggestTitles(clip.id);
    setSuggestions((s) => ({ ...s, [clip.id]: res.suggestions }));
  }

  return (
    <div>
      <PageHeader
        title="Clips"
        subtitle="Detected candidate reels. Edit titles, toggle selection, get AI suggestions."
      />

      {clips.length === 0 && (
        <div className="text-sm text-slate-400">
          No clips yet. Run the pipeline from the project overview.
        </div>
      )}

      <div className="space-y-4">
        {clips.map((clip) => (
          <Card key={clip.id}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="mb-2 flex items-center gap-3">
                  <span className="rounded bg-brand-900/50 px-2 py-0.5 text-xs font-semibold text-brand-300 ring-1 ring-brand-700/60">
                    score {clip.score.toFixed(2)}
                  </span>
                  <span className="text-xs text-slate-500">
                    {fmt(clip.source_start_sec)} – {fmt(clip.source_end_sec)} (
                    {Math.round(clip.source_end_sec - clip.source_start_sec)}s)
                  </span>
                  <label className="ml-auto flex items-center gap-2 text-xs text-slate-400">
                    <input
                      type="checkbox"
                      className="accent-brand-600"
                      checked={clip.selected}
                      onChange={() => toggleSelected(clip)}
                    />
                    selected
                  </label>
                </div>

                <input
                  className={inputClass + " mb-2 font-medium"}
                  defaultValue={clip.title.text}
                  onBlur={(e) => saveTitle(clip, e.target.value)}
                />

                <div className="text-xs text-slate-500">{clip.reason}</div>

                <div className="mt-3 flex items-center gap-3">
                  <Button variant="ghost" onClick={() => suggest(clip)}>
                    Suggest titles
                  </Button>
                  <span className="text-xs text-slate-500">
                    {clip.subtitles.length} subtitle segments ·{" "}
                    {clip.broll.length} b-roll
                  </span>
                </div>

                {suggestions[clip.id] && (
                  <div className="mt-2 space-y-1">
                    {suggestions[clip.id].map((t, i) => (
                      <button
                        key={i}
                        onClick={() => saveTitle(clip, t)}
                        className="block w-full rounded-lg border border-ink-600 bg-ink-900 px-3 py-1.5 text-left text-sm text-slate-200 transition hover:border-brand-600 hover:text-white"
                      >
                        {t}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
