<script lang="ts">
  import { onMount } from "svelte";
  import {
    currentSession,
    currentSessionId,
    sessions,
    isGenerating,
  } from "$lib/stores";
  import { api } from "$lib/api";
  import { showError, showSuccess } from "$lib/stores";
  import ChatHeader from "./ChatHeader.svelte";
  import MessageList from "./MessageList.svelte";
  import ChatInput from "./ChatInput.svelte";
  import WelcomeScreen from "./WelcomeScreen.svelte";

  let chatContainer: HTMLElement;

  // 새 채팅 생성
  async function createNewChat() {
    try {
      const newSession = await api.createSession();

      // 세션 목록 업데이트
      sessions.update((list) => [newSession, ...list]);

      // 새 세션으로 전환
      currentSessionId.set(newSession.id);
      currentSession.set(newSession);

      showSuccess("새 채팅이 생성되었습니다.");
    } catch (error) {
      console.error("새 채팅 생성 실패:", error);
      showError("새 채팅을 생성할 수 없습니다.");
    }
  }

  // 스크롤을 맨 아래로
  function scrollToBottom() {
    if (chatContainer) {
      chatContainer.scrollTop = chatContainer.scrollHeight;
    }
  }

  // 메시지 재생성 처리
  async function handleRegenerate() {
    if (!$currentSession || $isGenerating) return;

    try {
      // 마지막 AI 메시지 제거
      const updatedMessages = $currentSession.messages.filter(
        (_, index) =>
          index !== $currentSession.messages.length - 1 ||
          $currentSession.messages[index].role !== "assistant"
      );

      const updatedSession = {
        ...$currentSession,
        messages: updatedMessages,
      };

      currentSession.set(updatedSession);
      sessions.update((list) =>
        list.map((s) => (s.id === updatedSession.id ? updatedSession : s))
      );

      // 마지막 사용자 메시지 찾기
      const lastUserMessage = updatedMessages
        .filter((msg) => msg.role === "user")
        .pop();

      if (lastUserMessage) {
        // AI 응답 재생성
        $isGenerating = true;

        for await (const chunk of api.sendMessage(
          $currentSession.id,
          typeof lastUserMessage.content === "string"
            ? lastUserMessage.content
            : lastUserMessage.content.find((part) => part.type === "text")
                ?.text || ""
          // 현재 선택된 모델 사용
        )) {
          // 스트리밍 처리는 ChatInput에서와 동일
        }
      }
    } catch (error) {
      console.error("응답 재생성 실패:", error);
      showError("응답을 재생성할 수 없습니다.");
    } finally {
      $isGenerating = false;
    }
  }

  // 세션이 변경되거나 새 메시지가 추가될 때 스크롤
  $: if ($currentSession) {
    setTimeout(scrollToBottom, 100);
  }

  onMount(() => {
    // 첫 번째 세션을 기본으로 선택 (사이드바에서 처리됨)
  });
</script>

<div class="flex flex-col h-full">
  <!-- 채팅 헤더 -->
  <ChatHeader {createNewChat} />

  <!-- 채팅 내용 -->
  <div class="flex-1 flex flex-col overflow-hidden">
    {#if $currentSession}
      <!-- 메시지 목록 -->
      <div bind:this={chatContainer} class="flex-1 overflow-y-auto">
        <MessageList
          session={$currentSession}
          on:regenerate={handleRegenerate}
        />
      </div>

      <!-- 채팅 입력 -->
      <div class="border-t border-dark-700 bg-dark-900/50 backdrop-blur-sm">
        <ChatInput {scrollToBottom} />
      </div>
    {:else}
      <!-- 환영 화면 -->
      <WelcomeScreen {createNewChat} />
    {/if}
  </div>
</div>
