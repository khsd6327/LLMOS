// ted-os-project/frontend/src/lib/api/types/index.ts
// 채팅 세션 타입
export interface ChatSession {
    id: string;
    title: string;
    created_at: string;
    updated_at: string;
    is_pinned: boolean;
    messages: ChatMessage[];
  }
  
  // 채팅 메시지 타입  
  export interface ChatMessage {
    role: 'user' | 'assistant';
    content: string;
    timestamp?: string;
  }
  
  // 모델 정보 타입
  export interface ModelInfo {
    id: string;
    provider: string;
    model: string;
    display: string;
  }
  
  // API 응답 타입들
  export interface SessionResponse {
    session: ChatSession;
    message: string;
  }
  
  export interface ApiError {
    detail: string;
    status?: number;
  }