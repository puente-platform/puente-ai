import { auth } from "./firebase";

const BASE_URL =
  import.meta.env.VITE_API_URL ??
  "https://puente-backend-519686233522.us-central1.run.app/api/v1";

export interface UploadResponse {
  document_id: string;
  [key: string]: unknown;
}

export interface AnalyzeResponse {
  document_id: string;
  status?: string;
  message?: string;
  extraction?: {
    document_type?: string;
    extracted_at?: string;
    raw_text?: string;
    fields?: Record<string, unknown>;
    line_items?: Array<{
      description?: string;
      quantity?: string;
      unit_of_measure?: string;
      unit_price?: string;
      amount?: string | number;
      hs_code_candidate?: string;
      needs_hs_classification?: boolean;
    }>;
    line_item_count?: number;
    extraction_summary?: Record<string, unknown>;
  };
  analysis?: {
    fraud_assessment?: {
      score?: number;
      risk_level?: string;
      flags?: string[];
      explanation?: string;
    };
    compliance_assessment?: {
      level?: string;
      missing_documents?: string[];
      flags?: string[];
      corridor?: string;
      explanation?: string;
    };
    routing_recommendation?: {
      recommended_method?: string;
      traditional_cost_usd?: number;
      traditional_days?: number;
      puente_cost_usd?: number;
      puente_days?: number;
      savings_usd?: number;
      explanation?: string;
    };
    hs_classifications?: Array<{
      description?: string;
      suggested_hs_code?: string;
      confidence?: string;
      duty_rate_estimate?: string;
    }>;
    analyzed_at?: string;
  };
  [key: string]: unknown;
}

export interface RoutingOption {
  provider: string;
  fee: number;
  delivery_time?: string;
  recommended?: boolean;
  [key: string]: unknown;
}

export interface RoutingResponse {
  document_id: string;
  recommended_route?: RoutingOption;
  routes?: RoutingOption[];
  savings?: number;
  [key: string]: unknown;
}

export interface ComplianceResponse {
  document_id: string;
  status?: string;
  [key: string]: unknown;
}

export interface OnboardingProfileIn {
  displayName?: string | null;
  company?: string | null;
  corridors?: string[] | null;
  markComplete?: boolean;
}

export interface OnboardingProfileOut {
  displayName: string | null;
  company: string | null;
  corridors: string[] | null;
  completedAt: string | null;
  createdAt: string;
  updatedAt: string;
}

export async function authedFetch(path: string, init: RequestInit = {}) {
  const user = auth.currentUser;
  if (!user) throw new Error("Not authenticated");
  const token = await user.getIdToken();
  const headers = new Headers(init.headers);
  headers.set("Authorization", `Bearer ${token}`);
  if (
    init.body &&
    !(init.body instanceof FormData) &&
    !headers.has("Content-Type")
  ) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`${BASE_URL}${path}`, { ...init, headers });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`HTTP ${res.status}: ${body || res.statusText}`);
  }
  return res.json();
}

export async function uploadDocument(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return authedFetch("/upload", { method: "POST", body: formData });
}

export async function analyzeDocument(documentId: string): Promise<AnalyzeResponse> {
  return authedFetch("/analyze", {
    method: "POST",
    body: JSON.stringify({ document_id: documentId }),
  });
}

export async function routeDocument(documentId: string, amount?: number): Promise<RoutingResponse> {
  return authedFetch("/routing", {
    method: "POST",
    body: JSON.stringify(
      amount != null
        ? { document_id: documentId, transaction_amount: amount }
        : { document_id: documentId }
    ),
  });
}

export async function complianceDocument(documentId: string): Promise<ComplianceResponse> {
  return authedFetch("/compliance", {
    method: "POST",
    body: JSON.stringify({ document_id: documentId }),
  });
}

// Returns null on 404 (no profile yet); rethrows other errors.
// authedFetch throws on any non-2xx, so we catch and inspect the message.
export async function getOnboarding(): Promise<OnboardingProfileOut | null> {
  try {
    return await authedFetch("/onboarding", { method: "GET" });
  } catch (err) {
    const msg = err instanceof Error ? err.message : "";
    if (msg.startsWith("HTTP 404")) return null;
    throw err;
  }
}

export async function saveOnboarding(
  data: OnboardingProfileIn,
): Promise<OnboardingProfileOut> {
  return authedFetch("/onboarding", {
    method: "POST",
    body: JSON.stringify(data),
  });
}
