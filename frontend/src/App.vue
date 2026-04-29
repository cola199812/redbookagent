<template>
  <div id="app">
    <el-container>
      <el-header>
        <h1>小红书智能创作Agent</h1>
      </el-header>
      <el-container>
        <el-aside width="200px">
          <el-menu :default-active="$route.path" router>
            <el-menu-item index="/creator">
              <el-icon><Edit /></el-icon>
              <span>文案生成</span>
            </el-menu-item>
            <el-menu-item index="/knowledge">
              <el-icon><Collection /></el-icon>
              <span>知识库</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-main>
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { Edit, Collection } from '@element-plus/icons-vue'
</script>

<style>
#app {
  height: 100vh;
}
.el-header {
  background: #409eff;
  color: white;
  display: flex;
  align-items: center;
}
.el-aside {
  background: #f5f5f5;
}
.el-main {
  padding: 20px;
}
</style>
