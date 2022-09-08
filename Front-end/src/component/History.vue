<template>
    <div>
        <div class="table-area">
            <a-table :columns="columns" :data="data" :pagination="pagination"/>
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            pagination: { pageSize: 5 },
            data: []
        }
    },
    mounted() {
        this.$http.post('/summary/show_all_files').then(res => {
            if (res.data.code !== 200) {
                this.$message.error(res.message)
            }
            res.data.data.forEach(item => {
                let j = {
                    fileName: item,
                }
                this.data.push(j)
            })
        })
    },
    setup() {
        const columns = [
            {
                title: '文件名',
                dataIndex: 'fileName',
            }
        ]
        return {
            columns
        }
    }
}
</script>

<style scoped>
.table-area {
    margin-top: 10px;
}
</style>