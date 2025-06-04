<script lang="ts">
  import { onMount, afterUpdate } from "svelte";
  import type { ChatSession } from "$lib/api";
  import MessageItem from "./MessageItem.svelte";
  import TypingIndicator from "./TypingIndicator.svelte";
  import { isGenerating, streamingMessage } from "$lib/stores";

  export let session: ChatSession;

  let messagesContainer: HTMLElement;
  let isAtBottom = true;

  // 메시지가 추가되거나 스트리밍 중일 때 자동 스크롤
  function scrollToBottom(smooth = true) {
    if (messagesContainer && isAtBottom) {
      messagesContainer.scrollTo({
        top: messagesContainer.scrollHeight,
        behavior: smooth ? "smooth" : "auto",
      });
    }
  }

  // 스크롤 위치 감지
  function handleScroll() {
    if (!messagesContainer) return;

    const { scrollTop, scrollHeight, clientHeight } = messagesContainer;
    isAtBottom = scrollTop + clientHeight >= scrollHeight - 10;
  }

  // 메시지가 변경될 때마다 스크롤
  $: if (session?.messages) {
    setTimeout(() => scrollToBottom(), 100);
  }

  // 스트리밍 메시지가 업데이트될 때마다 스크롤
  $: if ($streamingMessage) {
    setTimeout(() => scrollToBottom(), 50);
  }

  afterUpdate(() => {
    if (isAtBottom) {
      scrollToBottom(false);
    }
  });
</script>

<div
  bind:this={messagesContainer}
  on:scroll={handleScroll}
  class="flex-1 overflow-y-auto space-y-6 px-4 py-6"
>
  {#if session.messages.length === 0}
    <!-- 빈 상태 -->
    <div
      class="flex flex-col items-center justify-center h-full text-center py-12"
    >
      <div
        class="w-16 h-16 bg-dark-800 rounded-full flex items-center justify-center mb-4"
      >
        <svg
          class="w-8 h-8 text-dark-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
      </div>
      <h3 class="text-lg font-medium text-dark-200 mb-2">
        새로운 대화를 시작하세요
      </h3>
      <p class="text-dark-400 max-w-md">
        아래에 메시지를 입력하여 AI와 대화를 시작할 수 있습니다. 질문하거나
        도움이 필요한 작업에 대해 물어보세요.
      </p>
    </div>
  {:else}
    <!-- 메시지 목록 -->
    {#each session.messages as message, index (index)}
      <MessageItem
        {message}
        {index}
        {session}
        isLast={index === session.messages.length - 1}
      />
    {/each}

    <!-- AI 스트리밍 응답 -->
    {#if $isGenerating}
      <div class="flex space-x-3">
        <div
          class="w-8 h-8 bg-gradient-to-br from-claude-orange to-claude-blue rounded-full flex items-center justify-center flex-shrink-0"
        >
          <svg
            class="w-4 h-4 text-white"
            fill="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
            />
          </svg>
        </div>

        <div class="flex-1 space-y-2">
          {#if $streamingMessage}
            <!-- 스트리밍 중인 메시지 -->
            <div
              class="bg-dark-900/50 rounded-xl p-4 border border-dark-700/50"
            >
              <div class="prose prose-invert max-w-none">
                {$streamingMessage}<span class="animate-typing">▌</span>
              </div>
            </div>
          {:else}
            <!-- 타이핑 인디케이터 -->
            <div
              class="bg-dark-900/50 rounded-xl p-4 border border-dark-700/50"
            >
              <TypingIndicator />
            </div>
          {/if}

          <div class="text-xs text-dark-500">
            AI가 응답을 생성하고 있습니다...
          </div>
        </div>
      </div>
    {/if}
  {/if}
</div>

<!-- 스크롤 하단으로 이동 버튼 -->
{#if !isAtBottom && session.messages.length > 0}
  <button
    class="fixed bottom-24 right-8 w-10 h-10 bg-dark-800 hover:bg-dark-700 border border-dark-600 rounded-full flex items-center justify-center shadow-lg transition-all duration-200 z-10"
    on:click={() => scrollToBottom()}
  >
    <svg
      class="w-5 h-5 text-dark-300"
      fill="none"
      stroke="currentColor"
      viewBox="0 0 24 24"
    >
      <path
        stroke-linecap="round"
        stroke-linejoin="round"
        stroke-width="2"
        d="M19 14l-7 7m0 0l-7-7m7 7V3"
      />
    </svg>
  </button>
{/if}
