import type {
  Application,
  ApplicationDetail,
  ApplicationCreateRequest,
  ApplicationDecideRequest,
  ApplicationListFilters,
  PaginatedResponse,
} from "@/types/applications.types";
import type { AxiosResponse } from "axios";
import apiClient from "./client";

export async function fetchApplications(
  filters: ApplicationListFilters = {}
): Promise<PaginatedResponse<Application>> {
  const params = new URLSearchParams();
  if (filters.page != null) params.set("page", String(filters.page));
  if (filters.size != null) params.set("size", String(filters.size));
  if (filters.status) params.set("status", filters.status);
  if (filters.date_from) params.set("date_from", filters.date_from);
  if (filters.date_to) params.set("date_to", filters.date_to);
  const res: AxiosResponse<PaginatedResponse<Application>> = await apiClient.get(
    "/api/v1/applications",
    { params }
  );
  return res.data;
}

export async function fetchApplication(id: string): Promise<ApplicationDetail> {
  const res: AxiosResponse<ApplicationDetail> = await apiClient.get(
    `/api/v1/applications/${id}`
  );
  return res.data;
}

export async function createApplication(
  data: ApplicationCreateRequest
): Promise<Application> {
  const res: AxiosResponse<Application> = await apiClient.post(
    "/api/v1/applications",
    data
  );
  return res.data;
}

export async function decideApplication(
  id: string,
  data: ApplicationDecideRequest
): Promise<Application> {
  const res: AxiosResponse<Application> = await apiClient.patch(
    `/api/v1/applications/${id}`,
    data
  );
  return res.data;
}

export async function uploadDocument(
  applicationId: string,
  documentType: string,
  file: File
): Promise<{ id: string; application_id: string; document_type: string; file_url: string; uploaded_by: string; created_at: string }> {
  const form = new FormData();
  form.append("document_type", documentType);
  form.append("file", file);
  const res = await apiClient.post(
    `/api/v1/applications/${applicationId}/documents`,
    form,
    {
      headers: { "Content-Type": "multipart/form-data" },
    }
  );
  return res.data;
}
