<!-- /ted-os-project/frontend/src/lib/components/features/chat/ChatSideBar.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import {
    sessions,
    currentSession,
    isLoading,
    error,
    chatStore,
  } from "$lib/stores/chat";

  // 컴포넌트 마운트 시 세션 목록 로드
  onMount(() => {
    chatStore.loadSessions();
  });

  function selectChat(session: any) {
    chatStore.selectSession(session);
  }

  async function createNewChat() {
    try {
      await chatStore.createSession();
    } catch (err) {
      console.error("새 채팅 생성 실패:", err);
    }
  }

  async function deleteChat(event: Event, sessionId: string) {
    event.stopPropagation();

    if (confirm("이 채팅을 삭제하시겠습니까?")) {
      try {
        await chatStore.deleteSession(sessionId);
      } catch (err) {
        console.error("채팅 삭제 실패:", err);
      }
    }
  }

  function formatDate(dateString: string) {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) {
      return date.toLocaleTimeString("ko-KR", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } else if (diffDays === 1) {
      return "어제";
    } else if (diffDays < 7) {
      return `${diffDays}일 전`;
    } else {
      return date.toLocaleDateString("ko-KR");
    }
  }
</script>

<div class="h-full flex flex-col">
  <!-- 헤더 -->
  <div class="p-4 border-b border-gray-200">
    <div class="flex items-center justify-between mb-4">
      <h2 class="text-lg font-semibold text-gray-900">채팅</h2>
      <div class="flex items-center space-x-2">
        <!-- 새 채팅 버튼 -->
        <button
          on:click={createNewChat}
          class="w-8 h-8 bg-gray-900 text-white rounded-lg flex items-center justify-center hover:bg-gray-800 transition-colors"
          title="새 채팅"
          disabled={$isLoading}
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
        </button>
      </div>
    </div>
  </div>

  <!-- 로딩 상태 -->
  {#if $isLoading && $sessions.length === 0}
    <div class="flex-1 flex items-center justify-center">
      <div class="text-gray-500 text-sm">채팅 목록을 불러오는 중...</div>
    </div>
  {/if}

  <!-- 에러 상태 -->
  {#if $error}
    <div class="p-4">
      <div class="bg-red-50 border border-red-200 rounded-lg p-3">
        <div class="text-red-800 text-sm">{$error}</div>
        <button
          on:click={() => chatStore.loadSessions()}
          class="mt-2 text-red-600 text-sm underline hover:no-underline"
        >
          다시 시도
        </button>
      </div>
    </div>
  {/if}

  <!-- 채팅 목록 -->
  {#if $sessions.length > 0}
    <div class="flex-1 overflow-y-auto">
      {#each $sessions as session}
        <button
          on:click={() => selectChat(session)}
          class="w-full p-4 text-left hover:bg-gray-100 border-b border-gray-100 transition-colors relative group
                 {$currentSession?.id === session.id ? 'bg-gray-100' : ''}"
        >
          <div class="space-y-1">
            <div class="font-medium text-gray-900 truncate pr-8">
              {session.title}
              {#if session.is_pinned}
                <span class="text-yellow-500 ml-1">📌</span>
              {/if}
            </div>
            <div class="text-sm text-gray-500 truncate">
              {#if session.messages.length > 0}
                {session.messages[session.messages.length - 1].content
                  .toString()
                  .substring(0, 50)}...
              {:else}
                새 채팅
              {/if}
            </div>
            <div class="text-xs text-gray-400">
              {formatDate(session.updated_at)}
            </div>
          </div>

          <!-- 삭제 버튼 -->
          <button
            on:click={(e) => deleteChat(e, session.id)}
            class="absolute top-4 right-4 opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 rounded transition-opacity"
            title="채팅 삭제"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <polyline points="3,6 5,6 21,6" />
              <path
                d="M19,6v14a2,2 0 0,1 -2,2H7a2,2 0 0,1 -2,-2V6M8,6V4a2,2 0 0,1 2,-2h4a2,2 0 0,1 2,2v2"
              />
            </svg>
          </button>
        </button>
      {/each}
    </div>
  {:else if !$isLoading && !$error}
    <!-- 빈 상태 -->
    <div class="flex-1 flex items-center justify-center p-4">
      <div class="text-center text-gray-500">
        <div class="text-sm">아직 채팅이 없습니다</div>
        <button
          on:click={createNewChat}
          class="mt-2 text-blue-600 text-sm underline hover:no-underline"
        >
          새 채팅 시작하기
        </button>
      </div>
    </div>
  {/if}
</div>
