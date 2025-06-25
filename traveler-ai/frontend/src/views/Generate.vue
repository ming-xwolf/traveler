<template>
  <app-layout>
    <div class="generate-page">
      <div class="container">
        <!-- 页面标题 -->
        <div class="page-header">
          <h1 class="page-title">
            <span class="gradient-text">AI智能生成</span>
            旅游攻略
          </h1>
          <p class="page-subtitle">
            填写您的旅行需求，AI将为您生成专业的旅游攻略
          </p>
        </div>

        <!-- 生成表单 -->
        <div class="generate-form-container">
          <el-card class="form-card" shadow="hover">
            <template #header>
              <div class="card-header">
                <h3>
                  <el-icon><Magic /></el-icon>
                  攻略生成配置
                </h3>
                <p>请填写详细信息以获得更精准的攻略推荐</p>
              </div>
            </template>

            <el-form
              ref="generateFormRef"
              :model="generateForm"
              :rules="generateFormRules"
              label-width="120px"
              size="large"
              class="generate-form"
            >
              <!-- 基本信息 -->
              <div class="form-section">
                <h4 class="section-title">
                  <el-icon><Location /></el-icon>
                  基本信息
                </h4>
                
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="目的地" prop="destination" required>
                      <el-input
                        v-model="generateForm.destination"
                        placeholder="请输入目的地，如：新疆伊犁"
                        clearable
                        @blur="validateDestination"
                      >
                        <template #prefix>
                          <el-icon><Location /></el-icon>
                        </template>
                      </el-input>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="12">
                    <el-form-item label="旅行天数" prop="days" required>
                      <el-input-number
                        v-model="generateForm.days"
                        :min="1"
                        :max="30"
                        placeholder="天数"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>

                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="出发日期">
                      <el-date-picker
                        v-model="generateForm.start_date"
                        type="date"
                        placeholder="选择出发日期"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="12">
                    <el-form-item label="人数" prop="group_size" required>
                      <el-input-number
                        v-model="generateForm.group_size"
                        :min="1"
                        :max="20"
                        placeholder="人数"
                        style="width: 100%"
                      />
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>

              <!-- 偏好设置 -->
              <div class="form-section">
                <h4 class="section-title">
                  <el-icon><Star /></el-icon>
                  偏好设置
                </h4>
                
                <el-row :gutter="24">
                  <el-col :span="12">
                    <el-form-item label="旅行风格">
                      <el-select
                        v-model="generateForm.travel_style"
                        placeholder="选择旅行风格"
                        style="width: 100%"
                      >
                        <el-option label="自然风光" value="nature" />
                        <el-option label="文化体验" value="culture" />
                        <el-option label="美食探索" value="food" />
                        <el-option label="历史古迹" value="history" />
                        <el-option label="休闲度假" value="leisure" />
                        <el-option label="探险刺激" value="adventure" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                  
                  <el-col :span="12">
                    <el-form-item label="预算范围">
                      <el-select
                        v-model="generateForm.budget"
                        placeholder="选择预算范围"
                        style="width: 100%"
                      >
                        <el-option label="经济实惠 (< ¥2000)" value="budget" />
                        <el-option label="中等预算 (¥2000-5000)" value="moderate" />
                        <el-option label="高端奢华 (> ¥5000)" value="luxury" />
                      </el-select>
                    </el-form-item>
                  </el-col>
                </el-row>
              </div>

              <!-- AI配置 -->
              <div class="form-section">
                <h4 class="section-title">
                  <el-icon><Setting /></el-icon>
                  AI配置
                </h4>
                
                <el-form-item label="AI模型">
                  <el-select
                    v-model="generateForm.ai_provider"
                    placeholder="选择AI模型"
                    style="width: 100%"
                  >
                    <el-option label="Ollama (本地)" value="ollama" />
                    <el-option label="DeepSeek" value="deepseek" />
                    <el-option label="阿里云百炼" value="bailian" />
                  </el-select>
                </el-form-item>
              </div>

              <!-- 特殊需求 -->
              <div class="form-section">
                <h4 class="section-title">
                  <el-icon><ChatDotRound /></el-icon>
                  特殊需求
                </h4>
                
                <el-form-item label="特殊要求">
                  <el-input
                    v-model="generateForm.special_requirements"
                    type="textarea"
                    :rows="4"
                    placeholder="请描述您的特殊需求或偏好（可选）"
                    maxlength="500"
                    show-word-limit
                  />
                </el-form-item>
              </div>

              <!-- 操作按钮 -->
              <div class="form-actions">
                <el-button
                  type="primary"
                  size="large"
                  @click="handleGenerate"
                  :loading="itineraryStore.isGenerating"
                  class="generate-button"
                >
                  <el-icon><Magic /></el-icon>
                  开始生成攻略
                </el-button>
                
                <el-button
                  size="large"
                  @click="resetForm"
                  :disabled="itineraryStore.isGenerating"
                >
                  <el-icon><RefreshLeft /></el-icon>
                  重置表单
                </el-button>
              </div>
            </el-form>
          </el-card>
        </div>

        <!-- 生成进度 -->
        <div v-if="itineraryStore.isGenerating" class="progress-container">
          <el-card class="progress-card" shadow="hover">
            <template #header>
              <h3>
                <el-icon class="rotating"><Loading /></el-icon>
                正在生成攻略
              </h3>
            </template>

            <el-progress
              :percentage="itineraryStore.currentProgress"
              :stroke-width="8"
              status="success"
            />
            
            <div class="progress-info">
              <p>AI正在为您精心制作专属的旅游攻略，请稍候...</p>
            </div>
          </el-card>
        </div>

        <!-- 生成结果 -->
        <div v-if="itineraryStore.currentItinerary?.status === 'completed'" class="result-container">
          <el-card class="result-card" shadow="hover">
            <template #header>
              <div class="result-header">
                <h3>
                  <el-icon><Check /></el-icon>
                  攻略生成完成
                </h3>
                <div class="result-actions">
                  <el-button type="primary" @click="viewItinerary">
                    查看攻略
                  </el-button>
                  <el-button @click="downloadItinerary">
                    下载攻略
                  </el-button>
                </div>
              </div>
            </template>

            <div class="result-summary">
              <h4>{{ itineraryStore.currentItinerary.title }}</h4>
              <div class="itinerary-meta">
                <el-tag size="large">{{ itineraryStore.currentItinerary.destination }}</el-tag>
                <el-tag size="large" type="info">{{ itineraryStore.currentItinerary.days }}天</el-tag>
                <el-tag size="large" type="success">已完成</el-tag>
              </div>
            </div>
          </el-card>
        </div>
      </div>
    </div>
  </app-layout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useItineraryStore } from '@/stores/itinerary'
import AppLayout from '@/components/layout/AppLayout.vue'
import {
  Magic,
  Location,
  Star,
  Setting,
  ChatDotRound,
  RefreshLeft,
  Loading,
  Check
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const itineraryStore = useItineraryStore()

// 表单引用
const generateFormRef = ref<FormInstance>()

// 表单数据
const generateForm = ref({
  destination: '',
  days: 7,
  start_date: '',
  group_size: 2,
  travel_style: '',
  budget: 'moderate',
  ai_provider: 'ollama',
  special_requirements: ''
})

// 表单验证规则
const generateFormRules: FormRules = {
  destination: [
    { required: true, message: '请输入目的地', trigger: 'blur' },
    { min: 2, max: 50, message: '目的地长度应在 2 到 50 个字符', trigger: 'blur' }
  ],
  days: [
    { required: true, message: '请选择旅行天数', trigger: 'change' },
    { type: 'number', min: 1, max: 30, message: '旅行天数应在 1 到 30 天之间', trigger: 'change' }
  ],
  group_size: [
    { required: true, message: '请选择人数', trigger: 'change' },
    { type: 'number', min: 1, max: 20, message: '人数应在 1 到 20 人之间', trigger: 'change' }
  ]
}

// 验证目的地
const validateDestination = async () => {
  if (generateForm.value.destination.trim().length < 2) return

  try {
    await itineraryStore.validateDestination(generateForm.value.destination)
  } catch (error) {
    console.error('验证目的地失败:', error)
  }
}

// 生成攻略
const handleGenerate = async () => {
  if (!generateFormRef.value) return

  try {
    await generateFormRef.value.validate()
    
    const request = {
      destination: generateForm.value.destination,
      days: generateForm.value.days,
      travel_style: generateForm.value.travel_style,
      budget_min: getBudgetRange(generateForm.value.budget).min,
      budget_max: getBudgetRange(generateForm.value.budget).max,
      group_size: generateForm.value.group_size,
      start_date: generateForm.value.start_date,
      ai_provider: generateForm.value.ai_provider,
      special_requirements: generateForm.value.special_requirements
    }

    const result = await itineraryStore.generateItinerary(request)
    
    if (result) {
      ElMessage.success('攻略开始生成，请稍候...')
    }
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 获取预算范围
const getBudgetRange = (budget: string) => {
  switch (budget) {
    case 'budget':
      return { min: 0, max: 2000 }
    case 'moderate':
      return { min: 2000, max: 5000 }
    case 'luxury':
      return { min: 5000, max: null }
    default:
      return { min: null, max: null }
  }
}

// 重置表单
const resetForm = () => {
  generateFormRef.value?.resetFields()
}

// 查看攻略
const viewItinerary = () => {
  if (itineraryStore.currentItinerary) {
    router.push(`/itinerary/${itineraryStore.currentItinerary.id}`)
  }
}

// 下载攻略
const downloadItinerary = async () => {
  if (itineraryStore.currentItinerary) {
    await itineraryStore.exportItinerary(itineraryStore.currentItinerary.id, 'pdf')
  }
}

// 初始化
onMounted(async () => {
  // 从URL参数初始化表单
  if (route.query.destination) {
    generateForm.value.destination = route.query.destination as string
  }
  if (route.query.days) {
    generateForm.value.days = parseInt(route.query.days as string)
  }

  // 获取AI服务商列表
  await itineraryStore.fetchAIProviders()
})
</script>

<style lang="scss" scoped>
.generate-page {
  min-height: calc(100vh - 60px);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 40px 0;
}

.page-header {
  text-align: center;
  margin-bottom: 40px;

  .page-title {
    font-size: 3rem;
    font-weight: 700;
    margin-bottom: 16px;
    color: var(--el-text-color-primary);

    @media (max-width: 768px) {
      font-size: 2rem;
    }
  }

  .page-subtitle {
    font-size: 1.25rem;
    color: var(--el-text-color-regular);
    margin-bottom: 0;
  }
}

.generate-form-container {
  max-width: 800px;
  margin: 0 auto 40px;
}

.form-card {
  .card-header {
    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
      font-size: 1.5rem;
      color: var(--el-text-color-primary);
    }

    p {
      margin: 0;
      color: var(--el-text-color-regular);
    }
  }
}

.form-section {
  margin-bottom: 40px;

  .section-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--el-text-color-primary);
    margin-bottom: 24px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--el-border-color-lighter);
  }
}

.form-actions {
  text-align: center;
  padding-top: 32px;
  border-top: 1px solid var(--el-border-color-lighter);

  .generate-button {
    padding: 16px 48px;
    font-size: 16px;
    font-weight: 600;
    margin-right: 16px;
  }
}

.progress-container,
.result-container {
  max-width: 800px;
  margin: 0 auto 40px;
}

.progress-card {
  h3 {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    font-size: 1.5rem;
    color: var(--el-text-color-primary);
  }

  .progress-info {
    margin-top: 16px;
    text-align: center;
    color: var(--el-text-color-regular);
  }
}

.result-card {
  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;

    h3 {
      display: flex;
      align-items: center;
      gap: 8px;
      margin: 0;
      font-size: 1.5rem;
      color: var(--el-color-success);
    }

    .result-actions {
      display: flex;
      gap: 12px;
    }
  }
}

.result-summary {
  h4 {
    font-size: 1.25rem;
    margin-bottom: 16px;
    color: var(--el-text-color-primary);
  }

  .itinerary-meta {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
    flex-wrap: wrap;
  }
}

// 旋转动画
.rotating {
  animation: rotate 2s linear infinite;
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

// 响应式适配
@media (max-width: 768px) {
  .generate-page {
    padding: 20px 0;
  }

  .result-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch !important;

    .result-actions {
      justify-content: center;
    }
  }

  .form-actions {
    .generate-button {
      margin-right: 0;
      margin-bottom: 12px;
      width: 100%;
    }
  }
}
</style> 