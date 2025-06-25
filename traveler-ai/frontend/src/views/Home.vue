<template>
  <app-layout>
    <!-- 英雄区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">TravelerAI</span>
          智能旅游攻略生成平台
        </h1>
        <p class="hero-subtitle">
          输入目的地和旅行天数，AI为您量身定制专业的旅游攻略
          <br>
          让每一次旅行都成为难忘的回忆
        </p>
        
        <!-- 快速生成表单 -->
        <div class="quick-form">
          <el-form
            ref="quickFormRef"
            :model="quickForm"
            :rules="quickFormRules"
            inline
            class="hero-form"
          >
            <el-form-item prop="destination">
              <el-input
                v-model="quickForm.destination"
                placeholder="输入目的地，如：新疆伊犁"
                size="large"
                style="width: 300px"
                clearable
              >
                <template #prefix>
                  <el-icon><Location /></el-icon>
                </template>
              </el-input>
            </el-form-item>
            
            <el-form-item prop="days">
              <el-input-number
                v-model="quickForm.days"
                :min="1"
                :max="30"
                size="large"
                placeholder="天数"
                style="width: 120px"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button
                type="primary"
                size="large"
                @click="handleQuickGenerate"
                :loading="isGenerating"
                class="generate-button"
              >
                <el-icon><Magic /></el-icon>
                立即生成
              </el-button>
            </el-form-item>
          </el-form>
        </div>

        <!-- 特色标签 -->
        <div class="feature-tags">
          <el-tag size="large" type="success">🤖 AI智能生成</el-tag>
          <el-tag size="large" type="info">🗺️ 实时地理信息</el-tag>
          <el-tag size="large" type="warning">📱 多格式导出</el-tag>
          <el-tag size="large" type="danger">⚡ 快速高效</el-tag>
        </div>
      </div>
      
      <!-- 背景装饰 -->
      <div class="hero-decoration">
        <div class="floating-card card-1">
          <el-icon size="40" color="#409EFF"><Map /></el-icon>
        </div>
        <div class="floating-card card-2">
          <el-icon size="40" color="#67C23A"><Compass /></el-icon>
        </div>
        <div class="floating-card card-3">
          <el-icon size="40" color="#E6A23C"><Camera /></el-icon>
        </div>
      </div>
    </section>

    <!-- 功能特色 -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">平台特色</h2>
        <div class="features-grid">
          <div class="feature-card" v-for="feature in features" :key="feature.title">
            <div class="feature-icon">
              <el-icon :size="48" :color="feature.color">
                <component :is="feature.icon" />
              </el-icon>
            </div>
            <h3>{{ feature.title }}</h3>
            <p>{{ feature.description }}</p>
          </div>
        </div>
      </div>
    </section>

    <!-- 使用流程 -->
    <section class="process-section">
      <div class="container">
        <h2 class="section-title">使用流程</h2>
        <div class="process-steps">
          <div class="step" v-for="(step, index) in processSteps" :key="index">
            <div class="step-number">{{ index + 1 }}</div>
            <div class="step-content">
              <h3>{{ step.title }}</h3>
              <p>{{ step.description }}</p>
            </div>
            <div class="step-arrow" v-if="index < processSteps.length - 1">
              <el-icon><ArrowRight /></el-icon>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- 示例展示 -->
    <section class="examples-section">
      <div class="container">
        <h2 class="section-title">精选示例</h2>
        <div class="examples-grid">
          <div class="example-card" v-for="example in examples" :key="example.id">
            <div class="example-image">
              <img :src="example.image" :alt="example.title" />
              <div class="example-overlay">
                <el-button type="primary" @click="viewExample(example)">
                  查看详情
                </el-button>
              </div>
            </div>
            <div class="example-content">
              <h3>{{ example.title }}</h3>
              <div class="example-meta">
                <el-tag size="small">{{ example.days }}天</el-tag>
                <el-tag size="small" type="info">{{ example.budget }}</el-tag>
                <el-tag size="small" type="success">{{ example.style }}</el-tag>
              </div>
              <p>{{ example.description }}</p>
            </div>
          </div>
        </div>
        
        <div class="examples-footer">
          <el-button type="primary" @click="$router.push('/examples')" size="large">
            查看更多示例
            <el-icon><ArrowRight /></el-icon>
          </el-button>
        </div>
      </div>
    </section>

    <!-- 统计数据 -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item" v-for="stat in stats" :key="stat.label">
            <div class="stat-number">{{ stat.value }}</div>
            <div class="stat-label">{{ stat.label }}</div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA区域 -->
    <section class="cta-section">
      <div class="container">
        <h2>开始您的智能旅行规划</h2>
        <p>只需几分钟，AI就能为您生成专业的旅游攻略</p>
        <div class="cta-buttons">
          <el-button type="primary" size="large" @click="$router.push('/generate')">
            <el-icon><Magic /></el-icon>
            立即开始
          </el-button>
          <el-button size="large" @click="$router.push('/examples')">
            <el-icon><Star /></el-icon>
            查看示例
          </el-button>
        </div>
      </div>
    </section>
  </app-layout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useItineraryStore } from '@/stores/itinerary'
import AppLayout from '@/components/layout/AppLayout.vue'
import {
  Location,
  Magic,
  Map,
  Compass,
  Camera,
  ArrowRight,
  Star,
  Setting,
  DataBoard,
  Download
} from '@element-plus/icons-vue'
import type { FormInstance, FormRules } from 'element-plus'

const router = useRouter()
const itineraryStore = useItineraryStore()

// 快速生成表单
const quickFormRef = ref<FormInstance>()
const quickForm = ref({
  destination: '',
  days: 7
})

const quickFormRules: FormRules = {
  destination: [
    { required: true, message: '请输入目的地', trigger: 'blur' },
    { min: 2, max: 50, message: '目的地长度应在 2 到 50 个字符', trigger: 'blur' }
  ],
  days: [
    { required: true, message: '请选择旅行天数', trigger: 'change' }
  ]
}

const isGenerating = ref(false)

// 平台特色
const features = [
  {
    icon: 'Magic',
    title: 'AI智能生成',
    description: '基于先进的大语言模型，智能分析您的需求，生成个性化旅游攻略',
    color: '#409EFF'
  },
  {
    icon: 'Map',
    title: '实时地理信息',
    description: '集成百度地图API，提供准确的地理位置、距离计算和路线规划',
    color: '#67C23A'
  },
  {
    icon: 'Setting',
    title: '多模型支持',
            description: '支持Ollama、DeepSeek、阿里云百炼等多种AI模型，确保生成质量',
    color: '#E6A23C'
  },
  {
    icon: 'Download',
    title: '多格式导出',
    description: '支持Markdown、HTML、PDF多种格式导出，满足不同使用场景',
    color: '#F56C6C'
  }
]

// 使用流程
const processSteps = [
  {
    title: '输入信息',
    description: '输入目的地、旅行天数、预算等基本信息'
  },
  {
    title: 'AI分析',
    description: '智能分析您的需求，匹配最佳的旅行方案'
  },
  {
    title: '生成攻略',
    description: '自动生成详细的旅游攻略，包含景点、美食、交通等'
  },
  {
    title: '导出使用',
    description: '支持多种格式导出，随时查看和分享您的攻略'
  }
]

// 示例数据
const examples = ref([
  {
    id: 1,
    title: '新疆伊犁深度游',
    days: 11,
    budget: '中等预算',
    style: '自然风光',
    description: '探索新疆伊犁的绝美风光，体验草原文化与自然奇观',
    image: '/images/examples/xinjiang.jpg'
  },
  {
    id: 2,
    title: '云南大理丽江游',
    days: 7,
    budget: '经济实惠',
    style: '文化体验',
    description: '漫步古城小巷，感受云南的民族风情和历史文化',
    image: '/images/examples/yunnan.jpg'
  },
  {
    id: 3,
    title: '四川九寨沟游',
    days: 5,
    budget: '高端奢华',
    style: '自然风光',
    description: '欣赏九寨沟的童话世界，体验高品质的旅行服务',
    image: '/images/examples/jiuzhaigou.jpg'
  }
])

// 统计数据
const stats = ref([
  { value: '1000+', label: '生成攻略数量' },
  { value: '500+', label: '注册用户' },
  { value: '100+', label: '覆盖目的地' },
  { value: '98%', label: '用户满意度' }
])

// 快速生成攻略
const handleQuickGenerate = async () => {
  if (!quickFormRef.value) return
  
  try {
    await quickFormRef.value.validate()
    
    // 跳转到生成页面并传递参数
    router.push({
      name: 'Generate',
      query: {
        destination: quickForm.value.destination,
        days: quickForm.value.days.toString()
      }
    })
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 查看示例
const viewExample = (example: any) => {
  // 这里可以跳转到示例详情页或者打开对话框
  router.push(`/examples?highlight=${example.id}`)
}

// 加载统计数据
onMounted(async () => {
  // 这里可以从API加载真实的统计数据
  // const statsData = await api.stats.getSystemStatus()
})
</script>

<style lang="scss" scoped>
.hero-section {
  position: relative;
  min-height: 80vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  overflow: hidden;

  .hero-content {
    text-align: center;
    max-width: 800px;
    padding: 0 20px;
    z-index: 2;
  }

  .hero-title {
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: 24px;
    line-height: 1.2;

    .gradient-text {
      background: linear-gradient(45deg, #FFD700, #FFA500);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
    }

    @media (max-width: 768px) {
      font-size: 2.5rem;
    }
  }

  .hero-subtitle {
    font-size: 1.25rem;
    margin-bottom: 40px;
    opacity: 0.9;
    line-height: 1.6;
  }

  .quick-form {
    margin-bottom: 40px;

    .hero-form {
      display: flex;
      justify-content: center;
      flex-wrap: wrap;
      gap: 16px;

      .generate-button {
        height: 48px;
        padding: 0 32px;
        font-size: 16px;
        font-weight: 600;
      }
    }
  }

  .feature-tags {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 12px;
  }

  .hero-decoration {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;

    .floating-card {
      position: absolute;
      width: 80px;
      height: 80px;
      background: rgba(255, 255, 255, 0.1);
      border-radius: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      backdrop-filter: blur(10px);
      animation: float 6s ease-in-out infinite;

      &.card-1 {
        top: 20%;
        left: 10%;
        animation-delay: 0s;
      }

      &.card-2 {
        top: 60%;
        right: 15%;
        animation-delay: 2s;
      }

      &.card-3 {
        bottom: 30%;
        left: 20%;
        animation-delay: 4s;
      }
    }
  }
}

@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.section-title {
  text-align: center;
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--el-text-color-primary);
  margin-bottom: 48px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.features-section {
  padding: 80px 0;
  background: white;

  .features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 32px;
  }

  .feature-card {
    text-align: center;
    padding: 32px 24px;
    border-radius: 16px;
    background: white;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease, box-shadow 0.3s ease;

    &:hover {
      transform: translateY(-8px);
      box-shadow: 0 8px 40px rgba(0, 0, 0, 0.12);
    }

    .feature-icon {
      margin-bottom: 24px;
    }

    h3 {
      font-size: 1.5rem;
      font-weight: 600;
      color: var(--el-text-color-primary);
      margin-bottom: 16px;
    }

    p {
      color: var(--el-text-color-regular);
      line-height: 1.6;
    }
  }
}

.process-section {
  padding: 80px 0;
  background: #f8f9fa;

  .process-steps {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 32px;
  }

  .step {
    display: flex;
    align-items: center;
    gap: 24px;
    max-width: 250px;

    .step-number {
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #409EFF;
      color: white;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      font-weight: 700;
      flex-shrink: 0;
    }

    .step-content {
      h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin-bottom: 8px;
      }

      p {
        color: var(--el-text-color-regular);
        line-height: 1.5;
      }
    }

    .step-arrow {
      color: #409EFF;
      font-size: 24px;
    }

    @media (max-width: 768px) {
      flex-direction: column;
      text-align: center;
      
      .step-arrow {
        transform: rotate(90deg);
      }
    }
  }
}

.examples-section {
  padding: 80px 0;
  background: white;

  .examples-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 32px;
    margin-bottom: 48px;
  }

  .example-card {
    border-radius: 16px;
    overflow: hidden;
    background: white;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    transition: transform 0.3s ease;

    &:hover {
      transform: translateY(-4px);
    }

    .example-image {
      position: relative;
      height: 200px;
      overflow: hidden;

      img {
        width: 100%;
        height: 100%;
        object-fit: cover;
      }

      .example-overlay {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        opacity: 0;
        transition: opacity 0.3s ease;
      }

      &:hover .example-overlay {
        opacity: 1;
      }
    }

    .example-content {
      padding: 24px;

      h3 {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--el-text-color-primary);
        margin-bottom: 12px;
      }

      .example-meta {
        display: flex;
        gap: 8px;
        margin-bottom: 16px;
        flex-wrap: wrap;
      }

      p {
        color: var(--el-text-color-regular);
        line-height: 1.5;
      }
    }
  }

  .examples-footer {
    text-align: center;
  }
}

.stats-section {
  padding: 60px 0;
  background: #409EFF;
  color: white;

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 32px;
  }

  .stat-item {
    text-align: center;

    .stat-number {
      font-size: 3rem;
      font-weight: 700;
      margin-bottom: 8px;
    }

    .stat-label {
      font-size: 1.125rem;
      opacity: 0.9;
    }
  }
}

.cta-section {
  padding: 80px 0;
  background: #f8f9fa;
  text-align: center;

  h2 {
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--el-text-color-primary);
    margin-bottom: 16px;
  }

  p {
    font-size: 1.25rem;
    color: var(--el-text-color-regular);
    margin-bottom: 32px;
  }

  .cta-buttons {
    display: flex;
    justify-content: center;
    gap: 16px;
    flex-wrap: wrap;
  }
}
</style> 