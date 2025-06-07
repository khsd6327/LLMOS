<script lang="ts">
  import { createEventDispatcher } from "svelte";

  export let isOpen = false;
  export let title = "";
  export let size: "sm" | "md" | "lg" | "xl" = "md";
  export let closeOnEscape = true;
  export let closeOnBackdrop = true;

  const dispatch = createEventDispatcher();

  // 모달 크기 클래스 매핑
  const sizeClasses = {
    sm: "max-w-md",
    md: "max-w-2xl",
    lg: "max-w-4xl",
    xl: "max-w-6xl",
  };

  // ESC 키 처리
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Escape" && closeOnEscape && isOpen) {
      close();
    }
  }

  // 백드롭 클릭 처리
  function handleBackdropClick(event: MouseEvent) {
    if (closeOnBackdrop && event.target === event.currentTarget) {
      close();
    }
  }

  // 모달 닫기
  function close() {
    dispatch("close");
  }

  // 모달이 열릴 때 body 스크롤 방지
  import { onMount } from "svelte";
  import { browser } from "$app/environment";

  // 브라우저 환경에서만 document 접근
  $: if (browser && isOpen) {
    document.body.style.overflow = "hidden";
  } else if (browser) {
    document.body.style.overflow = "";
  }
</script>

<svelte:window on:keydown={handleKeydown} />

{#if isOpen}
  <!-- 백드롭 -->
  <div
    class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4"
    on:click={handleBackdropClick}
  >
    <!-- 모달 컨테이너 -->
    <div
      class="bg-white rounded-lg shadow-xl w-full {sizeClasses[
        size
      ]} max-h-[90vh] flex flex-col"
      on:click|stopPropagation
    >
      <!-- 헤더 -->
      {#if title || $$slots.header}
        <div
          class="px-6 py-4 border-b border-gray-200 flex items-center justify-between"
        >
          <div class="flex-1">
            {#if $$slots.header}
              <slot name="header" />
            {:else}
              <h2 class="text-xl font-semibold text-gray-900">{title}</h2>
            {/if}
          </div>

          <!-- 닫기 버튼 -->
          <button
            on:click={close}
            class="p-1 hover:bg-gray-100 rounded-lg transition-colors"
            title="닫기"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      {/if}

      <!-- 콘텐츠 -->
      <div class="flex-1 overflow-y-auto">
        <slot />
      </div>

      <!-- 푸터 -->
      {#if $$slots.footer}
        <div class="px-6 py-4 border-t border-gray-200">
          <slot name="footer" />
        </div>
      {/if}
    </div>
  </div>
{/if}
