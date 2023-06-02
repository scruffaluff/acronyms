import App from "@/App.vue";
import "@/styles.scss";
import { MotionPlugin } from "@vueuse/motion";
import { createPinia } from "pinia";
import { createApp } from "vue";

const app = createApp(App);
app.use(createPinia());
app.use(MotionPlugin);
app.mount("#app");
