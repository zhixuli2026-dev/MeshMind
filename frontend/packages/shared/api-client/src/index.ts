const BASE = '/api/v1';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('meshmind_token');
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, { ...options, headers: { ...headers, ...options?.headers } });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ message: res.statusText }));
    throw new Error(err.error?.message || err.message || 'Request failed');
  }
  return res.json();
}

// Workspace
export const createWorkspace = (name: string, description?: string) =>
  request<{ workspace_id: string; api_key: string }>('/workspaces', { method: 'POST', body: JSON.stringify({ name, description }) });

export const getWorkspace = (id: string) => request<any>(`/workspaces/${id}`);
export const getWorkspaceStats = (id: string) => request<any>(`/workspaces/${id}/stats`);

// Auth
export const login = (workspace_id: string, user_id: string) =>
  request<{ access_token: string; workspace_id: string }>('/auth/login', { method: 'POST', body: JSON.stringify({ workspace_id, user_id }) });

// Search
export const search = (workspace_id: string, q: string, limit = 20) =>
  request<any>(`/workspaces/${workspace_id}/search?q=${encodeURIComponent(q)}&limit=${limit}`);

// Nodes
export const getNode = (workspace_id: string, node_id: string) =>
  request<any>(`/workspaces/${workspace_id}/nodes/${node_id}`);
export const getRelated = (workspace_id: string, node_id: string) =>
  request<any>(`/workspaces/${workspace_id}/nodes/${node_id}/related`);
export const getNodeDocuments = (workspace_id: string, node_id: string) =>
  request<any>(`/workspaces/${workspace_id}/nodes/${node_id}/documents`);

// Extract
export const extractFromConversation = (workspace_id: string, messages: any[], user_id: string, session_id: string) =>
  request<any>(`/workspaces/${workspace_id}/extract/conversation`, { method: 'POST', body: JSON.stringify({ messages, user_id, session_id }) });

export const extractFromDocument = (workspace_id: string, content: string, title: string, user_id: string) =>
  request<any>(`/workspaces/${workspace_id}/extract/document`, { method: 'POST', body: JSON.stringify({ content, title, user_id }) });
