export interface SearchHit {
  id: string;
  score: number;
  payload: {
    doc_url: string;
    doc_title?: string;
    text: string;
    index?: number;
  };
}

export async function search(
  q: string,
  opts: { topK?: number; hyde?: boolean } = {},
): Promise<SearchHit[]> {
  const params = new URLSearchParams({ q });
  if (opts.topK) params.set("top_k", String(opts.topK));
  if (opts.hyde) params.set("hyde", "1");
  const res = await fetch(`/search?${params.toString()}`);
  if (!res.ok) throw new Error(`Search failed (${res.status})`);
  const data = (await res.json()) as { results: SearchHit[] };
  return data.results ?? [];
}

export interface AskHandlers {
  onSources?: (sources: string[]) => void;
  onToken?: (text: string) => void;
}

export async function askStream(
  q: string,
  opts: { hyde?: boolean } = {},
  handlers: AskHandlers = {},
): Promise<void> {
  const params = new URLSearchParams({ q });
  if (opts.hyde) params.set("hyde", "1");
  const res = await fetch(`/ask/stream?${params.toString()}`);
  if (!res.ok) throw new Error(`Ask failed (${res.status})`);
  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";
    for (const line of lines) {
      const trimmed = line.trim();
      if (!trimmed.startsWith("data:")) continue;
      const json = trimmed.slice(5).trim();
      if (!json) continue;
      const evt = JSON.parse(json) as
        | { type: "sources"; sources: string[] }
        | { type: "token"; text: string };
      if (evt.type === "sources") handlers.onSources?.(evt.sources);
      else if (evt.type === "token") handlers.onToken?.(evt.text);
    }
  }
}
