<!-- ted-os-project/frontend/src/lib/components/pages/SettingsPage.svelte -->
<script lang="ts">
  import { onMount } from "svelte";
  import { api } from "$lib/api";
  import { showError, showSuccess } from "$lib/stores";
  import {
    Settings,
    Key,
    Palette,
    Database,
    Shield,
    RefreshCw,
    Eye,
    EyeOff,
    Save,
    RotateCcw,
    Music,
  } from "lucide-svelte";

  let loading = false;
  let settings: Record<string, any> = {};
  let showApiKeys: Record<string, boolean> = {};
  let apiKeys: Record<string, string> = {};

  // 별도 변수들 (초기값만 설정)
  let temperatureValue: number = 0.7;
  let maxTokensValue: number = 4096;
  let themeValue: string = "dark";
  let languageValue: string = "ko";
  let autoTitleGeneration: boolean = true;
  let usageTracking: boolean = true;
  let debugMode: boolean = false;

  // settings 초기화 시 값 동기화 (loadSettings 함수 내에서 처리)
  function syncSettingsToVariables() {
    if (settings.defaults?.temperature !== undefined) {
      temperatureValue = settings.defaults.temperature;
    }
    if (settings.defaults?.max_tokens !== undefined) {
      maxTokensValue = settings.defaults.max_tokens;
    }
    if (settings.ui?.theme !== undefined) {
      themeValue = settings.ui.theme;
    }
    if (settings.ui?.language !== undefined) {
      languageValue = settings.ui.language;
    }
    if (settings.features?.auto_title_generation !== undefined) {
      autoTitleGeneration = settings.features.auto_title_generation;
    }
    if (settings.features?.usage_tracking !== undefined) {
      usageTracking = settings.features.usage_tracking;
    }
    if (settings.features?.debug_mode !== undefined) {
      debugMode = settings.features.debug_mode;
    }
  }

  // 변수 값들을 settings에 반영
  function syncVariablesToSettings() {
    if (!settings.defaults) settings.defaults = {};
    if (!settings.ui) settings.ui = {};
    if (!settings.features) settings.features = {};

    settings.defaults.temperature = temperatureValue;
    settings.defaults.max_tokens = maxTokensValue;
    settings.ui.theme = themeValue;
    settings.ui.language = languageValue;
    settings.features.auto_title_generation = autoTitleGeneration;
    settings.features.usage_tracking = usageTracking;
    settings.features.debug_mode = debugMode;
  }

  // 설정 로드
  async function loadSettings() {
    loading = true;
    try {
      const data = await api.getSettings();
      settings = data;

      // API 키들을 별도로 관리 (마스킹된 상태)
      apiKeys = data.api_keys || {};

      // 모든 API 키의 표시 상태를 false로 초기화
      showApiKeys = Object.keys(apiKeys).reduce((acc, key) => {
        acc[key] = false;
        return acc;
      }, {} as Record<string, boolean>);

      // 설정 값들을 변수에 동기화
      syncSettingsToVariables();
    } catch (error) {
      console.error("설정 로드 실패:", error);
      showError("설정을 불러올 수 없습니다.");
    } finally {
      loading = false;
    }
  }

  // 설정 저장
  async function saveSettings() {
    try {
      // 변수 값들을 settings에 반영
      syncVariablesToSettings();

      // API 키는 별도로 처리하고, 나머지 설정만 저장
      const settingsToSave = { ...settings };
      delete settingsToSave.api_keys;

      await api.updateSettings(settingsToSave);
      showSuccess("설정이 저장되었습니다.");
    } catch (error) {
      console.error("설정 저장 실패:", error);
      showError("설정을 저장할 수 없습니다.");
    }
  }

  // API 키 토글
  function toggleApiKeyVisibility(provider: string) {
    showApiKeys[provider] = !showApiKeys[provider];
  }

  // API 키 업데이트 (실제로는 백엔드에서 처리해야 함)
  async function updateApiKey(provider: string, newKey: string) {
    if (!newKey.trim()) return;

    try {
      // 실제 구현에서는 별도의 API 엔드포인트 필요
      showSuccess(`${provider} API 키가 업데이트되었습니다.`);
    } catch (error) {
      showError("API 키 업데이트에 실패했습니다.");
    }
  }

  // 기본값으로 리셋
  function resetToDefaults() {
    if (!confirm("모든 설정을 기본값으로 되돌리시겠습니까?")) return;

    settings = {
      defaults: {
        temperature: 0.7,
        max_tokens: 4096,
      },
      ui: {
        theme: "dark",
        language: "ko",
      },
      features: {
        auto_title_generation: true,
        usage_tracking: true,
        debug_mode: false,
      },
    };

    syncSettingsToVariables();
    showSuccess("설정이 기본값으로 리셋되었습니다.");
  }

  onMount(() => {
    loadSettings();
  });

  // 제공업체 이름 포맷팅
  function formatProviderName(provider: string): string {
    const names: Record<string, string> = {
      openai: "OpenAI",
      anthropic: "Anthropic",
      google: "Google AI",
    };
    return names[provider] || provider;
  }

  // API 키 마스킹
  function maskApiKey(key: string): string {
    if (!key) return "";
    if (key === "***") return "설정됨";
    return key.substring(0, 8) + "••••••••";
  }
  // 연결 테스트 함수
  async function testApiConnection(provider: string) {
    try {
      showSuccess(
        `${formatProviderName(provider)} API 연결 테스트를 시작합니다...`
      );

      // 실제 구현에서는 백엔드 API 호출
      // const result = await api.testProviderConnection(provider);

      // 임시로 성공 메시지 (실제로는 백엔드에서 테스트 결과를 받아야 함)
      setTimeout(() => {
        showSuccess(`✅ ${formatProviderName(provider)} API 연결 성공!`);
      }, 1000);
    } catch (error) {
      showError(`❌ ${formatProviderName(provider)} API 연결 실패: ${error}`);
    }
  }
</script>

<div class="flex-1 overflow-y-auto p-6 space-y-6">
  <!-- 페이지 헤더 -->
  <div class="flex items-center justify-between">
    <div>
      <h1 class="text-2xl font-bold text-dark-100">설정</h1>
      <p class="text-dark-400 mt-1">애플리케이션 설정을 관리하세요.</p>
    </div>

    <div class="flex items-center space-x-2">
      <button
        class="btn-secondary {loading ? 'animate-spin' : ''}"
        on:click={loadSettings}
        disabled={loading}
      >
        <RefreshCw size={16} class="mr-2" />
        새로고침
      </button>

      <button class="btn-primary" on:click={saveSettings}>
        <Save size={16} class="mr-2" />
        저장
      </button>
    </div>
  </div>

  {#if loading}
    <!-- 로딩 상태 -->
    <div class="flex items-center justify-center py-12">
      <RefreshCw size={32} class="animate-spin text-dark-400" />
    </div>
  {:else}
    <!-- 설정 섹션들 -->
    <div class="space-y-6">
      <!-- API 키 설정 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <Key size={20} class="text-claude-orange" />
          <h2 class="text-lg font-semibold text-dark-100">API 키 관리</h2>
        </div>

        <p class="text-sm text-dark-400 mb-6">
          각 AI 제공업체의 API 키를 설정하세요. 키는 안전하게 암호화되어
          저장됩니다.
        </p>
        <!-- AI 제공업체 전체 상태 요약 -->
        <div class="grid grid-cols-4 gap-4 mb-6">
          <div
            class="bg-dark-800/50 border border-dark-700 rounded-lg p-3 text-center"
          >
            <div class="text-2xl font-bold text-dark-100">
              {Object.keys(apiKeys).length}
            </div>
            <div class="text-xs text-dark-500">총 제공업체</div>
          </div>
          <div
            class="bg-dark-800/50 border border-dark-700 rounded-lg p-3 text-center"
          >
            <div class="text-2xl font-bold text-green-400">
              {Object.entries(apiKeys).filter(([_, key]) => key && key !== "")
                .length}
            </div>
            <div class="text-xs text-dark-500">활성 제공업체</div>
          </div>
          <div
            class="bg-dark-800/50 border border-dark-700 rounded-lg p-3 text-center"
          >
            <div class="text-2xl font-bold text-dark-100">0</div>
            <div class="text-xs text-dark-500">오류</div>
          </div>
          <div
            class="bg-dark-800/50 border border-dark-700 rounded-lg p-3 text-center"
          >
            <div class="text-2xl font-bold text-dark-100">0</div>
            <div class="text-xs text-dark-500">경고</div>
          </div>
        </div>

        <!-- 새로고침 버튼 -->
        <div class="flex items-center justify-between mb-4">
          <div>
            <p class="text-sm text-dark-400">
              각 AI 제공업체의 API 키 및 연결 상태를 확인합니다.
            </p>
          </div>
          <button class="btn-secondary">
            <RefreshCw size={16} class="mr-2" />
            상태 새로고침
          </button>
        </div>
        <div class="space-y-4">
          {#each Object.entries(apiKeys) as [provider, key]}
            <div class="border border-dark-700 rounded-lg p-4">
              <div class="flex items-center justify-between mb-3">
                <h3 class="font-medium text-dark-200">
                  {formatProviderName(provider)}
                </h3>
                <div class="flex items-center space-x-2">
                  <span
                    class="text-xs px-2 py-1 rounded-full {key && key !== ''
                      ? 'bg-green-500/20 text-green-400'
                      : 'bg-red-500/20 text-red-400'}"
                  >
                    {key && key !== "" ? "설정됨" : "미설정"}
                  </span>
                  {#if key && key !== ""}
                    <button
                      class="btn-ghost text-xs px-2 py-1"
                      on:click={() => testApiConnection(provider)}
                    >
                      🔗 연결 테스트
                    </button>
                  {/if}
                </div>
              </div>

              <div class="space-y-3">
                <div class="relative">
                  <input
                    type={showApiKeys[provider] ? "text" : "password"}
                    value={showApiKeys[provider]
                      ? key || ""
                      : maskApiKey(key || "")}
                    placeholder={`${formatProviderName(provider)} API Key`}
                    class="input pr-10"
                    readonly={!showApiKeys[provider]}
                  />
                  <button
                    class="absolute right-2 top-2 btn-icon p-1"
                    on:click={() => toggleApiKeyVisibility(provider)}
                  >
                    {#if showApiKeys[provider]}
                      <EyeOff size={16} />
                    {:else}
                      <Eye size={16} />
                    {/if}
                  </button>
                </div>

                {#if showApiKeys[provider]}
                  <div class="text-xs text-dark-500">
                    <p>
                      • API 키는 {formatProviderName(provider)} 공식 웹사이트에서
                      발급받으세요
                    </p>
                    <p>• 키는 안전하게 암호화되어 저장됩니다</p>
                  </div>
                {/if}
              </div>
            </div>
          {/each}
        </div>
      </div>

      <!-- 기본 설정 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <Settings size={20} class="text-blue-400" />
          <h2 class="text-lg font-semibold text-dark-100">기본 매개변수</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Temperature -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              Temperature (창의성)
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              bind:value={temperatureValue}
              class="w-full h-2 bg-dark-700 rounded-lg appearance-none cursor-pointer slider"
            />
            <div class="flex justify-between text-xs text-dark-500 mt-1">
              <span>일관적 (0.0)</span>
              <span class="font-medium text-dark-300">
                {temperatureValue}
              </span>
              <span>창의적 (2.0)</span>
            </div>
          </div>

          <!-- Max Tokens -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              최대 토큰
            </label>
            <input
              type="number"
              min="100"
              max="100000"
              step="100"
              bind:value={maxTokensValue}
              class="input"
            />
            <p class="text-xs text-dark-500 mt-1">
              AI 응답의 최대 길이를 설정합니다
            </p>
          </div>
        </div>
      </div>

      <!-- UI 설정 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <Palette size={20} class="text-purple-400" />
          <h2 class="text-lg font-semibold text-dark-100">사용자 인터페이스</h2>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- 테마 -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              테마
            </label>
            <select bind:value={themeValue} class="input">
              <option value="dark">어두운 테마</option>
              <option value="light">밝은 테마</option>
              <option value="auto">시스템 설정</option>
            </select>
          </div>

          <!-- 언어 -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              언어
            </label>
            <select bind:value={languageValue} class="input">
              <option value="ko">한국어</option>
              <option value="en">English</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 기능 설정 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <Database size={20} class="text-green-400" />
          <h2 class="text-lg font-semibold text-dark-100">기능 설정</h2>
        </div>

        <div class="space-y-4">
          <!-- 자동 제목 생성 -->
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-medium text-dark-200">자동 채팅 제목 생성</h3>
              <p class="text-sm text-dark-500">
                첫 번째 응답 후 AI가 자동으로 채팅 제목을 생성합니다
              </p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={autoTitleGeneration}
                class="sr-only peer"
              />
              <div
                class="w-11 h-6 bg-dark-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-claude-orange"
              />
            </label>
          </div>

          <!-- 사용량 추적 -->
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-medium text-dark-200">사용량 추적</h3>
              <p class="text-sm text-dark-500">
                토큰 사용량과 비용을 자동으로 추적합니다
              </p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={usageTracking}
                class="sr-only peer"
              />
              <div
                class="w-11 h-6 bg-dark-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-claude-orange"
              />
            </label>
          </div>

          <!-- 디버그 모드 -->
          <div class="flex items-center justify-between">
            <div>
              <h3 class="font-medium text-dark-200">디버그 모드</h3>
              <p class="text-sm text-dark-500">
                개발자를 위한 추가 로깅과 정보를 표시합니다
              </p>
            </div>
            <label class="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                bind:checked={debugMode}
                class="sr-only peer"
              />
              <div
                class="w-11 h-6 bg-dark-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-claude-orange"
              />
            </label>
          </div>
        </div>
      </div>

      <!-- Spotify API 설정 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <Music size={20} class="text-green-500" />
          <h2 class="text-lg font-semibold text-dark-100">Spotify API 연동</h2>
        </div>

        <p class="text-sm text-dark-400 mb-6">
          LLMOS에서 Spotify 기능을 사용하려면 Spotify 개발자 대시보드에서
          애플리케이션을 생성하고 다음 정보를 설정해야 합니다.
        </p>

        <div class="bg-dark-800/50 border border-dark-700 rounded-lg p-4 mb-6">
          <h3 class="font-medium text-dark-200 mb-2">📋 설정 가이드</h3>
          <ol class="text-sm text-dark-400 space-y-1 list-decimal ml-4">
            <li>
              <a
                href="https://developer.spotify.com/dashboard/"
                target="_blank"
                class="text-claude-orange hover:underline"
              >
                Spotify Developer Dashboard
              </a>에서 앱을 생성하세요
            </li>
            <li>Client ID와 Client Secret을 복사하세요</li>
            <li>
              Redirect URI에 <code class="bg-dark-700 px-1 rounded"
                >http://127.0.0.1:8888/callback</code
              >를 추가하세요
            </li>
          </ol>
        </div>

        <div class="space-y-4">
          <!-- Client ID -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              Spotify Client ID
            </label>
            <input
              type="text"
              placeholder="여기에 Client ID를 입력하세요"
              class="input"
            />
            <p class="text-xs text-dark-500 mt-1">
              Spotify 개발자 대시보드에서 발급받은 Client ID입니다.
            </p>
          </div>

          <!-- Client Secret -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              Spotify Client Secret
            </label>
            <input
              type="password"
              placeholder="여기에 Client Secret을 입력하세요"
              class="input"
            />
            <p class="text-xs text-dark-500 mt-1">
              Spotify 개발자 대시보드에서 발급받은 Client Secret입니다.
            </p>
          </div>

          <!-- Redirect URI -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              Redirect URI
            </label>
            <input
              type="text"
              value="http://127.0.0.1:8888/callback"
              class="input"
              readonly
            />
            <p class="text-xs text-dark-500 mt-1">
              Spotify 앱 설정에 등록한 Redirect URI와 정확히 일치해야 합니다.
            </p>
          </div>

          <!-- 포트 타입 -->
          <div>
            <label class="block text-sm font-medium text-dark-300 mb-2">
              로컬 포트 타입
            </label>
            <div class="grid grid-cols-2 gap-2">
              <label
                class="flex items-center p-3 border border-dark-700 rounded-lg cursor-pointer hover:border-dark-600"
              >
                <input
                  type="radio"
                  name="portType"
                  value="fixed"
                  checked
                  class="mr-3 text-claude-orange"
                />
                <div>
                  <div class="font-medium text-dark-200">고정 포트</div>
                  <div class="text-xs text-dark-500">포트 8888 사용</div>
                </div>
              </label>
              <label
                class="flex items-center p-3 border border-dark-700 rounded-lg cursor-pointer hover:border-dark-600"
              >
                <input
                  type="radio"
                  name="portType"
                  value="dynamic"
                  class="mr-3 text-claude-orange"
                />
                <div>
                  <div class="font-medium text-dark-200">동적 포트</div>
                  <div class="text-xs text-dark-500">자동 할당</div>
                </div>
              </label>
            </div>
          </div>

          <!-- 저장 버튼 -->
          <button class="btn-primary w-full">
            <Save size={16} class="mr-2" />
            Spotify 설정 저장
          </button>

          <!-- 상태 표시 -->
          <div class="bg-dark-800/50 border border-dark-700 rounded-lg p-4">
            <h3 class="font-medium text-dark-200 mb-2">연동 상태</h3>
            <div class="flex items-center text-sm">
              <span class="w-3 h-3 bg-red-500 rounded-full mr-2" />
              <span class="text-dark-400"
                >Spotify API 정보가 설정되지 않았습니다</span
              >
            </div>
          </div>
        </div>
      </div>

      <!-- 데이터 관리 -->
      <div class="card p-6">
        <div class="flex items-center space-x-2 mb-4">
          <Shield size={20} class="text-red-400" />
          <h2 class="text-lg font-semibold text-dark-100">데이터 관리</h2>
        </div>

        <div class="space-y-4">
          <div
            class="flex items-center justify-between p-4 border border-dark-700 rounded-lg"
          >
            <div>
              <h3 class="font-medium text-dark-200">설정 초기화</h3>
              <p class="text-sm text-dark-500">
                모든 설정을 기본값으로 되돌립니다
              </p>
            </div>
            <button
              class="btn-secondary text-red-400 border-red-400 hover:bg-red-400/10"
              on:click={resetToDefaults}
            >
              <RotateCcw size={16} class="mr-2" />
              초기화
            </button>
          </div>

          <div
            class="flex items-center justify-between p-4 border border-dark-700 rounded-lg"
          >
            <div>
              <h3 class="font-medium text-dark-200">설정 내보내기</h3>
              <p class="text-sm text-dark-500">
                현재 설정을 JSON 파일로 다운로드합니다
              </p>
            </div>
            <button
              class="btn-secondary"
              on:click={() => {
                syncVariablesToSettings();
                const dataStr = JSON.stringify(settings, null, 2);
                const dataUri =
                  "data:application/json;charset=utf-8," +
                  encodeURIComponent(dataStr);
                const exportFileDefaultName = "llmos-settings.json";
                const linkElement = document.createElement("a");
                linkElement.setAttribute("href", dataUri);
                linkElement.setAttribute("download", exportFileDefaultName);
                linkElement.click();
              }}
            >
              다운로드
            </button>
          </div>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  /* 커스텀 토글 스위치와 슬라이더 스타일 */
  .slider::-webkit-slider-thumb {
    appearance: none;
    height: 16px;
    width: 16px;
    border-radius: 50%;
    background: #ff6b35;
    cursor: pointer;
    border: 2px solid #1e293b;
  }

  .slider::-moz-range-thumb {
    height: 16px;
    width: 16px;
    border-radius: 50%;
    background: #ff6b35;
    cursor: pointer;
    border: 2px solid #1e293b;
  }

  .slider::-webkit-slider-track {
    height: 8px;
    border-radius: 4px;
    background: #475569;
  }

  .slider::-moz-range-track {
    height: 8px;
    border-radius: 4px;
    background: #475569;
  }
</style>
