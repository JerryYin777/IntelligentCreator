<template>
  <a-layout class="h-screen">
    <a-layout-header class="h-14 shadow-lg">
      <Header></Header>
    </a-layout-header>
    <a-layout-content>
      <div class="p-4 bg-gray-50 min-h-screen">
        <div class="my-container max-w-screen-xl mx-auto bg-white p-8 rounded-lg shadow-xl">
          <a-tabs default-active-key="1" lazy-load @change="tableChange">
            <a-tab-pane v-for="item of data" :key="item.key" :title="item.title">
              <div v-if="item.key == 1"><Text :key="text"></Text></div>
              <div v-if="item.key == 2">
                <File :key="file"></File>
              </div>
              <div v-if="item.key == 3">
                <History :key="history"></History>
              </div>
            </a-tab-pane>
          </a-tabs>
        </div>
      </div>
    </a-layout-content>
  </a-layout>
</template>


<script>
import { ref } from 'vue'
import Header from '../component/Header.vue'
import Text from '../component/Text.vue'
import File from '../component/File.vue'
import History from '../component/History.vue'
export default {
  data() {
    return {
      text: '',
      file: '',
      history: '',
    }
  },
  components: {
    Header,
    Text,
    File,
    History
  },
  setup() {
    const data = ref([
      {
        key: '1',
        title: '文本检测'
      },
      {
        key: '2',
        title: '文件检测'
      },
      {
        key: '3',
        title: '检测历史'
      }
    ])
    return {
      data
    }
  },
  methods: {
    tableChange(key) {
      switch (key) {
        case '1':
          this.file = new Date().getTime()
          this.history = this.file
          break;
        case '2':
          this.text = new Date().getTime()
          this.history = this.text
          break;
        case '3':
          this.text = new Date().getTime()
          this.file = this.text
          break;
      }
    }
  }
}
</script>

<style scoped>
.my-container {
  min-height: 800px;
}
</style>