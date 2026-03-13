export const COWORKING_NOT_FOUND = "COWORKING_NOT_FOUND" as const;
export const BOOKING_NOT_FOUND = "BOOKING_NOT_FOUND" as const;
export const COWORKING_NOT_AVAILABLE = "COWORKING_NOT_AVAILABLE" as const;
export const BOOKING_INVALID_STATUS_TRANSITION =
  "BOOKING_INVALID_STATUS_TRANSITION" as const;
export const BOOKING_ACCESS_DENIED = "BOOKING_ACCESS_DENIED" as const;
export const STUDENT_ALREADY_HAS_ACTIVE_BOOKING =
  "STUDENT_ALREADY_HAS_ACTIVE_BOOKING" as const;

export type CoworkingErrorCode =
  | typeof COWORKING_NOT_FOUND
  | typeof BOOKING_NOT_FOUND
  | typeof COWORKING_NOT_AVAILABLE
  | typeof BOOKING_INVALID_STATUS_TRANSITION
  | typeof BOOKING_ACCESS_DENIED
  | typeof STUDENT_ALREADY_HAS_ACTIVE_BOOKING;

export const ERROR_MESSAGES: Record<string, string> = {
  [COWORKING_NOT_FOUND]: "Коворкинг не найден",
  [BOOKING_NOT_FOUND]: "Бронирование не найдено",
  [COWORKING_NOT_AVAILABLE]: "Коворкинг недоступен для бронирования",
  [BOOKING_INVALID_STATUS_TRANSITION]: "Некорректный переход статуса бронирования",
  [BOOKING_ACCESS_DENIED]: "Нет доступа к данному бронированию",
  [STUDENT_ALREADY_HAS_ACTIVE_BOOKING]:
    "У вас уже есть активное или ожидающее бронирование",
  UNAUTHORIZED: "Необходимо авторизоваться",
  FORBIDDEN: "Недостаточно прав",
};
