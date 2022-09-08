<template>
    <div>
        <a-textarea v-model="textData" placeholder="请在此输入文章..." allow-clear :auto-size="{
            minRows: 8,
            maxRows: 8
        }" />
        <div class="update-button">
            <a-button type="dashed" @click="start">开始检测</a-button>
        </div>
        <div class="divider mx-auto">
            <a-divider orientation="center">检测结果</a-divider>
        </div>
        <div>
            <h3>标题</h3>
            <div class="text-area">
                <div class="text">
                    {{ data.title }}
                </div>
            </div>
            <h3>摘要</h3>
            <div class="text-area summary">
                <div class="text">
                    {{ data.summary }}
                </div>
            </div>
            <h3 class="keyword">关键字</h3>
            <a-space wrap>
                <a-tag v-for="(item, index) of resultTags" :key="index" :color="item.color" size="large">{{ item.data }}
                </a-tag>
            </a-space>
            <div class="time-zone">
                <a-statistic title="所用时间" :value="data.time" :precision="3" :value-style="{ color: '#0fbf60' }">
                    <template #suffix> 秒</template>
                </a-statistic>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            textData: '',
            resultTags: [],
            data: {},
            colors: [
                'red',
                'orangered',
                'orange',
                'gold',
                'lime',
                'green',
                'cyan',
                'blue',
                'arcoblue',
                'purple',
                'pinkpurple',
                'magenta',
                'gray'
            ]
        }
    },
    methods: {
        start() {
            let formData = new FormData()
            formData.append('news_text', this.textData)
            this.initData()
            this.$http.post('/summary/signal_generate', formData).then(res => {
                if (res.status == 200) {
                    res.data.keyword.forEach(item => {
                        const tag = {
                            color: this.colors[Math.floor(Math.random() * 13)],
                            data: item
                        }
                        this.resultTags.unshift(tag)
                    })
                    const result = {
                        ...res.data,
                        time: parseFloat(res.data.time)
                    }
                    this.data = result
                } else {
                    this.$message.error(res.message)
                }
            }).catch(err => {
                this.$notification.error('服务器罢工了呢...')
                console.log(err.message)
            })
        },
        initData() {
            this.data = {},
                this.resultTags = []
        }
    }
}

</script>

<style scoped>
.divider {
    width: 75%;
}

.update-button {
    margin-top: 12px;
    float: right;
}

h3 {
    font-weight: 500;
    margin-top: 10px;
    margin-bottom: 10px;
    margin-left: 15px;
}

.keyword {
    margin-left: 12px;
}

.time-zone {
    float: right;
}

.text-area {
    width: auto;
    height: 50px;
    background-color: var(--color-fill-2)
}
.summary {
    height: 180px;
}
.text {
    margin-left: 10px;
    padding-top: 10px;
    user-select: none;
}
</style>