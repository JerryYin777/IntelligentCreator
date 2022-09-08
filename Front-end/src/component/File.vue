<template>
    <div>
        <div class="table-area">
            <a-upload class="table-body" draggable :custom-request="updateFile" @before-upload="beforeUpload"
                @before-remove="removeFile" :limit="1" />
        </div>
        <div class="update-button">
            <a-button type="dashed" @click="start">开始检测</a-button>
        </div>
        <div class="divider mx-auto">
            <a-divider orientation="center">检测结果</a-divider>
        </div>
        <a-table :columns="columns" :data="data" :pagination="pagination" @page-change="pageChange" />
    </div>
</template>

<script>
export default {
    data() {
        return {
            pagination: {},
            data: [],
            fileRecord: ''
        }
    },
    methods: {
        pageChange(page) {
            let formData = new FormData()
            formData.append('file_name', this.fileRecord)
            formData.append('page', page.toString())
            this.requestData(formData, page)
        },
        start() {
            if (this.fileRecord == '') {
                this.$message.error('请先上传文件')
                return
            }
            let formData = new FormData()
            formData.append('file_name', this.fileRecord)
            formData.append('page', '1')
            this.requestData(formData, 1)
        },
        requestData(formData, page) {
            this.$http.post('/summary/batch_generate', formData).then(res => {
                let result = res.data
                if (result.code !== 200) {
                    this.$notification.error(result.message)
                }
                this.data = []
                this.pagination = {}
                for (let j = 0, len = result.data.length; j < len; j++) {
                    this.data.push(result.data[j])
                }
                this.pagination = {
                    current: page,
                    pageSize: 5,
                    total: result.page_number * 5,
                }
            }).catch(err => {
                this.$notification.error('服务器罢工了呢...')
                console.log(err.message)
            })
        },
        beforeUpload(file) {
            let name = ['json', 'txt']
            let temp = file.name.split('.')
            let fileExt = temp[temp.length - 1]
            let typeIsOk = name.indexOf(fileExt) >= 0
            if (!typeIsOk) {
                this.$message.error('只支持Json和Txt文件!')
            } else {
                return new Promise(resolve => {
                    resolve(true)
                })
            }
        },
        updateFile(option) {
            const { onError, onSuccess, fileItem } = option
            let formData = new FormData();
            formData.append('myfile', fileItem.file)
            this.fileRecord = fileItem.file.name
            this.$http.post('/summary/upload_file', formData).then(res => {
                if (res.data.code !== '200') {
                    return onError(res.data.message)
                }
                onSuccess()
            }).catch(err => {
                this.$notification.error('服务器罢工了呢...')
                console.log(err.message)
            })
        },
        removeFile(file) {
            return new Promise((resolve, reject) => {
                let formData = new FormData()
                formData.append('file_name', file.name)
                this.$http.post('/summary/del_file', formData).then(res => {
                    if (res.data.code !== '200') {
                        return reject(res.data.message)
                    }
                    this.fileRecord = ''
                    this.$notification.success('删除成功')
                    resolve(true)
                }).catch(err => {
                    this.$notification.error('服务器罢工了呢...')
                    reject(err)
                })
            })
        },
    },
    setup() {
        const columns = [
            {
                title: '检测文章',
                dataIndex: 'content',
                ellipsis: true,
                tooltip: { position: 'right' },
                width: 300,
            },
            {
                title: '标题',
                dataIndex: 'title',
                width: 180,
            },
            {
                title: '摘要',
                dataIndex: 'summary',
                width: 300,
            },
            {
                title: '关键字',
                dataIndex: 'keyword',
                width: 180,
            },
            {
                title: '所用时间',
                dataIndex: 'time',
            },
        ]
        return {
            columns
        }
    }
}

</script>

<style scoped>
.table-area {
    height: 200px;
    display: flex;
}

.table-body {
    align-self: center;
}

.divider {
    width: 75%;
}

.update-button {
    margin-top: 12px;
    float: right;
}
</style>