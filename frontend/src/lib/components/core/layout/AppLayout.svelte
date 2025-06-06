<!-- ted-os-project/frontend/src/lib/components/core/layout/AppLayout.svelte -->
<script lang="ts">
  // 사이드바 표시 여부와 크기
  let showSidebar = true;
  let sidebarWidth = 320; // 초기 너비 (w-80 = 320px)
  let isResizing = false;

  function toggleSidebar() {
    showSidebar = !showSidebar;
  }

  // 사이드바 크기 조절
  function handleMouseDown(event: MouseEvent) {
    isResizing = true;
    document.addEventListener("mousemove", handleMouseMove);
    document.addEventListener("mouseup", handleMouseUp);
    event.preventDefault();
  }

  function handleMouseMove(event: MouseEvent) {
    if (!isResizing) return;

    const newWidth = Math.max(280, Math.min(500, event.clientX));
    sidebarWidth = newWidth;
  }

  function handleMouseUp() {
    isResizing = false;
    document.removeEventListener("mousemove", handleMouseMove);
    document.removeEventListener("mouseup", handleMouseUp);
  }
</script>

<!-- 전체 컨테이너 -->
<div class="h-screen bg-white flex">
  <!-- 사이드바 (채팅 목록) -->
  {#if showSidebar}
    <div
      class="bg-gray-50 border-r border-gray-200 flex-shrink-0 relative"
      style="width: {sidebarWidth}px;"
    >
      <slot name="sidebar" />

      <!-- 사이드바 크기 조절 핸들 -->
      <div
        class="absolute top-0 right-0 w-1 h-full bg-transparent hover:bg-blue-500 cursor-col-resize transition-colors"
        on:mousedown={handleMouseDown}
        title="사이드바 크기 조절"
      />
    </div>
  {/if}

  <!-- 메인 채팅 영역 -->
  <div class="flex-1 flex flex-col">
    <!-- 상단 헤더 -->
    <div
      class="h-14 bg-white border-b border-gray-200 flex items-center justify-between px-4"
    >
      <!-- 왼쪽: 사이드바 토글 + 슬롯으로 모델 선택기 -->
      <div class="flex items-center space-x-3">
        {#if !showSidebar}
          <button
            on:click={toggleSidebar}
            class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            title="사이드바 열기"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="21" y2="12" />
              <line x1="3" y1="18" x2="21" y2="18" />
            </svg>
          </button>
        {/if}
        <slot name="header-left" />
      </div>

      <!-- 중간: 채팅 제목 -->
      <div class="flex-1 text-center">
        <slot name="header-center" />
      </div>

      <!-- 오른쪽: 사용자 아이콘과 설정 -->
      <div class="flex items-center space-x-2">
        <!-- 사용자 프로필 버튼 -->
        <button
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="프로필"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
            <circle cx="12" cy="7" r="4" />
          </svg>
        </button>

        <!-- 설정 버튼 -->
        <button
          class="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          title="설정"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="2"
          >
            <circle cx="12" cy="12" r="3" />
            <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m21-7h-6M7 5H1m6 6h6" />
          </svg>
        </button>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <div class="flex-1">
      <slot />
    </div>
  </div>
</div>

<style>
  /* 크기 조절 중일 때 커서 변경 */
  :global(body.resizing) {
    cursor: col-resize !important;
    user-select: none;
  }
</style>
