export interface Application {
  id: string;
  user_id: string;
  is_minor: boolean;
  leave_time: string;
  return_time: string;
  reason: string;
  contact_phone: string;
  status: "pending" | "approved" | "rejected";
  decided_by: string | null;
  decided_at: string | null;
  reject_reason: string | null;
  created_at: string;
  updated_at: string;
  user_name?: string | null;
  room?: string | null;
  entrance?: number | null;
}

export interface ApplicationDocument {
  id: string;
  application_id: string;
  document_type: string;
  file_url: string;
  uploaded_by: string;
  created_at: string;
}

export interface ApplicationDetail extends Application {
  documents: ApplicationDocument[];
  can_decide?: boolean;
}

export interface ApplicationCreateRequest {
  leave_time: string;
  return_time: string;
  reason: string;
  contact_phone: string;
}

export interface ApplicationDecideRequest {
  status: "approved" | "rejected";
  reject_reason?: string | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApplicationListFilters {
  page?: number;
  size?: number;
  status?: string;
  date_from?: string;
  date_to?: string;
  entrance?: number;
  room?: string;
}
