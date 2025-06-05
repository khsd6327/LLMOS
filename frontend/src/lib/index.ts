// 중앙 export 파일 - $lib alias로 import 가능한 모든 모듈들

// API 클라이언트
export { api } from './api';
export type { 
  ChatSession, 
  ChatMessage, 
  ModelConfig, 
  ModelsData, 
  UsageStats, 
  FavoriteMessage 
} from './api';

// 상태 관리 스토어
export {
  sessions,
  currentSession,
  currentSessionId,
  isGenerating,
  streamingMessage,
  selectedProvider,
  selectedModel,
  temperature,
  maxTokens,
  sidebarOpen,
  settingsOpen,
  currentPage,
  usageStats,
  favorites,
  searchQuery,
  selectedTags,
  errorMessage,
  successMessage,
  theme,
  currentModelInfo,
  sessionStats,
  persistedSettings,
  sessionDuration,
  clearError,
  clearSuccess,
  showError,
  showSuccess
} from './stores';

// 모델 설정 및 유틸리티
export {
  MODELS_DATA,
  DEFAULT_MODELS,
  DEFAULT_PROVIDER,
  getAllProviders,
  getModelsForProvider,
  getModelConfig,
  getDefaultModelForProvider,
  formatCost,
  formatTokens
} from './models';

// 유틸리티 함수들
export * from './utils';

// === 새로운 폴더 구조 컴포넌트들 ===

// 🎨 UI 컴포넌트들
export { default as ErrorToast } from './components/ui/ErrorToast.svelte';
export { default as SuccessToast } from './components/ui/SuccessToast.svelte';
export { default as LoadingSpinner } from './components/ui/LoadingSpinner.svelte';
export { default as ProgressBar } from './components/ui/ProgressBar.svelte';
export { default as StatusIndicator } from './components/ui/StatusIndicator.svelte';
export { default as ConfirmDialog } from './components/ui/ConfirmDialog.svelte';

// 💬 채팅 컴포넌트들
export { default as ChatPage } from './components/chat/ChatPage.svelte';
export { default as ChatHeader } from './components/chat/ChatHeader.svelte';
export { default as ChatInput } from './components/chat/ChatInput.svelte';
export { default as MessageList } from './components/chat/MessageList.svelte';
export { default as MessageItem } from './components/chat/MessageItem.svelte';
export { default as TypingIndicator } from './components/chat/TypingIndicator.svelte';
export { default as WelcomeScreen } from './components/chat/WelcomeScreen.svelte';
export { default as StopButton } from './components/chat/StopButton.svelte';

// 📄 페이지 컴포넌트들
export { default as FavoritesPage } from './components/pages/FavoritesPage.svelte';
export { default as SettingsPage } from './components/pages/SettingsPage.svelte';
export { default as UsagePage } from './components/pages/UsagePage.svelte';

// 🏗️ 레이아웃 컴포넌트들
export { default as Sidebar } from './components/layout/Sidebar.svelte';
export { default as PageRouter } from './components/layout/PageRouter.svelte';

// 🤖 AI 관련 컴포넌트들
export { default as ModelSelector } from './components/ai/ModelSelector.svelte';
export { default as SessionUsageStats } from './components/ai/SessionUsageStats.svelte';
export { default as ProviderStatus } from './components/ai/ProviderStatus.svelte';
export { default as UsageTrends } from './components/ai/UsageTrends.svelte';