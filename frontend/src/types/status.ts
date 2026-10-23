export interface DaemonStatusInfo {
  status: "RUNNING" | "OFFLINE";
  reachable: boolean;
  port: number;
  startup_installed: boolean;
}

export interface IndexStatusInfo {
  indexed_count: number;
  storage_path: string;
  collection_name: string;
  model_name: string;
}

export interface WatchedDirectoryItem {
  path: string;
  name: string;
  exists: boolean;
  shallow_file_count: number;
}

export interface DiagnosticsInfo {
  os: string;
  python_version: string;
  tesseract_available: boolean;
  cargo_available: boolean;
}

export interface StatusResponse {
  daemon: DaemonStatusInfo;
  index: IndexStatusInfo;
  watched_directories: WatchedDirectoryItem[];
  diagnostics: DiagnosticsInfo;
}

export interface StatsResponse {
  daemon_status: string;
  daemon_reachable: boolean;
  daemon_pid: number | null;
  daemon_port: number;
  total_files_indexed: number;
  vector_embeddings_stored: number;
  neural_vector_model: string;
  multimodal_vision_model: string;
  vector_db_disk_size_mb: number;
  file_accesses_logged: number;
  co_access_links_formed: number;
  monitored_directories_count: number;
  monitored_directories: string[];
}

export interface WatchedFolder {
  id: string;
  path: string;
  fileCount: number;
  exists?: boolean;
}
