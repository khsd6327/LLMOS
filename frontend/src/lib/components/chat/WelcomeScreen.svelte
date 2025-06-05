<!-- ted-os-project/frontend/src/lib/components/chat/WelcomeScreen.svelte -->
<script lang="ts">
  import { selectedProvider, selectedModel, sessions } from "$lib/stores";
  import { getModelConfig } from "$lib/models";
  import { MessageSquare, Zap, Brain, Code, Image, Star } from "lucide-svelte";

  export let createNewChat: () => void;

  // 현재 선택된 모델 정보
  $: currentModel = getModelConfig($selectedProvider, $selectedModel);

  // 예시 프롬프트들
  const examplePrompts = [
    {
      icon: Code,
      title: "코딩 도움",
      prompt: "Python으로 간단한 웹 크롤러를 만들어줘",
      category: "개발",
    },
    {
      icon: Brain,
      title: "창의적 글쓰기",
      prompt: "미래의 AI 세상을 배경으로 한 단편소설을 써줘",
      category: "창작",
    },
    {
      icon: MessageSquare,
      title: "일반 대화",
      prompt: "오늘 하루 어떻게 보냈어? 재미있는 이야기 들려줘",
      category: "대화",
    },
    {
      icon: Zap,
      title: "문제 해결",
      prompt: "프로젝트 관리를 효율적으로 하는 방법을 알려줘",
      category: "생산성",
    },
  ];

  // 최근 세션 통계
  $: recentSessions = $sessions.slice(0, 3);
  $: totalMessages = $sessions.reduce(
    (sum, session) => sum + session.messages.length,
    0
  );

  // 예시 프롬프트로 채팅 시작
  async function startWithPrompt(prompt: string) {
    await createNewChat();
    // 프롬프트를 입력창에 설정하는 로직은 ChatInput 컴포넌트에서 처리
    // 여기서는 단순히 새 채팅만 생성
  }
</script>

<div
  class="flex-1 flex flex-col items-center justify-center p-8 bg-gradient-to-br from-dark-950 to-dark-900"
>
  <div class="max-w-4xl w-full space-y-8">
    <!-- 메인 헤더 -->
    <div class="text-center space-y-4">
      <div
        class="w-20 h-20 bg-gradient-to-br from-claude-orange to-claude-blue rounded-full mx-auto flex items-center justify-center shadow-2xl"
      >
        <svg
          class="w-10 h-10 text-white"
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"
          />
        </svg>
      </div>

      <div>
        <h1 class="text-4xl font-bold text-gradient mb-2">
          LLM OS에 오신 것을 환영합니다
        </h1>
        <p class="text-lg text-dark-400 max-w-2xl mx-auto">
          강력한 AI 모델들과 대화하고, 창작하고, 문제를 해결하세요. 지금 바로
          새로운 대화를 시작해보세요.
        </p>
      </div>
    </div>

    <!-- 현재 모델 정보 -->
    {#if currentModel}
      <div
        class="bg-dark-800/50 rounded-xl p-6 border border-dark-700/50 text-center"
      >
        <div class="flex items-center justify-center space-x-2 mb-2">
          <span class="text-sm text-dark-400">현재 선택된 모델:</span>
          <span class="text-lg font-semibold text-claude-orange">
            {currentModel.display_name}
          </span>
        </div>
        <p class="text-sm text-dark-500 max-w-md mx-auto">
          {currentModel.description}
        </p>

        <!-- 모델 기능 배지 -->
        <div class="flex items-center justify-center space-x-2 mt-3">
          {#if currentModel.supports_streaming}
            <span
              class="px-2 py-1 bg-green-500/20 text-green-400 text-xs rounded-full"
              >스트리밍</span
            >
          {/if}
          {#if currentModel.supports_vision}
            <span
              class="px-2 py-1 bg-blue-500/20 text-blue-400 text-xs rounded-full"
              >이미지</span
            >
          {/if}
          {#if currentModel.supports_functions}
            <span
              class="px-2 py-1 bg-purple-500/20 text-purple-400 text-xs rounded-full"
              >함수 호출</span
            >
          {/if}
        </div>
      </div>
    {/if}

    <!-- 예시 프롬프트 -->
    <div class="space-y-4">
      <h2 class="text-xl font-semibold text-dark-200 text-center">
        무엇을 도와드릴까요?
      </h2>

      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        {#each examplePrompts as example}
          <button
            class="card-hover p-6 text-left group transition-all duration-200 hover:scale-[1.02]"
            on:click={() => startWithPrompt(example.prompt)}
          >
            <div class="flex items-start space-x-4">
              <div
                class="w-10 h-10 bg-dark-700 rounded-lg flex items-center justify-center group-hover:bg-claude-orange/20 transition-colors"
              >
                <svelte:component
                  this={example.icon}
                  size={20}
                  class="text-dark-400 group-hover:text-claude-orange"
                />
              </div>

              <div class="flex-1">
                <div class="flex items-center justify-between mb-2">
                  <h3
                    class="font-medium text-dark-200 group-hover:text-dark-100"
                  >
                    {example.title}
                  </h3>
                  <span
                    class="text-xs text-dark-500 bg-dark-700 px-2 py-1 rounded"
                  >
                    {example.category}
                  </span>
                </div>

                <p
                  class="text-sm text-dark-400 group-hover:text-dark-300 line-clamp-2"
                >
                  "{example.prompt}"
                </p>
              </div>
            </div>
          </button>
        {/each}
      </div>
    </div>

    <!-- 새 채팅 시작 버튼 -->
    <div class="text-center">
      <button
        class="btn-primary text-lg px-8 py-4 shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-200"
        on:click={createNewChat}
      >
        <MessageSquare size={20} class="mr-2" />
        새 채팅 시작하기
      </button>
    </div>

    <!-- 통계 정보 (세션이 있을 때만) -->
    {#if $sessions.length > 0}
      <div class="border-t border-dark-800 pt-8">
        <h3 class="text-lg font-medium text-dark-300 text-center mb-4">
          최근 활동
        </h3>

        <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
          <!-- 총 대화 수 -->
          <div class="text-center">
            <div class="text-2xl font-bold text-claude-orange">
              {$sessions.length}
            </div>
            <div class="text-sm text-dark-400">총 대화</div>
          </div>

          <!-- 총 메시지 수 -->
          <div class="text-center">
            <div class="text-2xl font-bold text-claude-blue">
              {totalMessages}
            </div>
            <div class="text-sm text-dark-400">총 메시지</div>
          </div>

          <!-- 고정된 대화 수 -->
          <div class="text-center">
            <div class="text-2xl font-bold text-accent-500">
              {$sessions.filter((s) => s.is_pinned).length}
            </div>
            <div class="text-sm text-dark-400">고정된 대화</div>
          </div>
        </div>

        <!-- 최근 대화 목록 -->
        {#if recentSessions.length > 0}
          <div class="mt-6">
            <h4 class="text-sm font-medium text-dark-400 mb-3 text-center">
              최근 대화
            </h4>
            <div class="space-y-2">
              {#each recentSessions as session}
                <button
                  class="w-full text-left p-3 bg-dark-800/30 hover:bg-dark-800/50 rounded-lg transition-colors border border-dark-700/30"
                  on:click={() => {
                    // 세션 선택 로직은 부모에서 처리
                    // 여기서는 단순히 표시만
                  }}
                >
                  <div class="flex items-center justify-between">
                    <span class="text-sm text-dark-200 truncate">
                      {session.title}
                    </span>
                    <div class="flex items-center space-x-2">
                      {#if session.is_pinned}
                        <Star size={12} class="text-accent-500" />
                      {/if}
                      <span class="text-xs text-dark-500">
                        {session.messages.length}개 메시지
                      </span>
                    </div>
                  </div>
                </button>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    {/if}
  </div>
</div>

<style>
  .line-clamp-2 {
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }
</style>
