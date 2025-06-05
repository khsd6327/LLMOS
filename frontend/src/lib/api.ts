// ted-os-project/frontend/src/lib/api.ts
// API 클라이언트 - FastAPI 백엔드와 통신
const API_BASE = '/api';

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  created_at: string;
  updated_at: string;
  metadata: Record<string, any>;
  is_pinned?: boolean;
}

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string | any[];
  model_provider?: string;
  model_name?: string;
  model_display_name?: string;
  timestamp?: string;
  type?: string;
}

export interface ModelConfig {
  provider: string;
  model_name: string;
  display_name: string;
  max_tokens: number;
  supports_streaming: boolean;
  supports_functions: boolean;
  supports_vision: boolean;
  description: string;
  input_cost_per_1k: number;
  output_cost_per_1k: number;
}

export interface ModelsData {
  [providerName: string]: {
    provider: string;
    models: {
      [modelKey: string]: ModelConfig;
    };
  };
}

export interface UsageStats {
  total_usage: {
    total_tokens: number;
    total_cost: number;
    total_requests: number;
  };
  today_usage: {
    total_tokens: number;
    total_cost: number;
    total_requests: number;
  };
  weekly_usage: {
    total_tokens: number;
    total_cost: number;
    total_requests: number;
    period: string;
  };
  monthly_usage: {
    total_tokens: number;
    total_cost: number;
    total_requests: number;
    period: string;
  };
  usage_by_model: Record<string, {
    tokens: number;
    cost: number;
    requests: number;
  }>;
  usage_trends: Array<{
    date: string;
    tokens: number;
    cost: number;
    requests: number;
  }>;
  estimated_monthly_cost: number;
}

export interface FavoriteMessage {
  id: string;
  session_id: string;
  message_id: string;
  role: string;
  content: string;
  favorited_at: string;
  created_at: string;
  model_provider?: string;
  model_name?: string;
  context_messages?: ChatMessage[];
  tags: string[];
  notes?: string;
}

class ApiClient {
  // 세션 관리
  async getSessions(): Promise<ChatSession[]> {
    const response = await fetch(`${API_BASE}/sessions`);
    if (!response.ok) throw new Error('세션 목록을 가져올 수 없습니다');
    return response.json();
  }

  async createSession(title?: string): Promise<ChatSession> {
    const response = await fetch(`${API_BASE}/sessions`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ title })
    });
    if (!response.ok) throw new Error('세션을 생성할 수 없습니다');
    const data = await response.json();
    return data.session;
  }

  async deleteSession(sessionId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('세션을 삭제할 수 없습니다');
  }

  async updateSession(sessionId: string, updates: { title?: string; is_pinned?: boolean }): Promise<ChatSession> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    if (!response.ok) throw new Error('세션을 업데이트할 수 없습니다');
    const data = await response.json();
    return data.session;
  }

  // 채팅 메시지 전송 (스트리밍)
  async *sendMessage(sessionId: string, prompt: string, modelProvider?: string, modelName?: string): AsyncGenerator<string, void, unknown> {
    const response = await fetch(`${API_BASE}/sessions/${sessionId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        prompt,
        model_provider: modelProvider,
        model_name: modelName
      })
    });

    if (!response.ok) throw new Error('메시지를 전송할 수 없습니다');

    const reader = response.body?.getReader();
    if (!reader) throw new Error('스트리밍을 지원하지 않습니다');

    const decoder = new TextDecoder();
    let buffer = '';

    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6).trim();
            if (data === '[DONE]') return;
            if (data) yield data;
          }
        }
      }
    } finally {
      reader.releaseLock();
    }
  }

  // 사용량 통계
  async getUsageStats(): Promise<UsageStats> {
    const response = await fetch(`${API_BASE}/status/usage`);
    if (!response.ok) throw new Error('사용량 통계를 가져올 수 없습니다');
    return response.json();
  }

  // 즐겨찾기 관리
  async getFavorites(query?: string, tags?: string): Promise<FavoriteMessage[]> {
    const params = new URLSearchParams();
    if (query) params.set('query', query);
    if (tags) params.set('tags', tags);
    
    const response = await fetch(`${API_BASE}/favorites?${params}`);
    if (!response.ok) throw new Error('즐겨찾기를 가져올 수 없습니다');
    return response.json();
  }

  async createFavorite(favorite: Omit<FavoriteMessage, 'id' | 'favorited_at'>): Promise<FavoriteMessage> {
    const response = await fetch(`${API_BASE}/favorites`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(favorite)
    });
    if (!response.ok) throw new Error('즐겨찾기를 추가할 수 없습니다');
    return response.json();
  }

  async updateFavorite(favoriteId: string, updates: { tags?: string[]; notes?: string }): Promise<FavoriteMessage> {
    const response = await fetch(`${API_BASE}/favorites/${favoriteId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updates)
    });
    if (!response.ok) throw new Error('즐겨찾기를 업데이트할 수 없습니다');
    return response.json();
  }

  async deleteFavorite(favoriteId: string): Promise<void> {
    const response = await fetch(`${API_BASE}/favorites/${favoriteId}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('즐겨찾기를 삭제할 수 없습니다');
  }

  // 설정 관리
  async getSettings(): Promise<Record<string, any>> {
    const response = await fetch(`${API_BASE}/settings`);
    if (!response.ok) throw new Error('설정을 가져올 수 없습니다');
    const data = await response.json();
    return data.settings;
  }

  async updateSettings(updates: Record<string, any>): Promise<Record<string, any>> {
    const response = await fetch(`${API_BASE}/settings`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ updates })
    });
    if (!response.ok) throw new Error('설정을 업데이트할 수 없습니다');
    const data = await response.json();
    return data.settings;
  }
}

export const api = new ApiClient();