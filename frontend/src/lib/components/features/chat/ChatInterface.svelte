<!-- ted-os-project/frontend/src/lib/components/features/chat/ChatInterface.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import ModelSelector from "./ModelSelector.svelte";
  import {
    currentSession,
    selectedModel,
    isLoading,
    error,
    chatStore,
  } from "$lib/stores/chat";

  let inputMessage = "";
  let messagesContainer: HTMLElement;
  let isStreaming = false;

  // 현재 세션과 메시지들
  $: messages = $currentSession?.messages || [];
  $: isInitialState = !$currentSession || messages.length === 0;

  // 메시지가 업데이트될 때마다 스크롤을 맨 아래로
  $: if (messages && messagesContainer) {
    setTimeout(() => {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }, 50);
  }

  async function sendMessage() {
    if (!inputMessage.trim() || isStreaming) return;

    // 세션이 없으면 새로 생성
    if (!$currentSession) {
      try {
        await chatStore.createSession();
      } catch (err) {
        console.error("세션 생성 실패:", err);
        return;
      }
    }

    const messageToSend = inputMessage;
    inputMessage = ""; // 입력창 즉시 초기화
    isStreaming = true;

    try {
      await chatStore.sendMessage(messageToSend, (chunk) => {
        // 스트리밍 청크 처리 (이미 스토어에서 처리됨)
        console.log("수신 청크:", chunk);
      });
    } catch (err) {
      console.error("메시지 전송 실패:", err);
      // 에러 발생 시 입력 메시지 복원
      inputMessage = messageToSend;
    } finally {
      isStreaming = false;
    }
  }

  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage();
    }
  }

  function formatTimestamp(timestamp?: string) {
    if (!timestamp) return "";
    const date = new Date(timestamp);
    return date.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
      hour12: true, // 오전/오후 표시
    });
  }
</script>

<div class="h-full flex flex-col {isInitialState ? 'relative' : ''}">
  <!-- 메시지 영역 -->
  <div class="flex-1 overflow-hidden">
    {#if isInitialState}
      <!-- 초기 상태: 중앙에 환영 메시지 -->
      <div class="h-full flex items-center justify-center">
        <div class="text-center space-y-4 max-w-md">
          <h1 class="text-2xl font-semibold text-gray-900">
            어떻게 도와드릴까요?
          </h1>
          <p class="text-gray-500">궁금한 것이 있으면 무엇이든 물어보세요.</p>

          <!-- 선택된 모델 표시 -->
          <div class="mt-6 p-3 bg-gray-50 rounded-lg">
            <div class="text-sm text-gray-600">현재 선택된 모델:</div>
            <div class="font-medium text-gray-900">
              {$selectedModel.display}
            </div>
          </div>
        </div>
      </div>
    {:else}
      <!-- 채팅 메시지들 -->
      <div
        bind:this={messagesContainer}
        class="h-full overflow-y-auto p-4 space-y-4"
      >
        {#each messages as message, index}
          <div
            class="flex {message.role === 'user'
              ? 'justify-end'
              : 'justify-start'}"
          >
            <div
              class="max-w-3xl {message.role === 'user'
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-900'} 
                rounded-lg px-4 py-3 relative group"
            >
              <!-- 메시지 내용 -->
              <div class="whitespace-pre-wrap break-words">
                {#if typeof message.content === "string"}
                  {message.content}
                {:else}
                  {JSON.stringify(message.content)}
                {/if}
              </div>

              <!-- 타임스탬프와 모델명 -->
              {#if message.timestamp}
                <div class="text-xs opacity-60 mt-1">
                  {formatTimestamp(message.timestamp)}
                  {#if message.role === "assistant"}
                    - {$selectedModel.display}
                  {/if}
                </div>
              {/if}

              <!-- 스트리밍 중 표시 -->
              {#if message.role === "assistant" && index === messages.length - 1 && isStreaming}
                <div class="flex items-center mt-2">
                  <div class="animate-pulse text-xs opacity-60">
                    AI가 응답 중...
                  </div>
                </div>
              {/if}
            </div>
          </div>
        {/each}

        <!-- 로딩 상태 -->
        {#if $isLoading && !isStreaming}
          <div class="flex justify-start">
            <div class="bg-gray-100 text-gray-900 rounded-lg px-4 py-3">
              <div class="flex items-center space-x-2">
                <div
                  class="animate-spin w-4 h-4 border-2 border-gray-400 border-t-transparent rounded-full"
                />
                <span>처리 중...</span>
              </div>
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>

  <!-- 에러 표시 -->
  {#if $error}
    <div class="px-4 py-2 bg-red-50 border-t border-red-200">
      <div class="text-red-800 text-sm">{$error}</div>
    </div>
  {/if}

  <!-- 입력 영역 -->
  <div
    class="p-4 border-t border-gray-200 {isInitialState
      ? 'absolute bottom-0 left-0 right-0'
      : ''}"
  >
    <div class="flex space-x-2">
      <textarea
        bind:value={inputMessage}
        on:keydown={handleKeydown}
        placeholder="메시지를 입력하세요... (Enter: 전송, Shift+Enter: 줄바꿈)"
        class="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-500 focus:border-transparent resize-none"
        rows="1"
        style="max-height: 200px; min-height: 48px;"
        disabled={isStreaming}
      />
      <button
        on:click={sendMessage}
        disabled={!inputMessage.trim() || isStreaming}
        class="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
      >
        {#if isStreaming}
          <div
            class="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"
          />
          <span>전송 중</span>
        {:else}
          <span>전송</span>
        {/if}
      </button>
    </div>
  </div>
</div>
