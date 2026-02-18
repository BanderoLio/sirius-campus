import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type {
  Application,
  ApplicationDetail,
  ApplicationCreateRequest,
  ApplicationDecideRequest,
  ApplicationListFilters,
} from "@/types/applications.types";
import * as applicationsApi from "@/api/applications.api";

export const useApplicationsStore = defineStore("applications", () => {
  const items = ref<Application[]>([]);
  const total = ref(0);
  const page = ref(1);
  const size = ref(20);
  const pages = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentDetail = ref<ApplicationDetail | null>(null);

  const pendingCount = computed(() =>
    items.value.filter((a) => a.status === "pending").length
  );

  async function fetchList(filters: ApplicationListFilters = {}) {
    loading.value = true;
    error.value = null;
    try {
      const result = await applicationsApi.fetchApplications({
        page: filters.page ?? page.value,
        size: filters.size ?? size.value,
        status: filters.status,
        date_from: filters.date_from,
        date_to: filters.date_to,
      });
      items.value = result.items;
      total.value = result.total;
      page.value = result.page;
      size.value = result.size;
      pages.value = result.pages;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка загрузки заявлений";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchOne(id: string) {
    loading.value = true;
    error.value = null;
    try {
      currentDetail.value = await applicationsApi.fetchApplication(id);
      return currentDetail.value;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка загрузки заявления";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function create(data: ApplicationCreateRequest): Promise<Application> {
    loading.value = true;
    error.value = null;
    try {
      const created = await applicationsApi.createApplication(data);
      items.value = [created, ...items.value];
      return created;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка создания заявления";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function decide(
    id: string,
    data: ApplicationDecideRequest
  ): Promise<Application> {
    loading.value = true;
    error.value = null;
    try {
      const updated = await applicationsApi.decideApplication(id, data);
      const idx = items.value.findIndex((a) => a.id === id);
      if (idx >= 0) items.value[idx] = updated;
      if (currentDetail.value?.id === id) {
        currentDetail.value = { ...currentDetail.value, ...updated };
      }
      return updated;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Ошибка при принятии решения";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function uploadDoc(
    applicationId: string,
    documentType: string,
    file: File
  ) {
    loading.value = true;
    error.value = null;
    try {
      const doc = await applicationsApi.uploadDocument(
        applicationId,
        documentType,
        file
      );
      if (currentDetail.value?.id === applicationId) {
        currentDetail.value.documents = [
          ...(currentDetail.value.documents || []),
          doc as ApplicationDetail["documents"][0],
        ];
      }
      return doc;
    } catch (e) {
      error.value =
        e instanceof Error ? e.message : "Ошибка загрузки документа";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function $reset() {
    items.value = [];
    total.value = 0;
    page.value = 1;
    size.value = 20;
    pages.value = 0;
    loading.value = false;
    error.value = null;
    currentDetail.value = null;
  }

  return {
    items,
    total,
    page,
    size,
    pages,
    loading,
    error,
    currentDetail,
    pendingCount,
    fetchList,
    fetchOne,
    create,
    decide,
    uploadDoc,
    $reset,
  };
});
