<script lang="ts">
  import "../app.css";
  import { onMount } from "svelte";
  import { api } from "$lib/api";
  import {
    sessions,
    usageStats,
    errorMessage,
    successMessage,
  } from "$lib/stores";
  import { showError } from "$lib/stores";
  import Sidebar from "$lib/components/Sidebar.svelte";
  import ErrorToast from "$lib/components/ErrorToast.svelte";
  import SuccessToast from "$lib/components/SuccessToast.svelte";

  // 앱 초기화
  onMount(async () => {
    try {
      // 세션 목록 로드
      const sessionsData = await api.getSessions();
      sessions.set(sessionsData);

      // 사용량 통계 로드
      const usageData = await api.getUsageStats();
      usageStats.set(usageData);
    } catch (error) {
      console.error("앱 초기화 실패:", error);
      showError("앱을 초기화하는 중 오류가 발생했습니다.");
    }
  });
</script>

<div class="flex h-screen bg-dark-950 text-dark-50">
  <!-- 사이드바 -->
  <Sidebar />

  <!-- 메인 콘텐츠 -->
  <main class="flex-1 flex flex-col overflow-hidden">
    <slot />
  </main>

  <!-- 알림 토스트 -->
  {#if $errorMessage}
    <ErrorToast message={$errorMessage} />
  {/if}

  {#if $successMessage}
    <SuccessToast message={$successMessage} />
  {/if}
</div>
