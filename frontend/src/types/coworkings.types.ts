export interface Coworking {
  id: string;
  name: string;
  building: number;
  entrance: number;
  number: number;
  available: boolean;
}

export interface StudentShort {
  user_id: string;
  last_name: string;
  first_name: string;
  patronymic: string | null;
  building: number;
  entrance: number;
  room: string;
}

export type BookingStatus = "created" | "active" | "completed" | "cancelled";

export interface Booking {
  id: string;
  student_id: string;
  coworking_id: string;
  taken_from: string;
  returned_back: string;
  status: BookingStatus;
}

export interface BookingDetail extends Booking {
  student: StudentShort | null;
  coworking: Coworking | null;
}

export interface BookingListResponse {
  items: BookingDetail[];
  total: number;
  limit: number;
  offset: number;
}

export interface BookingCreateRequest {
  coworking_id: string;
  taken_from: string;
  returned_back: string;
}

export interface BookingListFilters {
  status?: string;
  coworking_id?: string;
  student_id?: string;
  coworking_name?: string;
  limit?: number;
  offset?: number;
}

export interface BookingHistoryFilters extends BookingListFilters {
  date_from?: string;
  date_to?: string;
}

export interface CoworkingListFilters {
  building?: number;
  entrance?: number;
  available?: boolean;
}
