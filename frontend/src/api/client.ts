import axios from "axios";
import { v4 as uuidv4 } from "uuid";

interface WindowWithTrace {
  __traceId?: string;
  __correlationId?: string;
}

const getTraceId = (): string => {
  const w = window as unknown as WindowWithTrace;
  if (!w.__traceId) w.__traceId = uuidv4();
  return w.__traceId;
};

const getCorrelationId = (): string => {
  const w = window as unknown as WindowWithTrace;
  if (!w.__correlationId) w.__correlationId = uuidv4();
  return w.__correlationId;
};

const apiClient = axios.create({
  baseURL:
    (import.meta as unknown as { env: { VITE_API_BASE_URL?: string } }).env
      ?.VITE_API_BASE_URL ?? "",
  timeout: 15000,
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  config.headers["X-Trace-ID"] = getTraceId();
  config.headers["X-Correlation-ID"] = getCorrelationId();
  return config;
});

apiClient.interceptors.response.use(
  (response) => {
    const traceId = response.headers["x-trace-id"];
    if (traceId) {
      (window as unknown as WindowWithTrace).__traceId = traceId;
    }
    return response;
  },
  (error) => {
    const traceId = error.response?.headers["x-trace-id"];
    if (traceId) {
      (window as unknown as WindowWithTrace).__traceId = traceId;
    }
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export default apiClient;
