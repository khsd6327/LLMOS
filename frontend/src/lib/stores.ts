// ted-os-project/frontend/src/lib/stores.ts
// Svelte stores for state management
import { writable, readable, derived } from 'svelte/store';
import type { ChatSession, ChatMessage, UsageStats, FavoriteMessage } from './api';
import { DEFAULT_PROVIDER, DEFAULT_MODELS } from './models';

// 세션 관리
export const sessions = writable<ChatSession[]>([]);
export const currentSession = writable<ChatSession | null>(null);
export const currentSessionId = writable<string | null>(null);

// 채팅 상태
export const isGenerating = writable<boolean>(false);
export const streamingMessage = writable<string>('');

// 모델 설정
export const selectedProvider = writable<string>(DEFAULT_PROVIDER);
export const selectedModel = writable<string>(DEFAULT_MODELS[DEFAULT_PROVIDER]);
export const temperature = writable<number>(0.7);
export const maxTokens = writable<number>(4096);

// UI 상태
export const sidebarOpen = writable<boolean>(true);
export const settingsOpen = writable<boolean>(false);
export const currentPage = writable<'chat' | 'favorites' | 'settings' | 'usage'>('chat');

// 사용량 통계
export const usageStats = writable<UsageStats | null>(null);

// 즐겨찾기
export const favorites = writable<FavoriteMessage[]>([]);

// 검색 및 필터
export const searchQuery = writable<string>('');
export const selectedTags = writable<string[]>([]);

// 에러 및 알림
export const errorMessage = writable<string | null>(null);
export const successMessage = writable<string | null>(null);

// 테마 설정
export const theme = writable<'dark' | 'light'>('dark');

// 현재 선택된 모델의 전체 정보
export const currentModelInfo = derived(
  [selectedProvider, selectedModel],
  ([$selectedProvider, $selectedModel]) => {
    return { provider: $selectedProvider, model: $selectedModel };
  }
);

// 세션 통계
export const sessionStats = derived(sessions, ($sessions) => {
  const totalSessions = $sessions.length;
  const totalMessages = $sessions.reduce((sum, session) => sum + session.messages.length, 0);
  const pinnedSessions = $sessions.filter(session => session.is_pinned).length;
  
  return {
    totalSessions,
    totalMessages,
    pinnedSessions,
    averageMessages: totalSessions > 0 ? Math.round(totalMessages / totalSessions) : 0
  };
});

// 유틸리티 함수들
export function clearError() {
  errorMessage.set(null);
}

export function clearSuccess() {
  successMessage.set(null);
}

export function showError(message: string) {
  errorMessage.set(message);
  setTimeout(clearError, 5000); // 5초 후 자동 제거
}

export function showSuccess(message: string) {
  successMessage.set(message);
  setTimeout(clearSuccess, 3000); // 3초 후 자동 제거
}

// 로컬 스토리지 동기화
function createPersistedStore<T>(key: string, defaultValue: T) {
  const store = writable<T>(defaultValue);

  // 브라우저 환경에서만 실행
  if (typeof window !== 'undefined') {
    // 초기값 로드
    const stored = localStorage.getItem(key);
    if (stored) {
      try {
        store.set(JSON.parse(stored));
      } catch (e) {
        console.warn(`Failed to parse stored value for ${key}:`, e);
      }
    }

    // 변경사항 저장
    store.subscribe(value => {
      localStorage.setItem(key, JSON.stringify(value));
    });
  }

  return store;
}

// 영구 저장되는 설정들
export const persistedSettings = {
  selectedProvider: createPersistedStore('selectedProvider', DEFAULT_PROVIDER),
  selectedModel: createPersistedStore('selectedModel', DEFAULT_MODELS[DEFAULT_PROVIDER]),
  temperature: createPersistedStore('temperature', 0.7),
  maxTokens: createPersistedStore('maxTokens', 4096),
  sidebarOpen: createPersistedStore('sidebarOpen', true),
  theme: createPersistedStore('theme', 'dark' as 'dark' | 'light')
};

// 실시간 세션 시간 계산
export const sessionDuration = readable(0, function start(set) {
  const startTime = Date.now();
  
  const interval = setInterval(() => {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    set(elapsed);
  }, 1000);

  return function stop() {
    clearInterval(interval);
  };
});