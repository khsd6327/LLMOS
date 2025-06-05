<!-- ted-os-project/frontend/src/lib/components/chat/MessageItem.svelte -->
<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import {
    MoreVertical,
    Copy,
    Edit,
    Trash2,
    Star,
    RefreshCw,
    Pin,
    User,
    Bot,
  } from "lucide-svelte";
  import type { ChatSession, ChatMessage } from "$lib/api";
  import { api } from "$lib/api";
  import { sessions, currentSession, favorites } from "$lib/stores";
  import { showError, showSuccess } from "$lib/stores";

  export let message: ChatMessage;
  export let index: number;
  export let session: ChatSession;
  export let isLast: boolean;

  let showMenu = false;
  let isEditing = false;
  let editContent = message.content as string;
  let menuElement: HTMLElement;

  const dispatch = createEventDispatcher();

  // 메시지 내용을 문자열로 변환
  function getMessageText(content: any): string {
    if (typeof content === "string") return content;
    if (Array.isArray(content)) {
      return content
        .filter((part) => part.type === "text")
        .map((part) => part.text)
        .join(" ");
    }
    return "";
  }

  // 클립보드 복사
  async function copyToClipboard() {
    try {
      const text = getMessageText(message.content);
      await navigator.clipboard.writeText(text);
      showSuccess("메시지가 클립보드에 복사되었습니다.");
    } catch (error) {
      showError("클립보드 복사에 실패했습니다.");
    }
    showMenu = false;
  }

  // 메시지 편집 시작
  function startEdit() {
    isEditing = true;
    editContent = getMessageText(message.content);
    showMenu = false;
  }

  // 메시지 편집 저장
  async function saveEdit() {
    if (!editContent.trim()) return;

    try {
      // 세션의 메시지 업데이트
      const updatedSession = {
        ...session,
        messages: session.messages.map((msg, idx) =>
          idx === index ? { ...msg, content: editContent.trim() } : msg
        ),
      };

      // 백엔드에 업데이트 (실제로는 세션 전체를 업데이트해야 할 수도 있음)
      await api.updateSession(session.id, { title: session.title });

      // 로컬 상태 업데이트
      sessions.update((list) =>
        list.map((s) => (s.id === session.id ? updatedSession : s))
      );
      currentSession.set(updatedSession);

      showSuccess("메시지가 수정되었습니다.");
    } catch (error) {
      console.error("메시지 수정 실패:", error);
      showError("메시지를 수정할 수 없습니다.");
    }

    isEditing = false;
  }

  // 메시지 편집 취소
  function cancelEdit() {
    isEditing = false;
    editContent = getMessageText(message.content);
  }

  // 메시지 삭제
  async function deleteMessage() {
    if (!confirm("이 메시지를 삭제하시겠습니까?")) return;

    try {
      // 세션의 메시지 삭제
      const updatedSession = {
        ...session,
        messages: session.messages.filter((_, idx) => idx !== index),
      };

      // 백엔드에 업데이트
      await api.updateSession(session.id, { title: session.title });

      // 로컬 상태 업데이트
      sessions.update((list) =>
        list.map((s) => (s.id === session.id ? updatedSession : s))
      );
      currentSession.set(updatedSession);

      showSuccess("메시지가 삭제되었습니다.");
    } catch (error) {
      console.error("메시지 삭제 실패:", error);
      showError("메시지를 삭제할 수 없습니다.");
    }

    showMenu = false;
  }

  // 즐겨찾기 추가
  async function addToFavorites() {
    try {
      const favoriteData = {
        session_id: session.id,
        message_id: `message_${index}`,
        role: message.role,
        content: getMessageText(message.content),
        created_at: new Date().toISOString(),
        model_provider: message.model_provider,
        model_name: message.model_name,
        context_messages: session.messages.slice(
          Math.max(0, index - 2),
          index + 1
        ),
        tags: [],
        notes: "",
      };

      const favorite = await api.createFavorite(favoriteData);

      // 즐겨찾기 목록 업데이트
      favorites.update((list) => [favorite, ...list]);

      showSuccess("즐겨찾기에 추가되었습니다.");
    } catch (error) {
      console.error("즐겨찾기 추가 실패:", error);
      showError("즐겨찾기에 추가할 수 없습니다.");
    }

    showMenu = false;
  }

  // AI 응답 재생성 (마지막 메시지인 경우만)
  function regenerateResponse() {
    // 이 기능은 부모 컴포넌트에서 처리하도록 이벤트 발생
    dispatch("regenerate");
    showMenu = false;
  }

  // 외부 클릭으로 메뉴 닫기
  function handleClickOutside(event: MouseEvent) {
    if (menuElement && !menuElement.contains(event.target as Node)) {
      showMenu = false;
    }
  }

  // 키보드 이벤트 처리
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      saveEdit();
    } else if (event.key === "Escape") {
      cancelEdit();
    }
  }

  $: messageText = getMessageText(message.content);
  $: isUser = message.role === "user";
  $: isAssistant = message.role === "assistant";
</script>

<svelte:window on:click={handleClickOutside} />

<div
  class="flex space-x-3 group {isUser
    ? 'flex-row-reverse space-x-reverse'
    : ''}"
>
  <!-- 아바타 -->
  <div
    class="w-8 h-8 flex-shrink-0 rounded-full flex items-center justify-center
    {isUser
      ? 'bg-dark-700'
      : 'bg-gradient-to-br from-claude-orange to-claude-blue'}"
  >
    {#if isUser}
      <User size={16} class="text-dark-300" />
    {:else}
      <Bot size={16} class="text-white" />
    {/if}
  </div>

  <!-- 메시지 내용 -->
  <div class="flex-1 min-w-0">
    <!-- 메시지 버블 -->
    <div
      class="relative {isUser ? 'ml-auto max-w-[80%]' : 'mr-auto max-w-[90%]'}"
    >
      <div
        class="rounded-xl p-4 {isUser
          ? 'bg-dark-800 text-dark-100'
          : 'bg-dark-900/50 border border-dark-700/50 text-dark-100'}"
      >
        {#if isEditing}
          <!-- 편집 모드 -->
          <textarea
            bind:value={editContent}
            on:keydown={handleKeydown}
            class="w-full bg-transparent border border-dark-600 rounded-lg p-2 text-sm resize-none focus:outline-none focus:ring-2 focus:ring-claude-orange/50"
            rows="3"
            autofocus
          />
          <div class="flex justify-end space-x-2 mt-2">
            <button class="btn-ghost text-xs" on:click={cancelEdit}>
              취소
            </button>
            <button class="btn-primary text-xs" on:click={saveEdit}>
              저장
            </button>
          </div>
        {:else}
          <!-- 일반 메시지 표시 -->
          <div class="prose prose-invert max-w-none text-sm">
            {messageText}
          </div>
        {/if}
      </div>

      <!-- 메시지 액션 버튼 -->
      <div
        class="absolute -top-2 {isUser
          ? 'left-0'
          : 'right-0'} opacity-0 group-hover:opacity-100 transition-opacity"
      >
        <div class="relative" bind:this={menuElement}>
          <button
            class="btn-icon bg-dark-800 border border-dark-600 shadow-lg"
            on:click={() => (showMenu = !showMenu)}
          >
            <MoreVertical size={14} />
          </button>

          <!-- 드롭다운 메뉴 -->
          {#if showMenu}
            <div class="dropdown {isUser ? 'left-0' : 'right-0'}">
              <button class="dropdown-item" on:click={copyToClipboard}>
                <Copy size={14} class="mr-2" />
                복사
              </button>

              {#if isUser}
                <button class="dropdown-item" on:click={startEdit}>
                  <Edit size={14} class="mr-2" />
                  수정
                </button>
              {/if}

              {#if isAssistant}
                <button class="dropdown-item" on:click={addToFavorites}>
                  <Star size={14} class="mr-2" />
                  즐겨찾기
                </button>

                {#if isLast}
                  <button class="dropdown-item" on:click={regenerateResponse}>
                    <RefreshCw size={14} class="mr-2" />
                    재생성
                  </button>
                {/if}
              {/if}

              <div class="border-t border-dark-600 my-1" />

              <button
                class="dropdown-item text-red-400 hover:text-red-300"
                on:click={deleteMessage}
              >
                <Trash2 size={14} class="mr-2" />
                삭제
              </button>
            </div>
          {/if}
        </div>
      </div>
    </div>

    <!-- 메시지 메타데이터 -->
    <div
      class="mt-1 text-xs text-dark-500 {isUser ? 'text-right' : 'text-left'}"
    >
      {#if isAssistant && message.model_display_name}
        <span>🤖 {message.model_display_name}</span>
      {:else if isAssistant && message.model_name}
        <span>🤖 {message.model_name}</span>
      {/if}

      {#if message.timestamp}
        <span class="ml-2"
          >{new Date(message.timestamp).toLocaleTimeString()}</span
        >
      {/if}
    </div>
  </div>
</div>
