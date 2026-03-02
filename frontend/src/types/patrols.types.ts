export interface PatrolEntry {
  patrol_entry_id: string;
  patrol_id: string;
  user_id: string;
  room: string;
  is_present: boolean | null;
  absence_reason: string | null;
  checked_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface Patrol {
  patrol_id: string;
  date: string;
  building: string;
  entrance: number;
  status: "in_progress" | "completed";
  started_at: string;
  submitted_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface PatrolDetail extends Patrol {
  entries: PatrolEntry[];
}

export interface PatrolCreateRequest {
  date: string;
  building: string;
  entrance: number;
}

export interface PatrolUpdateRequest {
  status: "completed";
}

export interface PatrolEntryUpdateRequest {
  is_present: boolean | null;
  absence_reason?: string | null;
}

export interface PatrolListFilters {
  page?: number;
  size?: number;
  date?: string;
  building?: string;
  entrance?: number;
  status?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}
