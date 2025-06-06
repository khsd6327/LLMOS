// ted-os-project/frontend/src/lib/stores/chat/index.ts
import { writable, get } from 'svelte/store';
import { api, type ChatSession, type ChatMessage } from '$lib/api/clients/main';

// 채팅 세션들
export const sessions = writable<ChatSession[]>([]);

// 현재 활성 세션
export const currentSession = writable<ChatSession | null>(null);

// 현재 선택된 모델
export const selectedModel = writable({
    id: 'claude-sonnet-4-20250514',
    provider: 'Anthropic',
    model: '4 Sonnet',
    display: 'Claude 4 Sonnet'
  });

// 로딩 상태
export const isLoading = writable(false);

// 에러 상태
export const error = writable<string | null>(null);

// 채팅 세션 관리 함수들
export const chatStore = {
  // 모든 세션 로드
  async loadSessions() {
    try {
      isLoading.set(true);
      error.set(null);
      
      const sessionList = await api.getSessions();
      sessions.set(sessionList);
      
      console.log('세션 로드 완료:', sessionList.length);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '세션을 불러오는데 실패했습니다';
      error.set(errorMessage);
      console.error('세션 로드 오류:', err);
    } finally {
      isLoading.set(false);
    }
  },
  
  // 새 세션 생성
  async createSession(title?: string) {
    try {
      isLoading.set(true);
      error.set(null);
      
      const newSession = await api.createSession(title);
      
      // 세션 목록에 추가
      sessions.update(list => [newSession, ...list]);
      
      // 새 세션을 활성 세션으로 설정
      currentSession.set(newSession);
      
      console.log('새 세션 생성:', newSession);
      return newSession;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '세션 생성에 실패했습니다';
      error.set(errorMessage);
      console.error('세션 생성 오류:', err);
      throw err;
    } finally {
      isLoading.set(false);
    }
  },
  
  // 세션 선택
  selectSession(session: ChatSession) {
    currentSession.set(session);
    console.log('세션 선택:', session.title);
  },
  
  // 세션 삭제
  async deleteSession(sessionId: string) {
    try {
      await api.deleteSession(sessionId);
      
      // 로컬 상태에서 제거
      sessions.update(list => list.filter(s => s.id !== sessionId));
      
      // 현재 세션이 삭제된 세션이면 null로 설정
      const current = get(currentSession);
      if (current?.id === sessionId) {
        currentSession.set(null);
      }
      
      console.log('세션 삭제 완료:', sessionId);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '세션 삭제에 실패했습니다';
      error.set(errorMessage);
      console.error('세션 삭제 오류:', err);
      throw err;
    }
  },
  
  // 메시지 전송 (스트리밍)
  async sendMessage(message: string, onChunk?: (chunk: string) => void) {
    const session = get(currentSession);
    const model = get(selectedModel);
    
    if (!session) {
      throw new Error('활성 세션이 없습니다');
    }
    
    try {
      isLoading.set(true);
      error.set(null);
      
      // 사용자 메시지를 로컬 상태에 즉시 추가
      const userMessage: ChatMessage = {
        role: 'user',
        content: message,
        timestamp: new Date().toISOString()
      };
      
      const updatedSession = {
        ...session,
        messages: [...session.messages, userMessage]
      };
      
      currentSession.set(updatedSession);
      
      // AI 응답을 위한 빈 메시지 추가
      const aiMessage: ChatMessage = {
        role: 'assistant',
        content: '',
        timestamp: new Date().toISOString()
      };
      
      const sessionWithAiMessage = {
        ...updatedSession,
        messages: [...updatedSession.messages, aiMessage]
      };
      
      currentSession.set(sessionWithAiMessage);
      
      // 스트리밍으로 AI 응답 받기
      let fullResponse = '';
      
      for await (const chunk of api.sendMessage(session.id, message, model.provider, model.id)) {
        fullResponse += chunk;
        
        // 실시간으로 AI 응답 업데이트
        currentSession.update(currentSession => {
          if (!currentSession) return null;
          
          const messages = [...currentSession.messages];
          const lastMessage = messages[messages.length - 1];
          
          if (lastMessage && lastMessage.role === 'assistant') {
            lastMessage.content = fullResponse;
          }
          
          return { ...currentSession, messages };
        });
        
        onChunk?.(chunk);
      }
      
      // 세션 목록도 업데이트
      const finalSession = get(currentSession);
      if (finalSession) {
        sessions.update(list => 
          list.map(s => s.id === session.id ? finalSession : s)
        );
      }
      
      console.log('메시지 전송 완료');
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '메시지 전송에 실패했습니다';
      error.set(errorMessage);
      console.error('메시지 전송 오류:', err);
      throw err;
    } finally {
      isLoading.set(false);
    }
  }
};