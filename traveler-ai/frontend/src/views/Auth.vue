<template>
  <div class="auth-page">
    <div class="auth-container">
      <div class="auth-card">
        <div class="auth-header">
          <router-link to="/" class="logo">
            <el-icon size="32" color="#409EFF">
              <Location />
            </el-icon>
            <span>TravelerAI</span>
          </router-link>
          <p class="auth-subtitle">智能旅游攻略生成平台</p>
        </div>

        <div class="auth-content">
          <el-tabs v-model="activeTab" class="auth-tabs">
            <el-tab-pane label="登录" name="login">
              <login-form @success="handleLoginSuccess" />
            </el-tab-pane>
            <el-tab-pane label="注册" name="register">
              <register-form @success="handleRegisterSuccess" />
            </el-tab-pane>
          </el-tabs>
        </div>

        <div class="auth-footer">
          <p>© 2024 TravelerAI. All rights reserved.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Location } from '@element-plus/icons-vue'
import LoginForm from '@/components/auth/LoginForm.vue'
import RegisterForm from '@/components/auth/RegisterForm.vue'

const route = useRoute()
const router = useRouter()

const activeTab = ref('login')

const handleLoginSuccess = () => {
  const redirect = (route.query.redirect as string) || '/'
  router.push(redirect)
}

const handleRegisterSuccess = () => {
  activeTab.value = 'login'
}

onMounted(() => {
  // 根据路由设置默认tab
  if (route.name === 'Register') {
    activeTab.value = 'register'
  }
})
</script>

<style lang="scss" scoped>
.auth-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.auth-container {
  width: 100%;
  max-width: 400px;
}

.auth-card {
  background: white;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.auth-header {
  text-align: center;
  padding: 40px 40px 20px;
  background: var(--el-fill-color-extra-light);

  .logo {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    text-decoration: none;
    color: var(--el-text-color-primary);
    font-size: 24px;
    font-weight: 600;
    margin-bottom: 8px;
  }

  .auth-subtitle {
    color: var(--el-text-color-regular);
    margin: 0;
  }
}

.auth-content {
  padding: 20px 40px;

  .auth-tabs {
    :deep(.el-tabs__header) {
      margin-bottom: 24px;
    }

    :deep(.el-tabs__nav) {
      width: 100%;
      display: flex;
    }

    :deep(.el-tabs__item) {
      flex: 1;
      text-align: center;
    }
  }
}

.auth-footer {
  text-align: center;
  padding: 20px;
  background: var(--el-fill-color-extra-light);
  border-top: 1px solid var(--el-border-color-lighter);

  p {
    margin: 0;
    font-size: 14px;
    color: var(--el-text-color-secondary);
  }
}

@media (max-width: 480px) {
  .auth-header,
  .auth-content {
    padding-left: 20px;
    padding-right: 20px;
  }
}
</style> 