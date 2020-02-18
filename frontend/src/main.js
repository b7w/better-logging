import Vue from "vue";
import App from "./App.vue";
import VueRouter from "vue-router";
import Home from "./components/Home";
import Vuetify from "vuetify/lib";

Vue.config.productionTip = false;

Vue.use(VueRouter);
Vue.use(Vuetify);

let store = {
    eventBus: new Vue(),
    events: [],
    updateEvents(data) {
        this.eventBus.$emit('update_events', data);
    },
    listenUpdateEvents(callback) {
        return this.eventBus.$on('update_events', callback);
    }
};
Vue.prototype.store = store;


const routes = [
    {
        path: "/",
        name: "home",
        component: Home
    },
    {
        path: "/about",
        name: "about",
        component: () => import("./components/About.vue")
    }
];

const router = new VueRouter({
    routes
});

const vuetify = new Vuetify({});

new Vue({
    router: router,
    vuetify: vuetify,
    render: h => h(App)
}).$mount("#app");
