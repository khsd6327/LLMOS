import { writable, derived } from 'svelte/store';
import type { AppSettings, SettingsModalState } from '../../types/settings.js';

// 설정 데이터 스토어
export const settings = writable<AppSettings | null>(null);

// 설정 모달 상태 스토어
export const settingsModal = writable<SettingsModalState>({
  isOpen: false,
  currentTab: 'models',
  isLoading: false,
  isSaving: false,
  error: null
});

// 설정 로딩 상태
export const isSettingsLoaded = derived(settings, ($settings) => $settings !== null);

// 모달 제어 함수들
export const settingsModalActions = {
  open: () => {
    settingsModal.update(state => ({ ...state, isOpen: true, error: null }));
  },
  
  close: () => {
    settingsModal.update(state => ({ 
      ...state, 
      isOpen: false, 
      currentTab: 'models',
      error: null 
    }));
  },
  
  setTab: (tab: SettingsModalState['currentTab']) => {
    settingsModal.update(state => ({ ...state, currentTab: tab }));
  },
  
  setLoading: (loading: boolean) => {
    settingsModal.update(state => ({ ...state, isLoading: loading }));
  },
  
  setSaving: (saving: boolean) => {
    settingsModal.update(state => ({ ...state, isSaving: saving }));
  },
  
  setError: (error: string | null) => {
    settingsModal.update(state => ({ ...state, error }));
  }
};

// 설정 데이터 업데이트 함수
export const updateSettings = (newSettings: AppSettings) => {
  settings.set(newSettings);
};
