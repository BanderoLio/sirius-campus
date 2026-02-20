import { format, parseISO } from "date-fns";
import { ru } from "date-fns/locale";

export function formatDate(isoDate: string): string {
  return format(parseISO(isoDate), "dd.MM.yyyy", { locale: ru });
}

export function formatDateTime(isoDate: string): string {
  return format(parseISO(isoDate), "dd.MM.yyyy HH:mm", { locale: ru });
}

export function formatTime(isoDate: string): string {
  return format(parseISO(isoDate), "HH:mm", { locale: ru });
}
