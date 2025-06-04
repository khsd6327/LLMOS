<script lang="ts">
  import { currentSession, sidebarOpen, isGenerating } from "$lib/stores";
  import { api } from "$lib/api";
  import { showError, showSuccess } from "$lib/stores";
  import {
    Menu,
    Plus,
    Edit,
    Pin,
    PinOff,
    Settings,
    MoreVertical,
  } from "lucide-svelte";

  export let createNewChat: () => void;

  let showMenu = false;
  let isEditing = false;
  let editTitle = "";

  // 제목 편집 시작
  function startEditing() {
    if (!$currentSession) return;
    isEditing = true;
    editTitle = $currentSession.title;
    showMenu = false;
  }

  // 제목 편집 완료
  async function saveTitle() {
    if (!$currentSession || !editTitle.trim()) {
      isEditing = false;
      return;
    }

    try {
      await api.updateSession($currentSession.id, { title: editTitle.trim() });
      showSuccess("제목이 변경되었습니다.");
    } catch (error) {
      console.error("제목 변경 실패:", error);
      showError("제목을 변경할 수 없습니다.");
    }

    isEditing = false;
  }

  // 제목 편집 취소
  function cancelEditing() {
    isEditing = false;
    editTitle = "";
  }

  // 세션 고정/해제
  async function togglePin() {
    if (!$currentSession) return;

    try {
      await api.updateSession($currentSession.id, {
        is_pinned: !$currentSession.is_pinned,
      });

      const action = $currentSession.is_pinned
        ? "고정이 해제되었습니다."
        : "채팅이 고정되었습니다.";
      showSuccess(action);
    } catch (error) {
      console.error("고정 상태 변경 실패:", error);
      showError("고정 상태를 변경할 수 없습니다.");
    }

    showMenu = false;
  }

  // 키보드 이벤트 처리
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      saveTitle();
    } else if (event.key === "Escape") {
      cancelEditing();
    }
  }

  // 외부 클릭으로 메뉴 닫기
  function handleClickOutside(event: MouseEvent) {
    const target = event.target as HTMLElement;
    if (!target.closest(".header-menu")) {
      showMenu = false;
    }
  }
</script>

<svelte:window on:click={handleClickOutside} />

<header
  class="flex items-center justify-between p-4 border-b border-dark-700 bg-dark-900/80 backdrop-blur-sm"
>
  <div class="flex items-center space-x-3">
    <!-- 사이드바 토글 (사이드바가 닫혀있을 때만) -->
    {#if !$sidebarOpen}
      <button class="btn-icon" on:click={() => sidebarOpen.set(true)}>
        <Menu size={20} />
      </button>
    {/if}

    <!-- 세션 제목 -->
    <div class="flex items-center space-x-2">
      {#if $currentSession}
        {#if $currentSession.is_pinned}
          <Pin size={16} class="text-accent-500" />
        {/if}

        {#if isEditing}
          <input
            type="text"
            bind:value={editTitle}
            on:keydown={handleKeydown}
            on:blur={saveTitle}
            class="bg-dark-800 border border-dark-600 rounded px-2 py-1 text-sm text-dark-100 focus:outline-none focus:ring-2 focus:ring-claude-orange/50"
            autofocus
          />
        {:else}
          <h1 class="text-lg font-semibold text-dark-100 truncate max-w-md">
            {$currentSession.title}
          </h1>
        {/if}
      {:else}
        <h1 class="text-lg font-semibold text-dark-100">LLM OS</h1>
      {/if}
    </div>
  </div>

  <!-- 헤더 액션 -->
  <div class="flex items-center space-x-2">
    <!-- 새 채팅 버튼 -->
    <button
      class="btn-secondary"
      on:click={createNewChat}
      disabled={$isGenerating}
      title="새 채팅 시작"
    >
      <Plus size={16} class="mr-1" />
      새 채팅
    </button>

    <!-- 세션 메뉴 (현재 세션이 있을 때만) -->
    {#if $currentSession}
      <div class="relative header-menu">
        <button class="btn-icon" on:click={() => (showMenu = !showMenu)}>
          <MoreVertical size={20} />
        </button>

        {#if showMenu}
          <div class="dropdown">
            <button class="dropdown-item" on:click={startEditing}>
              <Edit size={14} class="mr-2" />
              제목 변경
            </button>

            <button class="dropdown-item" on:click={togglePin}>
              {#if $currentSession.is_pinned}
                <PinOff size={14} class="mr-2" />
                고정 해제
              {:else}
                <Pin size={14} class="mr-2" />
                고정하기
              {/if}
            </button>

            <div class="border-t border-dark-600 my-1" />

            <button class="dropdown-item">
              <Settings size={14} class="mr-2" />
              채팅 설정
            </button>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</header>

<!-- 진행 표시 (AI가 응답 중일 때) -->
{#if $isGenerating}
  <div class="h-1 bg-dark-800 relative overflow-hidden">
    <div
      class="absolute inset-0 bg-gradient-to-r from-claude-orange to-claude-blue animate-pulse"
    />
    <div
      class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-[shimmer_1.5s_infinite]"
    />
  </div>
{/if}

<style>
  @keyframes shimmer {
    0% {
      transform: translateX(-100%);
    }
    100% {
      transform: translateX(100%);
    }
  }
</style>
