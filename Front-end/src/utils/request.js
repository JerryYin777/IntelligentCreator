import axios from "axios"

const baseUrl = "http://localhost:8080"

const requst = axios.create({
    baseURL: baseUrl,
})

export default requst