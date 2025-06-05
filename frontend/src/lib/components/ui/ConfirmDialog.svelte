<script lang="ts">
  import { createEventDispatcher } from "svelte";
  import { AlertTriangle, CheckCircle, XCircle, Info } from "lucide-svelte";

  export let show: boolean = false;
  export let title: string = "확인";
  export let message: string = "이 작업을 진행하시겠습니까?";
  export let confirmText: string = "확인";
  export let cancelText: string = "취소";
  export let type: "warning" | "danger" | "info" | "success" = "warning";
  export let confirmVariant: "primary" | "danger" = "primary";

  const dispatch = createEventDispatcher();

  function handleConfirm() {
    dispatch("confirm");
    show = false;
  }

  function handleCancel() {
    dispatch("cancel");
    show = false;
  }

  function handleBackdropClick(event: MouseEvent) {
    if (event.target === event.currentTarget) {
      handleCancel();
    }
  }

  // 타입별 아이콘과 색상 결정
  $: icon =
    type === "warning"
      ? AlertTriangle
      : type === "danger"
      ? XCircle
      : type === "success"
      ? CheckCircle
      : Info;

  $: iconColor =
    type === "warning"
      ? "text-yellow-400"
      : type === "danger"
      ? "text-red-400"
      : type === "success"
      ? "text-green-400"
      : "text-blue-400";

  $: confirmButtonClass =
    confirmVariant === "danger"
      ? "btn bg-red-600 hover:bg-red-700 text-white"
      : "btn-primary";
</script>

{#if show}
  <!-- 백드롭 오버레이 -->
  <div
    class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
    on:click={handleBackdropClick}
    role="dialog"
    aria-modal="true"
    aria-labelledby="dialog-title"
    aria-describedby="dialog-message"
  >
    <!-- 다이얼로그 컨테이너 -->
    <div
      class="bg-dark-900 border border-dark-700 rounded-xl shadow-2xl max-w-md w-full mx-4 transform transition-all duration-200 scale-100"
      on:click|stopPropagation
    >
      <!-- 헤더 -->
      <div class="p-6 border-b border-dark-700">
        <div class="flex items-center space-x-3">
          <svelte:component this={icon} size={24} class={iconColor} />
          <h2 id="dialog-title" class="text-lg font-semibold text-dark-100">
            {title}
          </h2>
        </div>
      </div>

      <!-- 메시지 본문 -->
      <div class="p-6">
        <p id="dialog-message" class="text-dark-300 leading-relaxed">
          {message}
        </p>
      </div>

      <!-- 버튼 영역 -->
      <div
        class="flex items-center justify-end space-x-3 p-6 border-t border-dark-700 bg-dark-800/50"
      >
        <button class="btn-secondary" on:click={handleCancel}>
          {cancelText}
        </button>
        <button class={confirmButtonClass} on:click={handleConfirm}>
          {confirmText}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  /* 애니메이션 효과 */
  .fixed {
    animation: fadeIn 0.2s ease-out;
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  /* 다이얼로그 등장 애니메이션 */
  .bg-dark-900 {
    animation: slideUp 0.3s ease-out;
  }

  @keyframes slideUp {
    from {
      opacity: 0;
      transform: translateY(20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  /* 버튼 스타일 */
  .btn {
    @apply inline-flex items-center justify-center px-4 py-2 text-sm font-medium rounded-lg transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-dark-900;
  }
</style>
