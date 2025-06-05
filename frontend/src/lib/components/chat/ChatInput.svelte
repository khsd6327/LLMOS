<script lang="ts">
  import {
    currentSession,
    sessions,
    isGenerating,
    streamingMessage,
    selectedProvider,
    selectedModel,
    temperature,
    maxTokens,
  } from "$lib/stores";
  import { api } from "$lib/api";
  import { showError, showSuccess } from "$lib/stores";
  import { Send, Square, Paperclip, Image } from "lucide-svelte";

  export let scrollToBottom: () => void;

  let inputText = "";
  let inputElement: HTMLTextAreaElement;
  let isComposing = false;
  let uploadedImage: File | null = null;
  let imagePreview: string | null = null;

  // 윈도우 클릭 핸들러
  function handleWindowClick(e: Event) {
    const target = e.target as HTMLElement;
    if (target.closest(".chat-input-focus-area") && !$isGenerating) {
      focusInput();
    }
  }

  // 메시지 전송
  async function sendMessage() {
    if (!inputText.trim() || !$currentSession || $isGenerating) return;

    const messageText = inputText.trim();
    inputText = "";

    // 사용자 메시지를 세션에 추가
    const userMessage = {
      role: "user" as const,
      content: messageText,
      timestamp: new Date().toISOString(),
    };

    const updatedSession = {
      ...$currentSession,
      messages: [...$currentSession.messages, userMessage],
    };

    currentSession.set(updatedSession);
    sessions.update((list) =>
      list.map((s) => (s.id === updatedSession.id ? updatedSession : s))
    );

    // 스크롤을 아래로
    setTimeout(scrollToBottom, 100);

    // AI 응답 생성 시작
    isGenerating.set(true);
    streamingMessage.set("");

    try {
      let fullResponse = "";

      // 스트리밍 응답 처리
      for await (const chunk of api.sendMessage(
        $currentSession.id,
        messageText,
        $selectedProvider,
        $selectedModel
      )) {
        fullResponse += chunk;
        streamingMessage.set(fullResponse);
        setTimeout(scrollToBottom, 50);
      }

      // 완료된 응답을 세션에 추가
      if (fullResponse) {
        const aiMessage = {
          role: "assistant" as const,
          content: fullResponse,
          model_provider: $selectedProvider,
          model_name: $selectedModel,
          timestamp: new Date().toISOString(),
        };

        const finalSession = {
          ...updatedSession,
          messages: [...updatedSession.messages, aiMessage],
        };

        currentSession.set(finalSession);
        sessions.update((list) =>
          list.map((s) => (s.id === finalSession.id ? finalSession : s))
        );
      }
    } catch (error) {
      console.error("메시지 전송 실패:", error);
      showError("메시지를 전송할 수 없습니다.");
    } finally {
      isGenerating.set(false);
      streamingMessage.set("");
      setTimeout(scrollToBottom, 100);
    }
  }

  // 생성 중단
  function stopGeneration() {
    isGenerating.set(false);
    streamingMessage.set("");
    showSuccess("AI 응답 생성이 중단되었습니다.");
  }

  // 텍스트영역 자동 크기 조절
  function autoResize() {
    if (inputElement) {
      inputElement.style.height = "auto";
      inputElement.style.height =
        Math.min(inputElement.scrollHeight, 200) + "px";
    }
  }

  // 키보드 이벤트 처리
  function handleKeydown(event: KeyboardEvent) {
    if (event.key === "Enter" && !event.shiftKey && !isComposing) {
      event.preventDefault();
      sendMessage();
    }
  }

  // 이미지 업로드 처리
  function handleImageUpload(event: Event) {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];

    if (file) {
      if (file.size > 10 * 1024 * 1024) {
        // 10MB 제한
        showError("이미지 크기는 10MB 이하여야 합니다.");
        return;
      }

      if (!file.type.startsWith("image/")) {
        showError("이미지 파일만 업로드할 수 있습니다.");
        return;
      }

      uploadedImage = file;

      // 이미지 미리보기 생성
      const reader = new FileReader();
      reader.onload = (e) => {
        imagePreview = e.target?.result as string;
      };
      reader.readAsDataURL(file);
    }
  }

  // 이미지 제거
  function removeImage() {
    uploadedImage = null;
    imagePreview = null;
  }

  // 입력창 포커스
  function focusInput() {
    if (inputElement) {
      inputElement.focus();
    }
  }

  // 플레이스홀더 텍스트
  $: placeholder = $isGenerating
    ? "AI가 응답하고 있습니다..."
    : "메시지를 입력하세요... (Shift+Enter로 줄바꿈)";
</script>

<div class="p-4 space-y-3">
  <!-- 이미지 미리보기 -->
  {#if imagePreview}
    <div class="relative inline-block">
      <img
        src={imagePreview}
        alt="업로드된 이미지"
        class="max-h-32 rounded-lg border border-dark-600"
      />
      <button
        class="absolute -top-2 -right-2 w-6 h-6 bg-red-500 hover:bg-red-600 text-white rounded-full flex items-center justify-center text-xs transition-colors"
        on:click={removeImage}
      >
        ×
      </button>
    </div>
  {/if}

  <!-- 메인 입력 영역 -->
  <div class="relative">
    <div class="flex items-end space-x-3">
      <!-- 파일 업로드 버튼 -->
      <div class="relative">
        <input
          type="file"
          accept="image/*"
          on:change={handleImageUpload}
          class="hidden"
          id="image-upload"
          disabled={$isGenerating}
        />
        <label
          for="image-upload"
          class="btn-icon cursor-pointer {$isGenerating
            ? 'opacity-50 cursor-not-allowed'
            : ''}"
          title="이미지 업로드"
        >
          <Image size={20} />
        </label>
      </div>

      <!-- 텍스트 입력 영역 -->
      <div class="flex-1 relative">
        <textarea
          bind:this={inputElement}
          bind:value={inputText}
          on:input={autoResize}
          on:keydown={handleKeydown}
          on:compositionstart={() => (isComposing = true)}
          on:compositionend={() => (isComposing = false)}
          {placeholder}
          disabled={$isGenerating}
          rows="1"
          class="w-full bg-dark-800 border border-dark-600 rounded-xl px-4 py-3 pr-12 text-dark-100 placeholder-dark-400 resize-none focus:outline-none focus:ring-2 focus:ring-claude-orange/50 focus:border-claude-orange/50 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
          style="min-height: 48px; max-height: 200px;"
        />

        <!-- 전송/중단 버튼 -->
        <div class="absolute right-2 bottom-2">
          {#if $isGenerating}
            <button
              class="w-8 h-8 bg-red-600 hover:bg-red-700 text-white rounded-lg flex items-center justify-center transition-colors duration-200"
              on:click={stopGeneration}
              title="생성 중단"
            >
              <Square size={16} />
            </button>
          {:else}
            <button
              class="w-8 h-8 bg-claude-orange hover:bg-claude-orange/90 text-white rounded-lg flex items-center justify-center transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
              on:click={sendMessage}
              disabled={!inputText.trim()}
              title="메시지 전송"
            >
              <Send size={16} />
            </button>
          {/if}
        </div>
      </div>
    </div>

    <!-- 입력 힌트 -->
    <div class="flex justify-between items-center mt-2 text-xs text-dark-500">
      <div class="flex items-center space-x-4">
        <span>Enter: 전송</span>
        <span>Shift+Enter: 줄바꿈</span>
        {#if uploadedImage}
          <span class="text-claude-orange">📎 이미지 첨부됨</span>
        {/if}
      </div>

      <!-- 현재 설정 표시 -->
      <div class="flex items-center space-x-2">
        <span title="현재 모델">{$selectedProvider}/{$selectedModel}</span>
        <span title="Temperature">🌡️{$temperature}</span>
        <span title="Max Tokens">📝{$maxTokens}</span>
      </div>
    </div>
  </div>
</div>

<!-- 빠른 액션 클릭으로 입력창 포커스 -->
<svelte:window on:click={handleWindowClick} />
