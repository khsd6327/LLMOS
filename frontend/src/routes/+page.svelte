<!-- ted-os-project/frontend/src/routes/+page.svelte -->
<script lang="ts">
  import ChatSidebar from "$lib/components/features/chat/ChatSidebar.svelte";
  import ChatInterface from "$lib/components/features/chat/ChatInterface.svelte";
  import ModelSelector from "$lib/components/features/chat/ModelSelector.svelte";
  import AppLayout from "$lib/components/core/layout/AppLayout.svelte";
  import { currentSession } from "$lib/stores/chat";
</script>

<svelte:head>
  <title>Ted OS - AI Assistant</title>
</svelte:head>

<AppLayout>
  <!-- 사이드바 슬롯 -->
  <div slot="sidebar">
    <ChatSidebar />
  </div>

  <!-- 헤더 왼쪽: 모델 선택기 -->
  <div slot="header-left">
    <ModelSelector />
  </div>

  <!-- 헤더 중간: 채팅 제목 -->
  <div slot="header-center">
    {#if $currentSession}
      <div class="text-sm font-medium text-gray-900 truncate">
        {$currentSession.title}
      </div>
    {:else}
      <div class="text-sm font-medium text-gray-500">새 채팅</div>
    {/if}
  </div>

  <!-- 메인 채팅 인터페이스 -->
  <ChatInterface />
</AppLayout>
