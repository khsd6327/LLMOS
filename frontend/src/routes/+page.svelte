<script lang="ts">
  import { onMount } from "svelte";
  import { currentSession, currentSessionId, sessions } from "$lib/stores";
  import PageRouter from "$lib/components/layout/PageRouter.svelte";

  onMount(() => {
    // 첫 번째 세션을 기본으로 선택
    if ($sessions.length > 0 && !$currentSession) {
      const firstSession = $sessions[0];
      currentSessionId.set(firstSession.id);
      currentSession.set(firstSession);
    }
  });
</script>

<svelte:head>
  <title>LLM OS - AI Assistant</title>
</svelte:head>

<!-- 페이지 라우터를 통해 다른 페이지들을 렌더링 -->
<PageRouter />
