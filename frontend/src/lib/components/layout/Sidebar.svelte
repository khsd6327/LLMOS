<script lang="ts">
  import { onMount } from "svelte";
  import {
    sessions,
    currentSession,
    currentSessionId,
    sidebarOpen,
    currentPage,
    usageStats,
  } from "$lib/stores";
  import { api } from "$lib/api";
  import { showError, showSuccess } from "$lib/stores";
  import {
    MessageSquare,
    Plus,
    Star,
    Settings,
    BarChart3,
    Menu,
    X,
    Pin,
    Trash2,
    Edit,
    MoreVertical,
  } from "lucide-svelte";
  import ModelSelector from "../ai/ModelSelector.svelte";
  import SessionUsageStats from "../ai/SessionUsageStats.svelte";

  let editingSessionId: string | null = null;
  let editingTitle = "";

  // 세션 선택
  function selectSession(session: any) {
    currentSessionId.set(session.id);
    currentSession.set(session);
    currentPage.set("chat");
  }

  // 세션 삭제
  async function deleteSession(sessionId: string, event: Event) {
    event.stopPropagation();

    if (!confirm("이 채팅을 삭제하시겠습니까?")) return;

    try {
      await api.deleteSession(sessionId);

      // 로컬 상태 업데이트
      sessions.update((list) => list.filter((s) => s.id !== sessionId));

      // 현재 세션이 삭제된 세션이면 초기화
      if ($currentSessionId === sessionId) {
        currentSessionId.set(null);
        currentSession.set(null);
      }

      showSuccess("채팅이 삭제되었습니다.");
    } catch (error) {
      console.error("세션 삭제 실패:", error);
      showError("채팅을 삭제할 수 없습니다.");
    }
  }

  // 세션 고정/해제
  async function togglePin(
    sessionId: string,
    isPinned: boolean | undefined,
    event: Event
  ) {
    event.stopPropagation();

    try {
      const updatedSession = await api.updateSession(sessionId, {
        is_pinned: !Boolean(isPinned),
      });

      // 로컬 상태 업데이트
      sessions.update((list) =>
        list.map((s) => (s.id === sessionId ? updatedSession : s))
      );

      if ($currentSessionId === sessionId) {
        currentSession.set(updatedSession);
      }

      showSuccess(
        Boolean(isPinned) ? "고정이 해제되었습니다." : "채팅이 고정되었습니다."
      );
    } catch (error) {
      console.error("세션 고정 실패:", error);
      showError(
        Boolean(isPinned)
          ? "고정을 해제할 수 없습니다."
          : "채팅을 고정할 수 없습니다."
      );
    }
  }

  // 제목 편집 시작
  function startEditing(session: any, event: Event) {
    event.stopPropagation();
    editingSessionId = session.id;
    editingTitle = session.title;
  }

  // 제목 편집 완료
  async function finishEditing() {
    if (!editingSessionId || !editingTitle.trim()) {
      editingSessionId = null;
      return;
    }

    try {
      const updatedSession = await api.updateSession(editingSessionId, {
        title: editingTitle.trim(),
      });

      // 로컬 상태 업데이트
      sessions.update((list) =>
        list.map((s) => (s.id === editingSessionId ? updatedSession : s))
      );

      if ($currentSessionId === editingSessionId) {
        currentSession.set(updatedSession);
      }

      showSuccess("제목이 변경되었습니다.");
    } catch (error) {
      console.error("제목 변경 실패:", error);
      showError("제목을 변경할 수 없습니다.");
    } finally {
      editingSessionId = null;
      editingTitle = "";
    }
  }

  // 제목 편집 취소
  function cancelEditing() {
    editingSessionId = null;
    editingTitle = "";
  }

  // 키보드 이벤트 처리
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter") {
      finishEditing();
    } else if (event.key === "Escape") {
      cancelEditing();
    }
  }

  // 새 채팅 생성
  async function createNewChat() {
    try {
      const newSession = await api.createSession();
      sessions.update((list) => [newSession, ...list]);
      selectSession(newSession);
      showSuccess("새 채팅이 생성되었습니다.");
    } catch (error) {
      console.error("새 채팅 생성 실패:", error);
      showError("새 채팅을 생성할 수 없습니다.");
    }
  }

  // 세션을 고정된 것과 일반 것으로 분리
  $: pinnedSessions = $sessions.filter((s) => s.is_pinned);
  $: unpinnedSessions = $sessions.filter((s) => !s.is_pinned);
</script>

<aside
  class="flex flex-col w-80 bg-dark-900 border-r border-dark-700 {$sidebarOpen
    ? ''
    : 'hidden'}"
>
  <!-- 헤더 -->
  <div class="flex items-center justify-between p-4 border-b border-dark-700">
    <h1 class="text-lg font-semibold text-gradient">LLM OS</h1>
    <button class="btn-icon" on:click={() => sidebarOpen.set(false)}>
      <X size={20} />
    </button>
  </div>

  <!-- 새 채팅 버튼 -->
  <div class="p-4">
    <button class="btn-primary w-full" on:click={createNewChat}>
      <Plus size={16} class="mr-2" />
      새 채팅
    </button>
  </div>

  <!-- 모델 선택 -->
  <div class="px-4 pb-4">
    <ModelSelector />
  </div>

  <!-- 세션 목록 -->
  <div class="flex-1 overflow-y-auto px-4">
    <!-- 고정된 채팅 -->
    {#if pinnedSessions.length > 0}
      <div class="mb-4">
        <h3
          class="text-xs font-medium text-dark-400 uppercase tracking-wider mb-2"
        >
          고정된 채팅
        </h3>
        {#each pinnedSessions as session (session.id)}
          <div class="mb-1">
            <button
              class="w-full text-left p-3 rounded-lg transition-colors duration-200 relative group
                {$currentSessionId === session.id
                ? 'bg-dark-700 text-dark-100'
                : 'hover:bg-dark-800 text-dark-300'}"
              on:click={() => selectSession(session)}
            >
              <div class="flex items-center">
                <Pin size={14} class="mr-2 text-accent-500 flex-shrink-0" />

                {#if editingSessionId === session.id}
                  <input
                    type="text"
                    bind:value={editingTitle}
                    on:keydown={handleKeydown}
                    on:blur={finishEditing}
                    class="flex-1 bg-transparent border-none outline-none text-sm"
                  />
                {:else}
                  <span class="flex-1 text-sm truncate">{session.title}</span>
                {/if}

                <!-- 세션 메뉴 -->
                <div
                  class="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <div class="relative">
                    <button
                      class="btn-icon p-1"
                      on:click={(e) => e.stopPropagation()}
                    >
                      <MoreVertical size={14} />
                    </button>

                    <!-- 드롭다운 메뉴 -->
                    <div class="dropdown">
                      <button
                        class="dropdown-item"
                        on:click={(e) => startEditing(session, e)}
                      >
                        <Edit size={14} class="mr-2" />
                        제목 변경
                      </button>
                      <button
                        class="dropdown-item"
                        on:click={(e) =>
                          togglePin(session.id, session.is_pinned, e)}
                      >
                        <Pin size={14} class="mr-2" />
                        고정 해제
                      </button>
                      <button
                        class="dropdown-item text-red-400 hover:text-red-300"
                        on:click={(e) => deleteSession(session.id, e)}
                      >
                        <Trash2 size={14} class="mr-2" />
                        삭제
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </button>
          </div>
        {/each}
      </div>
    {/if}

    <!-- 일반 채팅 -->
    <div>
      <h3
        class="text-xs font-medium text-dark-400 uppercase tracking-wider mb-2"
      >
        최근 채팅
      </h3>
      {#each unpinnedSessions.slice(0, 10) as session (session.id)}
        <div class="mb-1">
          <button
            class="w-full text-left p-3 rounded-lg transition-colors duration-200 relative group
              {$currentSessionId === session.id
              ? 'bg-dark-700 text-dark-100'
              : 'hover:bg-dark-800 text-dark-300'}"
            on:click={() => selectSession(session)}
          >
            <div class="flex items-center">
              <MessageSquare
                size={14}
                class="mr-2 text-dark-500 flex-shrink-0"
              />

              {#if editingSessionId === session.id}
                <input
                  type="text"
                  bind:value={editingTitle}
                  on:keydown={handleKeydown}
                  on:blur={finishEditing}
                  class="flex-1 bg-transparent border-none outline-none text-sm"
                />
              {:else}
                <span class="flex-1 text-sm truncate">{session.title}</span>
              {/if}

              <!-- 세션 메뉴 -->
              <div class="opacity-0 group-hover:opacity-100 transition-opacity">
                <div class="relative">
                  <button
                    class="btn-icon p-1"
                    on:click={(e) => e.stopPropagation()}
                  >
                    <MoreVertical size={14} />
                  </button>

                  <!-- 드롭다운 메뉴 -->
                  <div class="dropdown">
                    <button
                      class="dropdown-item"
                      on:click={(e) => startEditing(session, e)}
                    >
                      <Edit size={14} class="mr-2" />
                      제목 변경
                    </button>
                    <button
                      class="dropdown-item"
                      on:click={(e) =>
                        togglePin(session.id, session.is_pinned, e)}
                    >
                      <Pin size={14} class="mr-2" />
                      고정하기
                    </button>
                    <button
                      class="dropdown-item text-red-400 hover:text-red-300"
                      on:click={(e) => deleteSession(session.id, e)}
                    >
                      <Trash2 size={14} class="mr-2" />
                      삭제
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </button>
        </div>
      {/each}
    </div>
  </div>

  <!-- 하단 메뉴 -->
  <div class="border-t border-dark-700 p-4 space-y-2">
    <!-- 사용량 통계 -->
    <SessionUsageStats />

    <!-- 네비게이션 메뉴 -->
    <div class="space-y-1">
      <button
        class="w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors
          {$currentPage === 'favorites'
          ? 'bg-dark-700 text-dark-100'
          : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'}"
        on:click={() => currentPage.set("favorites")}
      >
        <Star size={16} class="mr-3" />
        즐겨찾기
      </button>

      <button
        class="w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors
          {$currentPage === 'usage'
          ? 'bg-dark-700 text-dark-100'
          : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'}"
        on:click={() => currentPage.set("usage")}
      >
        <BarChart3 size={16} class="mr-3" />
        사용량 통계
      </button>

      <button
        class="w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors
          {$currentPage === 'settings'
          ? 'bg-dark-700 text-dark-100'
          : 'text-dark-400 hover:text-dark-200 hover:bg-dark-800'}"
        on:click={() => currentPage.set("settings")}
      >
        <Settings size={16} class="mr-3" />
        설정
      </button>
    </div>
  </div>
</aside>

<!-- 사이드바가 닫혀있을 때 토글 버튼 -->
{#if !$sidebarOpen}
  <button
    class="fixed top-4 left-4 z-50 btn-secondary"
    on:click={() => sidebarOpen.set(true)}
  >
    <Menu size={20} />
  </button>
{/if}
