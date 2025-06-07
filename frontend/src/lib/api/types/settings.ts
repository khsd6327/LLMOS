// 설정 관련 타입 정의

export interface AppSettings {
    api_keys: Record<string, string>;
    paths: {
      chat_sessions: string;
      artifacts: string;
      usage_tracking: string;
      favorites: string;
    };
    defaults: {
      models_by_provider: Record<string, string>;
      temperature: number;
      max_tokens: number;
    };
    ui: {
      selected_provider: string;
      theme: 'light' | 'dark' | 'auto';
      language: 'ko' | 'en';
    };
  }
  
  export interface SettingsUpdateRequest {
    updates: Record<string, any>;
  }
  
  export interface SettingsResponse {
    settings: AppSettings;
    message: string;
  }
  
  // 설정 모달 상태
  export interface SettingsModalState {
    isOpen: boolean;
    currentTab: 'models' | 'api-keys' | 'interface' | 'advanced';
    isLoading: boolean;
    isSaving: boolean;
    error: string | null;
  }
