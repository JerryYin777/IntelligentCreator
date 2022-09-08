import axios from 'axios'


const http = axios.create({
    baseURL: "http://localhost:8000",
    timeout: 1000 * 180,
})

http.interceptors.request.use(config => {
    config.headers['Content-Type'] = 'multipart/form-data'
    return config
}),error => {
    return Promise.reject(error)
}

export default http