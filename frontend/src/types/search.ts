export type MatchSource = "filename" | "body" | "ocr" | "vision";

export interface MatchCitation {
  term: string;
  source: MatchSource;
  confidence: number;
  lineNo?: number;
}

export interface Result {
  id: string;
  fileName: string;
  ext: string;
  folder: string;
  snippet: string;
  score: number;
  minutesAgo: number;
  sizeBytes: number;
  lineCount: number;
  citations: MatchCitation[];
  fullContent: string;
  experimental?: {
    feature: "ocr" | "vision";
    label: string;
  };
}

export type Recency = "fresh" | "recent" | "stale" | "cold";
