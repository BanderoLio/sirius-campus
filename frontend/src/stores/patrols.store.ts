import { defineStore } from "pinia";
import { ref, computed } from "vue";
import type {
  Patrol,
  PatrolDetail,
  PatrolCreateRequest,
  PatrolEntryUpdateRequest,
  PatrolListFilters,
} from "@/types/patrols.types";
import * as patrolsApi from "@/api/patrols.api";

export const usePatrolsStore = defineStore("patrols", () => {
  const items = ref<Patrol[]>([]);
  const total = ref(0);
  const page = ref(1);
  const size = ref(20);
  const pages = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const currentDetail = ref<PatrolDetail | null>(null);

  const inProgressCount = computed(() =>
    items.value.filter((p) => p.status === "in_progress").length
  );

  const completedCount = computed(() =>
    items.value.filter((p) => p.status === "completed").length
  );

  async function fetchList(filters: PatrolListFilters = {}) {
    loading.value = true;
    error.value = null;
    try {
      const result = await patrolsApi.fetchPatrols({
        page: filters.page ?? page.value,
        size: filters.size ?? size.value,
        date: filters.date,
        building: filters.building,
        entrance: filters.entrance,
        status: filters.status,
      });
      items.value = result.items;
      total.value = result.total;
      page.value = result.page;
      size.value = result.size;
      pages.value = result.pages;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка загрузки обходов";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchOne(id: string) {
    loading.value = true;
    error.value = null;
    try {
      currentDetail.value = await patrolsApi.fetchPatrol(id);
      return currentDetail.value;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка загрузки обхода";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function create(data: PatrolCreateRequest): Promise<PatrolDetail> {
    loading.value = true;
    error.value = null;
    try {
      const created = await patrolsApi.createPatrol(data);
      items.value = [created, ...items.value];
      return created;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка создания обхода";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function complete(id: string): Promise<PatrolDetail> {
    loading.value = true;
    error.value = null;
    try {
      const updated = await patrolsApi.completePatrol(id);
      const idx = items.value.findIndex((p) => p.patrol_id === id);
      if (idx >= 0) items.value[idx] = updated;
      if (currentDetail.value?.patrol_id === id) {
        currentDetail.value = { ...currentDetail.value, ...updated };
      }
      return updated;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка завершения обхода";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function remove(id: string) {
    loading.value = true;
    error.value = null;
    try {
      await patrolsApi.deletePatrol(id);
      items.value = items.value.filter((p) => p.patrol_id !== id);
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка удаления обхода";
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function updateEntry(
    patrolId: string,
    entryId: string,
    data: PatrolEntryUpdateRequest
  ) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await patrolsApi.updatePatrolEntry(patrolId, entryId, data);
      if (currentDetail.value?.patrol_id === patrolId && currentDetail.value.entries) {
        const idx = currentDetail.value.entries.findIndex(
          (e) => e.patrol_entry_id === entryId
        );
        if (idx >= 0) {
          currentDetail.value.entries[idx] = updated;
        }
      }
      return updated;
    } catch (e) {
      error.value = e instanceof Error ? e.message : "Ошибка обновления записи";
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
    inProgressCount,
    completedCount,
    fetchList,
    fetchOne,
    create,
    complete,
    remove,
    updateEntry,
    $reset,
  };
});
