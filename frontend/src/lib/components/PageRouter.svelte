<script lang="ts">
  import { currentPage } from "$lib/stores";
  import ChatPage from "./ChatPage.svelte";
  import FavoritesPage from "./FavoritesPage.svelte";
  import UsagePage from "./UsagePage.svelte";
  import SettingsPage from "./SettingsPage.svelte";
  import { fade, slide } from "svelte/transition";

  // 페이지 전환 애니메이션 옵션
  const transitionOptions = {
    duration: 200,
    delay: 0,
  };
</script>

<!-- 페이지 라우터 - currentPage에 따라 다른 컴포넌트 렌더링 -->
<div class="flex-1 flex flex-col overflow-hidden">
  {#if $currentPage === "chat"}
    <div
      in:fade={transitionOptions}
      out:fade={{ duration: 100 }}
      class="flex-1 flex flex-col overflow-hidden"
    >
      <ChatPage />
    </div>
  {:else if $currentPage === "favorites"}
    <div
      in:fade={transitionOptions}
      out:fade={{ duration: 100 }}
      class="flex-1 flex flex-col overflow-hidden"
    >
      <FavoritesPage />
    </div>
  {:else if $currentPage === "usage"}
    <div
      in:fade={transitionOptions}
      out:fade={{ duration: 100 }}
      class="flex-1 flex flex-col overflow-hidden"
    >
      <UsagePage />
    </div>
  {:else if $currentPage === "settings"}
    <div
      in:fade={transitionOptions}
      out:fade={{ duration: 100 }}
      class="flex-1 flex flex-col overflow-hidden"
    >
      <SettingsPage />
    </div>
  {:else}
    <!-- 기본 페이지 (채팅) -->
    <div
      in:fade={transitionOptions}
      class="flex-1 flex flex-col overflow-hidden"
    >
      <ChatPage />
    </div>
  {/if}
</div>
