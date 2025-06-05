<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api";
  import { showError, showSuccess } from "$lib/stores";
  import StatusIndicator from "../ui/StatusIndicator.svelte";
  import LoadingSpinner from "../ui/LoadingSpinner.svelte";
  import {
    RefreshCw,
    TestTube,
    CheckCircle,
    XCircle,
    AlertTriangle,
    Zap,
    Eye,
    EyeOff,
    Settings,
  } from "lucide-svelte";

  export let showTestButtons: boolean = true;
  export let showDetails: boolean = true;
  export let keySuffix: string = "";

  let loading = false;
  let validationResult: any = {};
  let statusSummary = {
    total_providers: 0,
    active_providers: 0,
    errors: 0,
    warnings: 0,
  };

  // 각 제공업체별 테스트 상태
  let testingStates: Record<string, boolean> = {};

  // 제공업체 상태 로드
  async function loadProviderStatus() {
    loading = true;
    try {
      // 실제 구현에서는 백엔드 API 호출
      // const result = await api.validateConfiguration();

      // 임시 데이터 (실제로는 백엔드에서 받아야 함)
      validationResult = {
        valid: true,
        errors: [],
        warnings: ["일부 제공업체에서 API 할당량이 부족할 수 있습니다"],
        provider_status: {
          openai: {
            has_api_key: true,
            interface_initialized: true,
            available_models: 8,
            supported_features: {
              streaming: true,
              functions: true,
              vision: true,
            },
          },
          anthropic: {
            has_api_key: true,
            interface_initialized: true,
            available_models: 4,
            supported_features: {
              streaming: true,
              functions: true,
              vision: false,
            },
          },
          google: {
            has_api_key: false,
            interface_initialized: false,
            available_models: 0,
            supported_features: {
              streaming: false,
              functions: false,
              vision: false,
            },
          },
        },
      };

      // 상태 요약 계산
      const providers = Object.values(validationResult.provider_status);
      statusSummary = {
        total_providers: providers.length,
        active_providers: providers.filter(
          (p: any) => p.has_api_key && p.interface_initialized
        ).length,
        errors: validationResult.errors.length,
        warnings: validationResult.warnings.length,
      };
    } catch (error) {
      console.error("제공업체 상태 로드 실패:", error);
      showError("제공업체 상태를 불러올 수 없습니다.");
    } finally {
      loading = false;
    }
  }

  // API 연결 테스트
  async function testApiConnection(provider: string) {
    testingStates[provider] = true;

    try {
      // 실제 구현에서는 백엔드 API 호출
      // const result = await api.testProviderConnection(provider);

      // 임시 지연 (실제 테스트 시뮬레이션)
      await new Promise((resolve) => setTimeout(resolve, 2000));

      showSuccess(`✅ ${formatProviderName(provider)} API 연결 성공!`);
    } catch (error) {
      showError(`❌ ${formatProviderName(provider)} API 연결 실패: ${error}`);
    } finally {
      testingStates[provider] = false;
    }
  }

  // 제공업체 이름 포맷팅
  function formatProviderName(provider: string): string {
    const names: Record<string, string> = {
      openai: "OpenAI",
      anthropic: "Anthropic",
      google: "Google AI",
    };
    return names[provider] || provider.toUpperCase();
  }

  // 상태 아이콘 및 텍스트 결정
  function getProviderStatus(status: any) {
    if (status.has_api_key && status.interface_initialized) {
      return { icon: "success", text: "정상", color: "text-green-400" };
    } else if (status.has_api_key && !status.interface_initialized) {
      return { icon: "error", text: "인터페이스 오류", color: "text-red-400" };
    } else {
      return { icon: "warning", text: "미설정", color: "text-yellow-400" };
    }
  }

  onMount(() => {
    loadProviderStatus();
  });
</script>

<div class="space-y-6">
  <!-- 헤더 -->
  <div class="flex items-center justify-between">
    <div class="flex items-center space-x-3">
      <Settings size={24} class="text-claude-orange" />
      <div>
        <h2 class="text-xl font-bold text-dark-100">🔌 AI 제공업체 상태</h2>
        <p class="text-dark-400 text-sm">
          각 AI 제공업체의 API 키 및 연결 상태를 확인합니다
        </p>
      </div>
    </div>

    <button
      class="btn-secondary {loading ? 'animate-spin' : ''}"
      on:click={loadProviderStatus}
      disabled={loading}
    >
      <RefreshCw size={16} class="mr-2" />
      상태 새로고침
    </button>
  </div>

  {#if loading}
    <LoadingSpinner text="제공업체 상태를 확인하는 중..." size="lg" />
  {:else}
    <!-- 전체 상태 요약 -->
    <div class="grid grid-cols-4 gap-4">
      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-dark-100">
          {statusSummary.total_providers}
        </div>
        <div class="text-sm text-dark-400">총 제공업체</div>
      </div>
      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-green-400">
          {statusSummary.active_providers}
        </div>
        <div class="text-sm text-dark-400">활성 제공업체</div>
      </div>
      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-red-400">
          {statusSummary.errors}
        </div>
        <div class="text-sm text-dark-400">오류</div>
      </div>
      <div
        class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 text-center"
      >
        <div class="text-2xl font-bold text-yellow-400">
          {statusSummary.warnings}
        </div>
        <div class="text-sm text-dark-400">경고</div>
      </div>
    </div>

    <!-- 전체 상태 메시지 -->
    <div class="space-y-2">
      {#if validationResult.valid}
        <StatusIndicator
          status="success"
          message="모든 설정이 올바릅니다"
          variant="card"
        />
      {:else}
        <StatusIndicator
          status="error"
          message="설정에 문제가 있습니다"
          variant="card"
        />
        {#each validationResult.errors as error}
          <StatusIndicator
            status="error"
            message={error}
            variant="inline"
            size="sm"
          />
        {/each}
      {/if}

      {#each validationResult.warnings as warning}
        <StatusIndicator
          status="warning"
          message={warning}
          variant="inline"
          size="sm"
        />
      {/each}
    </div>

    <!-- 각 제공업체별 상세 상태 -->
    <div class="space-y-4">
      {#each Object.entries(validationResult.provider_status || {}) as [providerKey, status]}
        {@const providerName = formatProviderName(providerKey)}
        {@const providerStatus = getProviderStatus(status)}

        <div class="border border-dark-700 rounded-lg overflow-hidden">
          <!-- 제공업체 헤더 -->
          <div class="bg-dark-800/50 p-4 border-b border-dark-700">
            <div class="flex items-center justify-between">
              <div class="flex items-center space-x-3">
                <StatusIndicator
                  status={providerStatus.icon}
                  message=""
                  variant="badge"
                  size="sm"
                />
                <div>
                  <h3 class="font-semibold text-dark-100">{providerName}</h3>
                  <p class="text-sm {providerStatus.color}">
                    {providerStatus.text}
                  </p>
                </div>
              </div>

              <!-- 연결 테스트 버튼 -->
              {#if showTestButtons && status.has_api_key && status.interface_initialized}
                <button
                  class="btn-ghost text-xs px-3 py-1 {testingStates[providerKey]
                    ? 'animate-pulse'
                    : ''}"
                  on:click={() => testApiConnection(providerKey)}
                  disabled={testingStates[providerKey]}
                >
                  {#if testingStates[providerKey]}
                    <LoadingSpinner text="" size="sm" />
                  {:else}
                    <TestTube size={14} class="mr-1" />
                  {/if}
                  연결 테스트
                </button>
              {/if}
            </div>
          </div>

          <!-- 상세 정보 -->
          {#if showDetails}
            <div class="p-4 space-y-3">
              <div class="grid grid-cols-2 gap-4 text-sm">
                <!-- 기본 상태 -->
                <div>
                  <h4 class="font-medium text-dark-200 mb-2">기본 상태</h4>
                  <div class="space-y-1">
                    <div class="flex justify-between">
                      <span class="text-dark-400">API 키:</span>
                      <StatusIndicator
                        status={status.has_api_key ? "success" : "error"}
                        message={status.has_api_key ? "설정됨" : "미설정"}
                        variant="badge"
                        size="sm"
                      />
                    </div>
                    <div class="flex justify-between">
                      <span class="text-dark-400">인터페이스:</span>
                      <StatusIndicator
                        status={status.interface_initialized
                          ? "success"
                          : "error"}
                        message={status.interface_initialized
                          ? "초기화됨"
                          : "오류"}
                        variant="badge"
                        size="sm"
                      />
                    </div>
                  </div>
                </div>

                <!-- 모델 정보 -->
                <div>
                  <h4 class="font-medium text-dark-200 mb-2">모델 정보</h4>
                  <div class="space-y-1">
                    <div class="flex justify-between">
                      <span class="text-dark-400">사용 가능한 모델:</span>
                      <span class="text-dark-200 font-medium"
                        >{status.available_models}개</span
                      >
                    </div>
                  </div>
                </div>
              </div>

              <!-- 지원 기능 -->
              {#if status.interface_initialized && status.supported_features}
                <div>
                  <h4 class="font-medium text-dark-200 mb-2">지원 기능</h4>
                  <div class="flex flex-wrap gap-2">
                    {#each Object.entries(status.supported_features) as [feature, supported]}
                      <StatusIndicator
                        status={supported ? "success" : "error"}
                        message={feature}
                        variant="badge"
                        size="sm"
                      />
                    {/each}
                  </div>
                </div>
              {/if}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {/if}
</div>
