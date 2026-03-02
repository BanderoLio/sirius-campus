import type {
  Patrol,
  PatrolDetail,
  PatrolEntry,
  PatrolCreateRequest,
  PatrolEntryUpdateRequest,
  PatrolListFilters,
  PaginatedResponse,
} from "@/types/patrols.types";
import type { AxiosResponse } from "axios";
import apiClient from "./client";

/**
 * Fetches a list of patrols with optional filters
 */
export async function fetchPatrols(
  filters: PatrolListFilters = {}
): Promise<PaginatedResponse<Patrol>> {
  const params = new URLSearchParams();
  if (filters.page != null) params.set("page", String(filters.page));
  if (filters.size != null) params.set("size", String(filters.size));
  if (filters.date) params.set("date", filters.date);
  if (filters.building) params.set("building", filters.building);
  if (filters.entrance != null) params.set("entrance", String(filters.entrance));
  if (filters.status) params.set("status", filters.status);

  const res: AxiosResponse<PaginatedResponse<Patrol>> = await apiClient.get(
    "/api/v1/patrols",
    { params }
  );
  return res.data;
}

/**
 * Fetches a single patrol by ID with all entries
 */
export async function fetchPatrol(id: string): Promise<PatrolDetail> {
  const res: AxiosResponse<PatrolDetail> = await apiClient.get(
    `/api/v1/patrols/${id}`
  );
  return res.data;
}

/**
 * Creates a new patrol session
 */
export async function createPatrol(
  data: PatrolCreateRequest
): Promise<PatrolDetail> {
  const res: AxiosResponse<PatrolDetail> = await apiClient.post(
    "/api/v1/patrols",
    data
  );
  return res.data;
}

/**
 * Completes a patrol session
 */
export async function completePatrol(id: string): Promise<PatrolDetail> {
  const res: AxiosResponse<PatrolDetail> = await apiClient.patch(
    `/api/v1/patrols/${id}`,
    { status: "completed" }
  );
  return res.data;
}

/**
 * Deletes a patrol session
 */
export async function deletePatrol(id: string): Promise<void> {
  await apiClient.delete(`/api/v1/patrols/${id}`);
}

/**
 * Updates a patrol entry (student presence check)
 */
export async function updatePatrolEntry(
  patrolId: string,
  entryId: string,
  data: PatrolEntryUpdateRequest
): Promise<PatrolEntry> {
  const res: AxiosResponse<PatrolEntry> = await apiClient.patch(
    `/api/v1/patrols/${patrolId}/${entryId}`,
    data
  );
  return res.data;
}
