<script lang="ts">
  import {
    CheckCircle,
    XCircle,
    AlertTriangle,
    Info,
    Clock,
    Loader2,
    Zap,
    Circle,
  } from "lucide-svelte";

  export let status:
    | "success"
    | "error"
    | "warning"
    | "info"
    | "loading"
    | "pending"
    | "active" = "info";
  export let message: string = "";
  export let showIcon: boolean = true;
  export let size: "sm" | "md" | "lg" = "md";
  export let variant: "badge" | "inline" | "card" = "inline";
  export let pulse: boolean = false;

  // 상태별 설정
  $: statusConfig = {
    success: {
      icon: CheckCircle,
      color: "text-green-400",
      bgColor: "bg-green-500/20",
      borderColor: "border-green-500/30",
      emoji: "✅",
    },
    error: {
      icon: XCircle,
      color: "text-red-400",
      bgColor: "bg-red-500/20",
      borderColor: "border-red-500/30",
      emoji: "❌",
    },
    warning: {
      icon: AlertTriangle,
      color: "text-yellow-400",
      bgColor: "bg-yellow-500/20",
      borderColor: "border-yellow-500/30",
      emoji: "⚠️",
    },
    info: {
      icon: Info,
      color: "text-blue-400",
      bgColor: "bg-blue-500/20",
      borderColor: "border-blue-500/30",
      emoji: "ℹ️",
    },
    loading: {
      icon: Loader2,
      color: "text-claude-orange",
      bgColor: "bg-claude-orange/20",
      borderColor: "border-claude-orange/30",
      emoji: "⏳",
    },
    pending: {
      icon: Clock,
      color: "text-purple-400",
      bgColor: "bg-purple-500/20",
      borderColor: "border-purple-500/30",
      emoji: "⏸️",
    },
    active: {
      icon: Zap,
      color: "text-claude-orange",
      bgColor: "bg-claude-orange/20",
      borderColor: "border-claude-orange/30",
      emoji: "⚡",
    },
  };

  $: config = statusConfig[status];

  // 크기별 설정
  $: sizeConfig = {
    sm: {
      icon: 14,
      text: "text-xs",
      padding: "px-2 py-1",
      spacing: "space-x-1",
    },
    md: {
      icon: 16,
      text: "text-sm",
      padding: "px-3 py-2",
      spacing: "space-x-2",
    },
    lg: {
      icon: 20,
      text: "text-base",
      padding: "px-4 py-3",
      spacing: "space-x-3",
    },
  };

  $: currentSize = sizeConfig[size];
</script>

{#if variant === "badge"}
  <!-- 배지 스타일 -->
  <span
    class="inline-flex items-center {currentSize.spacing} {currentSize.padding} {config.bgColor} {config.borderColor} border rounded-full {currentSize.text} font-medium"
  >
    {#if showIcon}
      <svelte:component
        this={config.icon}
        size={currentSize.icon}
        class="{config.color} {status === 'loading'
          ? 'animate-spin'
          : ''} {pulse ? 'animate-pulse' : ''}"
      />
    {:else}
      <span class={currentSize.text}>{config.emoji}</span>
    {/if}
    {#if message}
      <span class="text-dark-200">{message}</span>
    {/if}
  </span>
{:else if variant === "card"}
  <!-- 카드 스타일 -->
  <div
    class="flex items-center {currentSize.spacing} {currentSize.padding} {config.bgColor} {config.borderColor} border rounded-lg"
  >
    {#if showIcon}
      <svelte:component
        this={config.icon}
        size={currentSize.icon}
        class="{config.color} {status === 'loading'
          ? 'animate-spin'
          : ''} {pulse ? 'animate-pulse' : ''} flex-shrink-0"
      />
    {:else}
      <span class="{currentSize.text} flex-shrink-0">{config.emoji}</span>
    {/if}
    {#if message}
      <span class="{currentSize.text} text-dark-200 font-medium">{message}</span
      >
    {/if}
  </div>
{:else}
  <!-- 인라인 스타일 (기본) -->
  <div
    class="inline-flex items-center {currentSize.spacing} {currentSize.text}"
  >
    {#if showIcon}
      <svelte:component
        this={config.icon}
        size={currentSize.icon}
        class="{config.color} {status === 'loading'
          ? 'animate-spin'
          : ''} {pulse ? 'animate-pulse' : ''}"
      />
    {:else}
      <span>{config.emoji}</span>
    {/if}
    {#if message}
      <span class="text-dark-200 font-medium">{message}</span>
    {/if}
  </div>
{/if}

<!-- 사용 예시 (주석):
  <StatusIndicator status="success" message="설정이 저장되었습니다" variant="badge" />
  <StatusIndicator status="loading" message="처리 중..." variant="card" size="lg" />
  <StatusIndicator status="error" message="오류가 발생했습니다" variant="inline" pulse={true} />
  -->
