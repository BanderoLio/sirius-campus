import { defineStore } from "pinia";
import { ref } from "vue";
import type {
  Coworking,
  BookingDetail,
  BookingCreateRequest,
  BookingListFilters,
  BookingHistoryFilters,
  CoworkingListFilters,
} from "@/types/coworkings.types";
import * as api from "@/api/coworkings.api";
import { ERROR_MESSAGES } from "@/constants/errorCodes";
import axios from "axios";

interface ErrorResponseBody {
  error?: { code?: string; message?: string };
}

function extractErrorMessage(e: unknown): string {
  if (axios.isAxiosError(e)) {
    const body = e.response?.data as ErrorResponseBody | undefined;
    const code = body?.error?.code;
    if (code && ERROR_MESSAGES[code]) return ERROR_MESSAGES[code];
    if (body?.error?.message) return body.error.message;
  }
  if (e instanceof Error) return e.message;
  return "Произошла ошибка";
}

export const useCoworkingsStore = defineStore("coworkings", () => {
  const coworkings = ref<Coworking[]>([]);
  const bookings = ref<BookingDetail[]>([]);
  const activeBookings = ref<BookingDetail[]>([]);
  const currentBooking = ref<BookingDetail | null>(null);
  const total = ref(0);
  const limit = ref(20);
  const offset = ref(0);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchCoworkings(filters: CoworkingListFilters = {}) {
    loading.value = true;
    error.value = null;
    try {
      coworkings.value = await api.fetchCoworkings(filters);
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function createBooking(
    data: BookingCreateRequest,
  ): Promise<ReturnType<typeof api.createBooking>> {
    loading.value = true;
    error.value = null;
    try {
      return await api.createBooking(data);
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchMyBookings(
    filters: { status?: string; limit?: number; offset?: number } = {},
  ) {
    loading.value = true;
    error.value = null;
    try {
      const result = await api.fetchMyBookings(filters);
      bookings.value = result.items;
      total.value = result.total;
      limit.value = result.limit;
      offset.value = result.offset;
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchBookings(filters: BookingListFilters = {}) {
    loading.value = true;
    error.value = null;
    try {
      const result = await api.fetchBookings(filters);
      bookings.value = result.items;
      total.value = result.total;
      limit.value = result.limit;
      offset.value = result.offset;
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchActiveBookings() {
    loading.value = true;
    error.value = null;
    try {
      activeBookings.value = await api.fetchActiveBookings();
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchBookingHistory(filters: BookingHistoryFilters = {}) {
    loading.value = true;
    error.value = null;
    try {
      const result = await api.fetchBookingHistory(filters);
      bookings.value = result.items;
      total.value = result.total;
      limit.value = result.limit;
      offset.value = result.offset;
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function fetchBooking(id: string) {
    loading.value = true;
    error.value = null;
    try {
      currentBooking.value = await api.fetchBooking(id);
      return currentBooking.value;
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function confirmBooking(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await api.confirmBooking(id);
      if (currentBooking.value?.id === id) {
        currentBooking.value = { ...currentBooking.value, ...updated };
      }
      return updated;
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function closeBooking(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await api.closeBooking(id);
      if (currentBooking.value?.id === id) {
        currentBooking.value = { ...currentBooking.value, ...updated };
      }
      return updated;
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  async function cancelBooking(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await api.cancelBooking(id);
      if (currentBooking.value?.id === id) {
        currentBooking.value = { ...currentBooking.value, ...updated };
      }
      return updated;
    } catch (e) {
      error.value = extractErrorMessage(e);
      throw e;
    } finally {
      loading.value = false;
    }
  }

  function $reset() {
    coworkings.value = [];
    bookings.value = [];
    activeBookings.value = [];
    currentBooking.value = null;
    total.value = 0;
    limit.value = 20;
    offset.value = 0;
    loading.value = false;
    error.value = null;
  }

  return {
    coworkings,
    bookings,
    activeBookings,
    currentBooking,
    total,
    limit,
    offset,
    loading,
    error,
    fetchCoworkings,
    createBooking,
    fetchMyBookings,
    fetchBookings,
    fetchActiveBookings,
    fetchBookingHistory,
    fetchBooking,
    confirmBooking,
    closeBooking,
    cancelBooking,
    $reset,
  };
});
