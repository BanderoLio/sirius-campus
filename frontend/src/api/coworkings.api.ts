import type { AxiosResponse } from "axios";
import apiClient from "./client";
import type {
  Coworking,
  Booking,
  BookingDetail,
  BookingListResponse,
  BookingCreateRequest,
  BookingListFilters,
  BookingHistoryFilters,
  CoworkingListFilters,
} from "@/types/coworkings.types";

export async function fetchCoworkings(
  filters: CoworkingListFilters = {},
): Promise<Coworking[]> {
  const params = new URLSearchParams();
  if (filters.building != null) params.set("building", String(filters.building));
  if (filters.entrance != null) params.set("entrance", String(filters.entrance));
  if (filters.available != null)
    params.set("available", String(filters.available));
  const res: AxiosResponse<Coworking[]> = await apiClient.get(
    "/api/v1/coworkings",
    { params },
  );
  return res.data;
}

export async function fetchCoworking(id: string): Promise<Coworking> {
  const res: AxiosResponse<Coworking> = await apiClient.get(
    `/api/v1/coworkings/${id}`,
  );
  return res.data;
}

export async function createBooking(
  data: BookingCreateRequest,
): Promise<Booking> {
  const res: AxiosResponse<Booking> = await apiClient.post(
    "/api/v1/bookings",
    data,
  );
  return res.data;
}

export async function fetchBookings(
  filters: BookingListFilters = {},
): Promise<BookingListResponse> {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.coworking_id) params.set("coworking_id", filters.coworking_id);
  if (filters.student_id) params.set("student_id", filters.student_id);
  if (filters.coworking_name)
    params.set("coworking_name", filters.coworking_name);
  if (filters.limit != null) params.set("limit", String(filters.limit));
  if (filters.offset != null) params.set("offset", String(filters.offset));
  const res: AxiosResponse<BookingListResponse> = await apiClient.get(
    "/api/v1/bookings",
    { params },
  );
  return res.data;
}

export async function fetchMyBookings(
  filters: { status?: string; limit?: number; offset?: number } = {},
): Promise<BookingListResponse> {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.limit != null) params.set("limit", String(filters.limit));
  if (filters.offset != null) params.set("offset", String(filters.offset));
  const res: AxiosResponse<BookingListResponse> = await apiClient.get(
    "/api/v1/bookings/my",
    { params },
  );
  return res.data;
}

export async function fetchActiveBookings(): Promise<BookingDetail[]> {
  const res: AxiosResponse<BookingDetail[]> = await apiClient.get(
    "/api/v1/bookings/active",
  );
  return res.data;
}

export async function fetchBookingHistory(
  filters: BookingHistoryFilters = {},
): Promise<BookingListResponse> {
  const params = new URLSearchParams();
  if (filters.coworking_id) params.set("coworking_id", filters.coworking_id);
  if (filters.coworking_name)
    params.set("coworking_name", filters.coworking_name);
  if (filters.student_id) params.set("student_id", filters.student_id);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  if (filters.limit != null) params.set("limit", String(filters.limit));
  if (filters.offset != null) params.set("offset", String(filters.offset));
  const res: AxiosResponse<BookingListResponse> = await apiClient.get(
    "/api/v1/bookings/history",
    { params },
  );
  return res.data;
}

export async function fetchBooking(id: string): Promise<BookingDetail> {
  const res: AxiosResponse<BookingDetail> = await apiClient.get(
    `/api/v1/bookings/${id}`,
  );
  return res.data;
}

export async function confirmBooking(id: string): Promise<Booking> {
  const res: AxiosResponse<Booking> = await apiClient.patch(
    `/api/v1/bookings/${id}/confirm`,
  );
  return res.data;
}

export async function closeBooking(id: string): Promise<Booking> {
  const res: AxiosResponse<Booking> = await apiClient.patch(
    `/api/v1/bookings/${id}/close`,
  );
  return res.data;
}

export async function cancelBooking(id: string): Promise<Booking> {
  const res: AxiosResponse<Booking> = await apiClient.patch(
    `/api/v1/bookings/${id}/cancel`,
  );
  return res.data;
}
