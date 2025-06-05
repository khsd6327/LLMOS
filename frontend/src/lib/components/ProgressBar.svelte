<script lang="ts">
  export let progress: number = 0; // 0-100 사이의 값
  export let text: string = "";
  export let showPercentage: boolean = true;
  export let color: "primary" | "success" | "warning" | "error" | "info" =
    "primary";
  export let size: "sm" | "md" | "lg" = "md";
  export let variant: "default" | "striped" | "animated" = "default";
  export let indeterminate: boolean = false;

  // 진행률을 0-100 범위로 제한
  $: clampedProgress = Math.min(Math.max(progress, 0), 100);

  // 색상별 설정
  $: colorConfig = {
    primary: {
      bg: "bg-claude-orange",
      track: "bg-dark-700",
    },
    success: {
      bg: "bg-green-500",
      track: "bg-dark-700",
    },
    warning: {
      bg: "bg-yellow-500",
      track: "bg-dark-700",
    },
    error: {
      bg: "bg-red-500",
      track: "bg-dark-700",
    },
    info: {
      bg: "bg-blue-500",
      track: "bg-dark-700",
    },
  };

  $: currentColor = colorConfig[color];

  // 크기별 설정
  $: sizeConfig = {
    sm: { height: "h-1", text: "text-xs" },
    md: { height: "h-2", text: "text-sm" },
    lg: { height: "h-3", text: "text-base" },
  };

  $: currentSize = sizeConfig[size];
</script>

<div class="w-full space-y-2">
  <!-- 레이블과 퍼센티지 -->
  {#if text || showPercentage}
    <div class="flex items-center justify-between">
      {#if text}
        <span class="{currentSize.text} text-dark-300 font-medium">{text}</span>
      {/if}
      {#if showPercentage && !indeterminate}
        <span class="{currentSize.text} text-dark-400 font-mono">
          {clampedProgress.toFixed(0)}%
        </span>
      {/if}
    </div>
  {/if}

  <!-- 진행률 바 -->
  <div
    class="relative w-full {currentColor.track} rounded-full {currentSize.height} overflow-hidden"
  >
    {#if indeterminate}
      <!-- 무한 로딩 애니메이션 -->
      <div
        class="absolute inset-y-0 {currentColor.bg} rounded-full animate-pulse w-full opacity-60"
      />
      <div
        class="absolute inset-y-0 {currentColor.bg} rounded-full w-1/3 animate-indeterminate"
      />
    {:else}
      <!-- 일반 진행률 바 -->
      <div
        class="
            {currentColor.bg} 
            {currentSize.height} 
            rounded-full
            transition-all
            duration-500
            ease-out
            {variant === 'striped'
          ? 'bg-gradient-to-r from-transparent via-white/20 to-transparent bg-[length:1rem_100%]'
          : ''}
            {variant === 'animated' ? 'animate-pulse' : ''}
          "
        style="width: {clampedProgress}%"
      />
    {/if}

    <!-- 스트라이프 효과 (선택적) -->
    {#if variant === "striped"}
      <div
        class="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent bg-[length:1rem_100%] animate-slide"
      />
    {/if}
  </div>

  <!-- 상세 정보 (선택적) -->
  <slot name="details" />
</div>

<!-- 사용 예시 (주석):
  <ProgressBar progress={75} text="파일 업로드 중..." color="primary" size="md" />
  <ProgressBar progress={100} text="완료!" color="success" variant="striped" />
  <ProgressBar indeterminate={true} text="처리 중..." color="info" />
  -->

<style>
  /* 무한 진행률 애니메이션 */
  @keyframes indeterminate {
    0% {
      left: -35%;
      right: 100%;
    }
    60% {
      left: 100%;
      right: -90%;
    }
    100% {
      left: 100%;
      right: -90%;
    }
  }

  .animate-indeterminate {
    animation: indeterminate 2s cubic-bezier(0.65, 0.815, 0.735, 0.395) infinite;
  }

  /* 스트라이프 슬라이드 애니메이션 */
  @keyframes slide {
    0% {
      background-position: 0 0;
    }
    100% {
      background-position: 1rem 0;
    }
  }

  .animate-slide {
    animation: slide 1s linear infinite;
  }
</style>
